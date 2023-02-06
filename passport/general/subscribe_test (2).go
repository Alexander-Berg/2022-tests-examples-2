package pushsubscription

import (
	"context"
	"fmt"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/labstack/echo/v4"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/passport/infra/daemons/push_subscription/internal/errs"
	"a.yandex-team.ru/passport/infra/daemons/push_subscription/internal/model"
	"a.yandex-team.ru/passport/infra/daemons/push_subscription/internal/reqs"
)

func TestTranslatePlatform(t *testing.T) {
	type Case struct {
		Name string
		In   string
		Out  string
		Err  string
	}
	cases := []Case{
		{Name: "empty",
			In:  "",
			Err: "got illegal platform: ''",
		},
		{Name: "dummy",
			In:  "kek",
			Err: "got illegal platform: 'kek'",
		},
		{Name: "android",
			In:  "android",
			Out: "gcm",
		},
		{Name: "android with trash",
			In:  "androidkek",
			Out: "gcm",
		},
		{Name: "gcm",
			In:  "gcmkek",
			Out: "gcm",
		},
		{Name: "apple",
			In:  "applekek",
			Out: "apns",
		},
	}

	for _, c := range cases {
		res, err := translatePlatform(c.In)

		if c.Err == "" {
			require.NoError(t, err, c.Name)
			require.EqualValues(t, c.Out, res, c.Name)
		} else {
			require.ErrorContains(t, err, c.Err, c.Name)
		}
	}
}

func TestGetAppName(t *testing.T) {
	type Case struct {
		Name          string
		InAppPlatform string
		InAppID       string
		Out           string
	}
	cases := []Case{
		{Name: "common",
			InAppPlatform: "someplatform",
			InAppID:       "someid",
			Out:           "someid",
		},
		{Name: "common#2",
			InAppPlatform: "someplatform",
			InAppID:       "someid.passport",
			Out:           "someid.passport",
		},
		{Name: "gcm",
			InAppPlatform: "gcm",
			InAppID:       "someid",
			Out:           "someid.passport",
		},
		{Name: "gcm with passport",
			InAppPlatform: "gcm",
			InAppID:       "someid.passport",
			Out:           "someid.passport",
		},
	}

	for _, c := range cases {
		require.EqualValues(t,
			c.Out,
			getAppName(c.InAppPlatform, c.InAppID),
			c.Name,
		)
	}
}

func TestCreateUUID(t *testing.T) {
	require.EqualValues(t,
		"5dc40597089a3a9876ec18edcbdb831f",
		createUUID("some_deviceid", "some_app_id"),
	)
}

type testOAuthProvider struct {
	response *model.AuthResponse
	err      error
}

func (p *testOAuthProvider) CheckOAuth(context.Context, *model.AuthRequest) (*model.AuthResponse, error) {
	return p.response, p.err
}

type testSubscriberProvider struct {
	response  *model.SubscribeResponse
	err       error
	wasCalled bool
}

func (p *testSubscriberProvider) Subscribe(context.Context, *model.SubscribeRequest) (*model.SubscribeResponse, error) {
	p.wasCalled = true
	return p.response, p.err
}

