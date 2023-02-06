package handlers

import (
	"net/http"
	"net/url"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/core/xerrors"
	"a.yandex-team.ru/library/go/yandex/tvm"
	"a.yandex-team.ru/passport/infra/daemons/tvmtool/internal/errs"
	"a.yandex-team.ru/passport/infra/daemons/tvmtool/internal/httpclientmock"
)

var ValidRoles = `{"revision":"GYYTKYZRMVSDC","born_date":1633427153,"tvm":{"11":{"/role/factors_by_number/":[{}]}}}`

type testGetRoles struct {
	roles map[string]*tvm.Roles
	err   error
}

func (t *testGetRoles) GetRoles(slug string) (*tvm.Roles, error) {
	return t.roles[slug], t.err
}

func TestGetRolesHandlerV2(t *testing.T) {
	ongoingRoles, err := tvm.NewRoles([]byte(ValidRoles))
	require.NoError(t, err)

	tr := &testGetRoles{
		roles: map[string]*tvm.Roles{"some_slug": ongoingRoles},
	}

	handler := GetRolesHandlerV2(createComplexConfig(), tr)

	httpclientmock.TestCaseErr(t, handler,
		httpclientmock.MakeRequest("", nil),
		&errs.InvalidParam{Message: "missing parameter 'self'"},
	)
	httpclientmock.TestCaseErr(t, handler,
		httpclientmock.MakeRequest("self=kek", nil),
		&errs.InvalidParam{Message: "failed to get roles for self alias 'kek': couldn't find client in config by alias: 'kek'"},
	)
	resp := httpclientmock.TestCase(t, handler,
		httpclientmock.MakeRequest("self=kokoko", nil),
		ValidRoles,
		http.StatusOK)
	require.EqualValues(t, `"GYYTKYZRMVSDC"`, resp.Header.Get("ETag"))

	resp = httpclientmock.TestCase(t, handler,
		httpclientmock.MakeRequest("self=kokoko", map[string]string{"If-None-Match": `"YYY"`}),
		ValidRoles,
		http.StatusOK)
	require.EqualValues(t, `"GYYTKYZRMVSDC"`, resp.Header.Get("ETag"))

	resp = httpclientmock.TestCase(t, handler,
		httpclientmock.MakeRequest("self=kokoko", map[string]string{"If-None-Match": `"GYYTKYZRMVSDC"`}),
		``,
		http.StatusNotModified)
	require.EqualValues(t, ``, resp.Header.Get("ETag"))
}

func TestGetRolesHandlerV2Args(t *testing.T) {
	_, _, err := getRolesHandlerV2Args(&http.Request{
		URL: &url.URL{},
	})
	require.EqualError(t, err, "missing parameter 'self'")

	selfAlias, currentRevision, err := getRolesHandlerV2Args(&http.Request{
		URL: &url.URL{RawQuery: "self=kek"},
	})
	require.NoError(t, err)
	require.EqualValues(t, "kek", selfAlias)
	require.EqualValues(t, "", currentRevision)

	_, _, err = getRolesHandlerV2Args(&http.Request{
		URL:    &url.URL{RawQuery: "self=kek"},
		Header: map[string][]string{"If-None-Match": {`lol`}},
	})
	require.EqualError(t, err, "failed to unquote header If-None-Match body: 'lol'")

	selfAlias, currentRevision, err = getRolesHandlerV2Args(&http.Request{
		URL:    &url.URL{RawQuery: "self=kek"},
		Header: map[string][]string{"If-None-Match": {`"lol"`}},
	})
	require.NoError(t, err)
	require.EqualValues(t, "kek", selfAlias)
	require.EqualValues(t, "lol", currentRevision)
}

func TestGetCurrentRevision(t *testing.T) {
	rev, err := getCurrentRevision(&http.Request{})
	require.NoError(t, err)
	require.EqualValues(t, "", rev)

	_, err = getCurrentRevision(&http.Request{
		Header: map[string][]string{"If-None-Match": {"kek"}},
	})
	require.EqualError(t, err, "failed to unquote header If-None-Match body: 'kek'")

	rev, err = getCurrentRevision(&http.Request{
		Header: map[string][]string{"If-None-Match": {`"kek"`}},
	})
	require.NoError(t, err)
	require.EqualValues(t, "kek", rev)
}

func TestGetRolesForClient(t *testing.T) {
	ongoingRoles, err := tvm.NewRoles([]byte(ValidRoles))
	require.NoError(t, err)

	config := createComplexConfig()
	tr := &testGetRoles{
		roles: map[string]*tvm.Roles{},
		err:   xerrors.New("lol"),
	}

	roles, err := getRolesForClient("kek", config, tr)
	require.EqualError(t, err, "couldn't find client in config by alias: 'kek'")
	require.Nil(t, roles)

	roles, err = getRolesForClient("kekeke", config, tr)
	require.EqualError(t, err, "IDM slug is not configured for self alias 'kekeke'")
	require.Nil(t, roles)

	roles, err = getRolesForClient("kokoko", config, tr)
	require.EqualError(t, err, "failed to get roles for self alias 'kokoko': lol")
	require.Nil(t, roles)

	tr.err = nil
	roles, err = getRolesForClient("kokoko", config, tr)
	require.NoError(t, err)
	require.Nil(t, roles)

	tr.roles["some_slug"] = ongoingRoles
	roles, err = getRolesForClient("kokoko", config, tr)
	require.NoError(t, err)
	require.Equal(t, ongoingRoles, roles)
}
