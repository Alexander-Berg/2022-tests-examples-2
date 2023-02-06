package tvmcache

import (
	"io/ioutil"
	"os"
	"testing"
	"time"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/core/xerrors"
	"a.yandex-team.ru/library/go/yandex/tvm"
	"a.yandex-team.ru/passport/infra/daemons/tvmtool/internal/tvmtypes"
)

func TestFetchFromDiskImpl(t *testing.T) {
	cleanup := func() {
		_ = os.Remove("./.tvm-roles.cache.slug3")
		_ = os.Remove("./.tvm-roles.cache.slug4")
	}
	cleanup()
	defer cleanup()

	require.NoError(t, writeCacheFile("./.tvm-roles.cache.slug3", 42, []byte("kokokokokokokokokokoko")))
	require.NoError(t, writeCacheFile("./.tvm-roles.cache.slug4", 42, []byte(ValidRoles)))

	cfg := &tvmtypes.Config{}
	res, err := fetchFromDiskImpl("./", tvmtypes.NewOptimizedConfig(cfg))
	require.NoError(t, err)
	require.EqualValues(t, 0, len(res))

	cfg = &tvmtypes.Config{
		Clients: map[string]tvmtypes.Client{
			"alias#1": {},
			"alias#2": {IdmSlug: "slug2"},
			"alias#3": {IdmSlug: "slug3"},
			"alias#4": {IdmSlug: "slug4"},
		},
	}
	res, err = fetchFromDiskImpl("./", tvmtypes.NewOptimizedConfig(cfg))
	require.Error(t, err)
	require.Contains(t, err.Error(), "failed to read file: open .tvm-roles.cache.slug2")
	require.Contains(t, err.Error(), "fail to parse roles from file: .tvm-roles.cache.slug3")
	require.EqualValues(t, 1, len(res))
	require.Contains(t, res, "slug4")

	cfg = &tvmtypes.Config{
		Clients: map[string]tvmtypes.Client{
			"alias#4": {IdmSlug: "slug4"},
		},
	}
	res, err = fetchFromDiskImpl("./", tvmtypes.NewOptimizedConfig(cfg))
	require.NoError(t, err)
	require.EqualValues(t, 1, len(res))
	require.Contains(t, res, "slug4")
}

func TestIsTimeForAttempt(t *testing.T) {
	now := time.Now()
	cache := NewRolesCache("./")
	clients := []*tvmtypes.Client{}
	require.False(t, cache.IsTimeForAttempt(clients, now))
	clients = []*tvmtypes.Client{
		{},
	}
	require.False(t, cache.IsTimeForAttempt(clients, now))

	clients = []*tvmtypes.Client{
		{},
		{IdmSlug: "kek"},
		{IdmSlug: "lol"},
	}
	require.True(t, cache.IsTimeForAttempt(clients, now))

	cache.bySlug["kek"] = &rolesState{state: cacheState{lastUpdated: time.Unix(100500, 0)}}
	cache.bySlug["lol"] = &rolesState{state: cacheState{lastUpdated: now}}
	require.True(t, cache.IsTimeForAttempt(clients, now))

	clients = []*tvmtypes.Client{
		{IdmSlug: "lol"},
	}
	require.False(t, cache.IsTimeForAttempt(clients, now))
}

func TestGetDiag(t *testing.T) {
	now := time.Now()
	cache := NewRolesCache("./")
	require.EqualValues(t, DiagState{Status: StatusOk}, cache.GetDiag(now))

	cache.bySlug["kek"] = &rolesState{state: cacheState{lastUpdated: time.Unix(100500, 0)}}
	require.EqualValues(t,
		DiagState{Status: StatusWarning, LastUpdate: time.Unix(100500, 0)},
		cache.GetDiag(time.Now()),
	)

	cache.bySlug["lol"] = &rolesState{state: cacheState{lastUpdated: now}}
	require.EqualValues(t,
		DiagState{Status: StatusWarning, LastUpdate: time.Unix(100500, 0)},
		cache.GetDiag(now),
	)

	delete(cache.bySlug, "kek")
	require.EqualValues(t, DiagState{Status: StatusOk}, cache.GetDiag(now))
}