func TestSubscribeImpl(t *testing.T) {
	authProvider := &testOAuthProvider{
		response: &model.AuthResponse{UID: 100500, LoginID: "someloginid"},
	}
	subscribeProvider := &testSubscriberProvider{
		response: &model.SubscribeResponse{},
	}
	passpLogWasHappen := false
	pushLogWasHappen := false

	cleanup := func() {
		authProvider.err = nil
		subscribeProvider.err = nil
		subscribeProvider.wasCalled = false
		passpLogWasHappen = false
		pushLogWasHappen = false
	}
	check := func(req *reqs.SubscribeRequest, headers map[string]string) error {
		return subscribeImpl(
			echo.New().NewContext(makeRequest(headers), httptest.NewRecorder()),
			req,
			authProvider,
			subscribeProvider,
			func(string, string) { passpLogWasHappen = true },
			func(string, string) { pushLogWasHappen = true },
		)
	}

	t.Run("bad platform", func(t *testing.T) {
		cleanup()
		err := check(&reqs.SubscribeRequest{}, nil)
		require.EqualValues(t, err, &errs.InvalidParamError{
			Key:     "push_api",
			Type:    "app_platform_unsupported",
			Message: "got illegal platform: ''",
		})
		require.False(t, subscribeProvider.wasCalled)
		require.False(t, passpLogWasHappen)
		require.False(t, pushLogWasHappen)
	})

	t.Run("no auth", func(t *testing.T) {
		cleanup()
		err := check(&reqs.SubscribeRequest{AppPlatform: "android"}, nil)
		require.EqualValues(t, err, &errs.InvalidParamError{
			Key:     "authorization",
			Type:    "empty",
			Message: "missing header: 'Ya-Consumer-Authorization'",
		})
		require.False(t, subscribeProvider.wasCalled)
		require.False(t, passpLogWasHappen)
		require.False(t, pushLogWasHappen)
	})

	t.Run("illegal auth type", func(t *testing.T) {
		cleanup()
		err := check(&reqs.SubscribeRequest{AppPlatform: "android"}, map[string]string{
			"Ya-Consumer-Authorization": "foo kek",
		})
		require.EqualValues(t, err, &errs.InvalidParamError{
			Key:     "authorization",
			Type:    "invalid",
			Message: "got unsupported auth type: 'foo'",
		})
		require.False(t, subscribeProvider.wasCalled)
		require.False(t, passpLogWasHappen)
		require.False(t, pushLogWasHappen)
	})

	t.Run("invalid auth", func(t *testing.T) {
		cleanup()
		authProvider.err = fmt.Errorf("someerror")
		err := check(&reqs.SubscribeRequest{AppPlatform: "android"}, map[string]string{
			"Ya-Consumer-Authorization": "OAuth kek",
		})
		require.EqualError(t, err, "someerror")
		require.False(t, subscribeProvider.wasCalled)
		require.False(t, passpLogWasHappen)
		require.False(t, pushLogWasHappen)
	})

	t.Run("failed to subscribe", func(t *testing.T) {
		cleanup()
		subscribeProvider.err = fmt.Errorf("someerror")
		err := check(&reqs.SubscribeRequest{
			AppPlatform:                "android",
			IsPushTokenUpgradeRequired: true,
		}, map[string]string{
			"Ya-Consumer-Authorization": "oauth kek",
		})
		require.EqualError(t, err, "someerror")
		require.True(t, subscribeProvider.wasCalled)
		require.False(t, passpLogWasHappen)
		require.False(t, pushLogWasHappen)
	})

	t.Run("usual case", func(t *testing.T) {
		cleanup()
		err := check(&reqs.SubscribeRequest{
			AppPlatform:                "android",
			IsPushTokenUpgradeRequired: true,
		}, map[string]string{
			"Ya-Consumer-Authorization": "oauth kek",
		})
		require.NoError(t, err)
		require.True(t, subscribeProvider.wasCalled)
		require.True(t, passpLogWasHappen)
		require.True(t, pushLogWasHappen)
	})

	t.Run("token was the same: should only write push logs", func(t *testing.T) {
		cleanup()
		err := check(
			&reqs.SubscribeRequest{
				AppPlatform:                "android",
				IsPushTokenUpgradeRequired: false,
			},
			map[string]string{
				"Ya-Consumer-Authorization": "oauth kek",
			},
		)
		require.NoError(t, err)
		require.False(t, subscribeProvider.wasCalled)
		require.False(t, passpLogWasHappen)
		require.True(t, pushLogWasHappen)
	})
}

func makeRequest(headers map[string]string) *http.Request {
	req, err := http.NewRequest("POST", "/", nil)
	if err != nil {
		panic(err)
	}
	for k, v := range headers {
		req.Header.Set(k, v)
	}
	return req
}
