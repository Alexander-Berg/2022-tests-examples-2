package xiva

import (
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/passport/infra/daemons/push_subscription/internal/model"
)

func TestCreateSubscribeQueryParams(t *testing.T) {
	type Case struct {
		Name string
		In   *model.SubscribeRequest
		Out  map[string]string
	}
	cases := []Case{
		{Name: "empty request",
			In: &model.SubscribeRequest{},
			Out: map[string]string{
				"app_name": "",
				"device":   "",
				"platform": "",
				"service":  "some_service",
				"user":     "",
				"uuid":     "",
			},
		},
		{Name: "common request",
			In: &model.SubscribeRequest{
				AppName:  "someapp",
				DeviceID: "someadevice",
				Platform: "someplatform",
				User:     "someuser",
				UUID:     "someuuid",
			},
			Out: map[string]string{
				"app_name": "someapp",
				"device":   "someadevice",
				"platform": "someplatform",
				"service":  "some_service",
				"user":     "someuser",
				"uuid":     "someuuid",
			},
		},
		{Name: "request with client",
			In: &model.SubscribeRequest{
				AppName:  "someapp",
				Client:   "someclient",
				DeviceID: "someadevice",
				Platform: "someplatform",
				User:     "someuser",
				UUID:     "someuuid",
			},
			Out: map[string]string{
				"app_name": "someapp",
				"client":   "someclient",
				"device":   "someadevice",
				"platform": "someplatform",
				"service":  "some_service",
				"user":     "someuser",
				"uuid":     "someuuid",
			},
		},
	}

	for _, c := range cases {
		require.EqualValues(t,
			c.Out,
			createSubscribeQueryParams(c.In, "some_service"),
			c.Name,
		)
	}
}

func TestCreateSubscribeFormData(t *testing.T) {
	type Case struct {
		Name string
		In   *model.SubscribeRequest
		Out  map[string]string
		Err  string
	}
	cases := []Case{
		{Name: "empty request",
			In: &model.SubscribeRequest{},
			Out: map[string]string{
				"extra":      "{}",
				"push_token": "",
			},
		},
		{Name: "common request",
			In: &model.SubscribeRequest{
				Extra: model.SubscribeExtra{
					AmVersion:  "someversion",
					LoginID:    "someloginid",
					AppVersion: "someotherversion",
				},
				PushToken: "sometoken",
			},
			Out: map[string]string{
				"extra":      `{"0":"someversion","1":"someloginid","2":"someotherversion"}`,
				"push_token": "sometoken",
			},
		},
		{Name: "request with filter",
			In: &model.SubscribeRequest{
				PushToken: "sometoken",
				Filter:    "somefilter",
			},
			Out: map[string]string{
				"extra":      "{}",
				"filter":     "somefilter",
				"push_token": "sometoken",
			},
		},
	}

	for _, c := range cases {
		res, err := createSubscribeFormData(c.In)
		require.NoError(t, err, c.Name)
		require.EqualValues(t, c.Out, res, c.Name)
	}
}