func TestGetRoles(t *testing.T) {
	cache := NewRolesCache("./")
	_, err := cache.GetRoles("kek")
	require.EqualError(t, err, "slug 'kek' was not configured")

	newRoles, err := tvm.NewRoles([]byte(`{"revision":"YYYTKYZRMVSDC","born_date":1633427153}`))
	require.NoError(t, err)
	cache.bySlug["kek"] = &rolesState{roles: newRoles}

	roles, err := cache.GetRoles("kek")
	require.NoError(t, err, "slug 'kek' was not configured")
	require.NotNil(t, roles)
	require.EqualValues(t, "YYYTKYZRMVSDC", roles.GetMeta().Revision)
}

func TestUpdate(t *testing.T) {
	cache := NewRolesCache("./")

	var wasCalled bool
	cache.updateForClient = func(
		gate tiroleGate,
		client *tvmtypes.Client,
		currentRoles *rolesState,
		cacheDirectory string,
		now time.Time,
	) (*rolesState, error) {
		wasCalled = true
		return nil, nil
	}

	err := cache.Update(nil, []*tvmtypes.Client{})
	require.NoError(t, err)
	require.False(t, wasCalled)
	require.EqualValues(t, 0, len(cache.bySlug))

	err = cache.Update(nil, []*tvmtypes.Client{
		{},
	})
	require.NoError(t, err)
	require.False(t, wasCalled)
	require.EqualValues(t, 0, len(cache.bySlug))

	err = cache.Update(nil, []*tvmtypes.Client{
		{IdmSlug: "kek"},
	})
	require.NoError(t, err)
	require.True(t, wasCalled)
	require.EqualValues(t, 0, len(cache.bySlug))

	cache.updateForClient = func(
		gate tiroleGate,
		client *tvmtypes.Client,
		currentRoles *rolesState,
		cacheDirectory string,
		now time.Time,
	) (*rolesState, error) {
		slug1, err := tvm.NewRoles([]byte(`{"revision":"YYYTKYZRMVSDC","born_date":1633427153}`))
		require.NoError(t, err)
		slug2, err := tvm.NewRoles([]byte(`{"revision":"ZYYTKYZRMVSDC","born_date":1633427153}`))
		require.NoError(t, err)

		cases := map[string]struct {
			roles *tvm.Roles
			err   error
		}{
			"slug#1": {roles: slug1},
			"slug#2": {roles: slug2, err: xerrors.New("foo")},
			"slug#3": {err: xerrors.New("bar")},
			"slug#4": {},
		}

		c, found := cases[client.IdmSlug]
		require.True(t, found)

		var res *rolesState
		if c.roles != nil {
			res = &rolesState{roles: c.roles}
		}
		return res, c.err
	}

	err = cache.Update(nil, []*tvmtypes.Client{
		{IdmSlug: "slug#1"},
		{IdmSlug: "slug#2"},
		{IdmSlug: "slug#3"},
		{IdmSlug: "slug#4"},
	})
	require.EqualError(t, err, "foo. bar")
	require.EqualValues(t, 2, len(cache.bySlug))
	require.Contains(t, cache.bySlug, "slug#1")
	require.Contains(t, cache.bySlug, "slug#2")

	err = cache.Update(nil, []*tvmtypes.Client{
		{IdmSlug: "slug#1"},
		{IdmSlug: "slug#4"},
	})
	require.NoError(t, err)
	require.EqualValues(t, 1, len(cache.bySlug))
	require.Contains(t, cache.bySlug, "slug#1")
}

func TestUpdateForClient(t *testing.T) {
	currentRoles, err := tvm.NewRoles([]byte(ValidRoles))
	require.NoError(t, err)
	ongoingRoles, err := tvm.NewRoles([]byte(`{"revision":"YYYTKYZRMVSDC","born_date":1633427153}`))
	require.NoError(t, err)
	now := time.Now()

	gate := &tiroleGateImpl{
		tvmapiClient: &testTvmAPIClient{
			t:           t,
			expectedSrc: 100500,
			expectedDst: 42,
			result:      "some_ticket",
			err:         xerrors.New("foo"),
		},
		tiroleClient: &testTiroleClient{
			t:                       t,
			expectedSlug:            "some_slug",
			expectedServiceTicket:   "some_ticket",
			expectedCurrentRevision: "GYYTKYZRMVSDC",
			err:                     xerrors.New("kek"),
		},
		tiroleTvmID: 42,
	}

	_, err = updateForClient(
		gate,
		&tvmtypes.Client{SelfTvmID: 100500, IdmSlug: "some_slug"},
		&rolesState{},
		"./",
		now,
	)
	require.EqualError(t, err, "failed to update roles for slug 'some_slug': foo")

	gate.tvmapiClient = &testTvmAPIClient{
		t:           t,
		expectedSrc: 100500,
		expectedDst: 42,
		result:      "some_ticket",
	}
	_, err = updateForClient(
		gate,
		&tvmtypes.Client{SelfTvmID: 100500, IdmSlug: "some_slug"},
		&rolesState{state: cacheState{lastUpdated: now}},
		"./",
		now,
	)
	require.EqualError(t, err, "failed to update roles for slug 'some_slug': internal error: no cache and no errors from tirole")

	gate.tiroleClient = &testTiroleClient{
		t:                       t,
		expectedSlug:            "some_slug",
		expectedServiceTicket:   "some_ticket",
		expectedCurrentRevision: "GYYTKYZRMVSDC",
		result:                  ongoingRoles,
	}
	newRoles, err := updateForClient(
		gate,
		&tvmtypes.Client{SelfTvmID: 100500, IdmSlug: "some_slug"},
		&rolesState{roles: currentRoles},
		"/",
		now,
	)
	require.Error(t, err)
	require.Contains(t, err.Error(), "failed to write disk cache:")
	require.NotNil(t, newRoles)

	newRoles, err = updateForClient(
		gate,
		&tvmtypes.Client{SelfTvmID: 100500, IdmSlug: "some_slug"},
		&rolesState{roles: currentRoles},
		"./",
		now,
	)
	require.NoError(t, err)
	require.EqualValues(t, "YYYTKYZRMVSDC", newRoles.roles.GetMeta().Revision)
	blob, err := ioutil.ReadFile("./.tvm-roles.cache.some_slug")
	require.NoError(t, err)
	require.Contains(t, string(blob), "YYYTKYZRMVSDC")
}

func TestGetActualRolesForClient(t *testing.T) {
	now := time.Now()
	currentRoles, err := tvm.NewRoles([]byte(`{"revision":"GYYTKYZRMVSDC","born_date":1633427153,"tvm":{"11":{"/role/factors_by_number/":[{}]}}}`))
	require.NoError(t, err)
	ongoingRoles, err := tvm.NewRoles([]byte(`{"revision":"YYYTKYZRMVSDC","born_date":1633427153}`))
	require.NoError(t, err)

	roleReader := func(currentRevision string) (*tvm.Roles, error) {
		return ongoingRoles, xerrors.New("kek")
	}

	newRoles, err := getActualRolesForClient(
		roleReader,
		&rolesState{
			roles: currentRoles,
			state: cacheState{lastUpdated: now.Add(time.Duration(-1) * time.Second)},
		},
		now,
	)
	require.NoError(t, err)
	require.EqualValues(t, "GYYTKYZRMVSDC", newRoles.roles.GetMeta().Revision)
	require.EqualValues(t, now.Add(time.Duration(-1)*time.Second), newRoles.state.lastUpdated)

	newRoles, err = getActualRolesForClient(
		roleReader,
		&rolesState{
			roles: currentRoles,
			state: cacheState{lastUpdated: now.Add(time.Duration(-1) * time.Hour)},
		},
		now,
	)
	require.EqualError(t, err, "kek")
	require.EqualValues(t, "GYYTKYZRMVSDC", newRoles.roles.GetMeta().Revision)
	require.EqualValues(t, now.Add(time.Duration(-1)*time.Hour), newRoles.state.lastUpdated)

	roleReader = func(currentRevision string) (*tvm.Roles, error) { return ongoingRoles, nil }
	newRoles, err = getActualRolesForClient(
		roleReader,
		&rolesState{
			roles: currentRoles,
			state: cacheState{lastUpdated: now.Add(time.Duration(-1) * time.Hour)},
		},
		now,
	)
	require.NoError(t, err)
	require.EqualValues(t, "YYYTKYZRMVSDC", newRoles.roles.GetMeta().Revision)
	require.EqualValues(t, now, newRoles.state.lastUpdated)

	newRoles, err = getActualRolesForClient(
		func(currentRevision string) (*tvm.Roles, error) { return nil, nil },
		&rolesState{
			roles: currentRoles,
			state: cacheState{lastUpdated: now.Add(time.Duration(-1) * time.Hour)},
		},
		now,
	)
	require.NoError(t, err)
	require.EqualValues(t, "GYYTKYZRMVSDC", newRoles.roles.GetMeta().Revision)
	require.EqualValues(t, now, newRoles.state.lastUpdated)
}

func TestBuildRolesFileName(t *testing.T) {
	require.EqualValues(t,
		".tvm-roles.cache.kek",
		buildRolesFileName("kek"),
	)
}

var ValidRoles = `{"revision":"GYYTKYZRMVSDC","born_date":1633427153,"tvm":{"11":{"/role/factors_by_number/":[{}]}}}`

type testTvmAPIClient struct {
	t *testing.T

	expectedSrc tvm.ClientID
	expectedDst tvm.ClientID

	result string
	er     string
	err    error
}

func (c *testTvmAPIClient) GetTicket(src tvm.ClientID, dst tvm.ClientID) (tvmtypes.Ticket, string, error) {
	require.EqualValues(c.t, c.expectedSrc, src)
	require.EqualValues(c.t, c.expectedDst, dst)
	return tvmtypes.Ticket(c.result), c.er, c.err
}

type testTiroleClient struct {
	t *testing.T

	expectedSlug            string
	expectedServiceTicket   string
	expectedCurrentRevision string

	result *tvm.Roles
	err    error
}

func (c *testTiroleClient) GetRoles(slug, serviceTicket, currentRevision string) (*tvm.Roles, error) {
	require.EqualValues(c.t, c.expectedSlug, slug)
	require.EqualValues(c.t, c.expectedServiceTicket, serviceTicket)
	require.EqualValues(c.t, c.expectedCurrentRevision, currentRevision)
	return c.result, c.err
}

func TestGate_GetServiceTicket(t *testing.T) {
	gate := tiroleGateImpl{
		tvmapiClient: &testTvmAPIClient{
			t:           t,
			expectedSrc: 100500,
			expectedDst: 42,
			result:      "lol",
			er:          "foo",
			err:         xerrors.New("kek"),
		},
		tiroleTvmID: 42,
	}

	st, err := gate.GetServiceTicket(100500)
	require.EqualError(t, err, "foo")
	require.EqualValues(t, st, "lol")

	gate.tvmapiClient = &testTvmAPIClient{
		t:           t,
		expectedSrc: 100500,
		expectedDst: 42,
		result:      "lol",
		err:         xerrors.New("kek"),
	}

	st, err = gate.GetServiceTicket(100500)
	require.EqualError(t, err, "kek")
	require.EqualValues(t, st, "lol")
}

func TestGate_CreateRolesReader(t *testing.T) {
	expectedRoles, err := tvm.NewRoles([]byte(ValidRoles))
	require.NoError(t, err)

	gate := tiroleGateImpl{
		tiroleClient: &testTiroleClient{
			t:                       t,
			expectedSlug:            "some_slug",
			expectedServiceTicket:   "some_ticket",
			expectedCurrentRevision: "some_revision",
			result:                  expectedRoles,
			err:                     xerrors.New("kek"),
		},
	}

	f := gate.CreateRolesReader("some_slug", "some_ticket")
	actualRoles, err := f("some_revision")
	require.EqualError(t, err, "kek")
	require.Equal(t, expectedRoles, actualRoles)
}
