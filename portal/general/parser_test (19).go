package requests

import (
	"net/http"
	"net/url"
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	protoanswers "a.yandex-team.ru/apphost/lib/proto_answers"
	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/libs/utils/common"
	"a.yandex-team.ru/portal/avocado/libs/utils/errors/v3"
)

func Test_parser_isInternal(t *testing.T) {
	type fields struct {
		env     common.Environment
		headers http.Header
		cgi     url.Values
	}
	tests := []struct {
		name   string
		fields fields
		want   bool
	}{
		{
			name: "If env is testing",
			fields: fields{
				env: common.Testing,
			},
			want: true,
		},
		{
			name: "If env is dev",
			fields: fields{
				env: common.Development,
			},
			want: true,
		},
		{
			name: "Env is prod and no http headers",
			fields: fields{
				env:     common.Production,
				headers: map[string][]string{},
			},
			want: false,
		},
		{
			name: "Env is prod and got expected header",
			fields: fields{
				env: common.Production,
				headers: map[string][]string{
					"X-Yandex-Internal-Request": {"1"},
				},
			},
			want: true,
		},
		{
			name: "Env is prod and got expected header but value is zero",
			fields: fields{
				env: common.Production,
				headers: map[string][]string{
					"X-Yandex-Internal-Request": {"0"},
				},
			},
			want: false,
		},
		{
			name: "Env is prod and got expected header, yandex=0",
			fields: fields{
				env: common.Production,
				headers: map[string][]string{
					"X-Yandex-Internal-Request": {"1"},
				},
				cgi: url.Values{"yandex": {"0"}},
			},
			want: false,
		},
		{
			name: "Env is prod and got expected header, invalid yandex cgi",
			fields: fields{
				env: common.Production,
				headers: map[string][]string{
					"X-Yandex-Internal-Request": {"1"},
				},
				cgi: url.Values{"yandex": {"111"}},
			},
			want: true,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			originRequestKeeper := NewMockoriginRequestKeeper(gomock.NewController(t))
			originRequestKeeper.EXPECT().GetOriginRequest().Return(
				&models.OriginRequest{
					Headers: tt.fields.headers,
				},
				nil,
			).MaxTimes(1)

			k := &parser{
				env:                 tt.fields.env,
				originRequestKeeper: originRequestKeeper,
			}

			got, err := k.isInternal(tt.fields.cgi)
			require.NoError(t, err)
			require.Equal(t, tt.want, got)
		})
	}
}

func Test_parser_isPumpkin(t *testing.T) {
	type fields struct {
		headers http.Header
	}
	tests := []struct {
		name   string
		fields fields
		want   bool
	}{
		{
			name: "header is 1",
			fields: fields{
				headers: map[string][]string{
					"X-Yandex-Morda-Pumpkin": {"1"},
				},
			},
			want: true,
		},
		{
			name: "header is 0",
			fields: fields{
				headers: map[string][]string{
					"X-Yandex-Morda-Pumpkin": {"0"},
				},
			},
			want: false,
		},
		{
			name: "header is not set",
			fields: fields{
				headers: map[string][]string{},
			},
			want: false,
		},
		{
			name: "header is another value",
			fields: fields{
				headers: map[string][]string{
					"X-Yandex-Morda-Pumpkin": {"yes"},
				},
			},
			want: false,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			originRequestKeeper := NewMockoriginRequestKeeper(gomock.NewController(t))
			originRequestKeeper.EXPECT().GetOriginRequest().Return(
				&models.OriginRequest{
					Headers: tt.fields.headers,
				},
				nil,
			).MaxTimes(1)
			k := &parser{
				originRequestKeeper: originRequestKeeper,
			}

			got, err := k.isPumpkin()
			require.NoError(t, err)
			require.Equal(t, tt.want, got)
		})
	}
}

func Test_parser_getURL(t *testing.T) {
	type fields struct {
		path               string
		originRequestError error
	}
	tests := []struct {
		name      string
		fields    fields
		want      string
		wantError bool
	}{
		{
			name: "Got error from origin request getter",
			fields: fields{
				path:               "",
				originRequestError: errors.Error("some kind of error"),
			},
			want:      "",
			wantError: true,
		},
		{
			name: "Got not empty origin request",
			fields: fields{
				path:               "/for_test/?ok=1",
				originRequestError: nil,
			},
			want: "/for_test/?ok=1",
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			originKeeperMock := NewMockoriginRequestKeeper(gomock.NewController(t))
			originKeeperMock.EXPECT().GetOriginRequest().Return(
				&models.OriginRequest{
					Path: tt.fields.path,
				},
				tt.fields.originRequestError,
			).MaxTimes(1)

			k := &parser{
				originRequestKeeper: originKeeperMock,
			}

			got, err := k.getURL()

			require.Equal(t, tt.wantError, err != nil)
			require.Equal(t, tt.want, got)
		})
	}
}

func Test_parser_getIP(t *testing.T) {
	type fields struct {
		headers      map[string][]string
		requestError error
	}
	tests := []struct {
		name      string
		fields    fields
		want      string
		wantError bool
	}{
		{
			name: "Got error from origin getter",
			fields: fields{
				requestError: errors.Error("some kind of error"),
			},
			want:      "",
			wantError: true,
		},
		{
			name: "Got ip from X-Forwarded-For-Y",
			fields: fields{
				headers: map[string][]string{
					"X-Forwarded-For-Y": {"127.0.0.1"},
				},
			},
			want: "127.0.0.1",
		},
		{
			name: "Got ip from X-Real-Ip",
			fields: fields{
				headers: map[string][]string{
					"X-Real-Ip": {"127.0.0.1"},
				},
			},
			want: "127.0.0.1",
		},
		{
			name: "Got ip from X-Real-Remote-Ip",
			fields: fields{
				headers: map[string][]string{
					"X-Real-Remote-Ip": {"127.0.0.1"},
				},
			},
			want: "127.0.0.1",
		},
		{
			name: "Ip in all checked headers",
			fields: fields{
				headers: map[string][]string{
					"X-Forwarded-For-Y": {"127.0.0.10"},
					"X-Real-Ip":         {"127.0.0.11"},
					"X-Real-Remote-Ip":  {"127.0.0.12"},
				},
			},
			want: "127.0.0.10",
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			originKeeperMock := NewMockoriginRequestKeeper(gomock.NewController(t))
			originKeeperMock.EXPECT().GetOriginRequest().Return(
				&models.OriginRequest{
					Headers: tt.fields.headers,
				},
				tt.fields.requestError,
			).MaxTimes(1)

			k := &parser{
				originRequestKeeper: originKeeperMock,
			}

			got, err := k.getIP()

			require.Equal(t, tt.wantError, err != nil)
			require.Equal(t, tt.want, got)
		})
	}
}

func Test_parser_getCGIParams(t *testing.T) {
	type fields struct {
		path string
	}
	tests := []struct {
		name    string
		fields  fields
		want    url.Values
		wantErr bool
	}{
		{
			name: "empty",
			fields: fields{
				path: "",
			},
			want:    url.Values{},
			wantErr: false,
		},
		{
			name: "without cgi",
			fields: fields{
				path: "/for_test",
			},
			want:    url.Values{},
			wantErr: false,
		},
		{
			name: "without slash",
			fields: fields{
				path: "for_test",
			},
			want:    url.Values{},
			wantErr: false,
		},
		{
			name: "several simple cgi",
			fields: fields{
				path: "/for_test?a=1&city=moscow&fruit=apple&city=spb&debug",
			},
			want: url.Values{
				"a":     {"1"},
				"city":  {"moscow", "spb"},
				"fruit": {"apple"},
				"debug": {""},
			},
			wantErr: false,
		},
		{
			name: "invalid query from prod 1",
			fields: fields{
				path: "/?clid=44289&amp;yasoft=barie",
			},
			want:    url.Values{},
			wantErr: true,
		},
		{
			name: "invalid query from prod 2",
			fields: fields{
				path: "/?adgroupid=64837943225&amp;campaignid=1679778663&amp;creative=325777385260&amp;gclid=CjwKCAjw9uKIBhA8EiwAYPUS3Iy0pweI9WZZ7e9SFGHUiFhV7U-QRzUPQnc8ekOaNi6lUFv1iFkV-RoCoAYQAvD_BwE&amp;keyword=%D1%8F%D0%BD%D0%B4%D0%B5%D0%BA%D1%81&amp;utm_campaign=brand_search_ru&amp;utm_medium=search&amp;utm_source=google&amp;utm_term=%D1%8F%D0%BD%D0%B4%D0%B5%D0%BA%D1%81",
			},
			want:    url.Values{},
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			originRequestKeeper := NewMockoriginRequestKeeper(gomock.NewController(t))
			originRequestKeeper.EXPECT().GetOriginRequest().Return(
				&models.OriginRequest{
					Path: tt.fields.path,
				},
				nil,
			)

			p := &parser{
				originRequestKeeper: originRequestKeeper,
			}
			got, err := p.getCGIParams()

			// именно assert; ошибка может игнорироваться, хотим проверять возвращаемое значение всегда
			assert.Equal(t, tt.wantErr, err != nil)
			assert.Equal(t, tt.want, got)
		})
	}
}

func Test_parser_getHost(t *testing.T) {
	type fields struct {
		createOriginRequestKeeper func(t *testing.T) *MockoriginRequestKeeper
	}

	tests := []struct {
		name    string
		fields  fields
		want    string
		wantErr assert.ErrorAssertionFunc
	}{
		{
			name: "failed",
			fields: fields{
				createOriginRequestKeeper: func(t *testing.T) *MockoriginRequestKeeper {
					keeper := NewMockoriginRequestKeeper(gomock.NewController(t))
					keeper.EXPECT().GetOriginRequest().Return(nil, errors.Error("error"))
					return keeper
				},
			},
			want:    "",
			wantErr: assert.Error,
		},
		{
			name: "success",
			fields: fields{
				createOriginRequestKeeper: func(t *testing.T) *MockoriginRequestKeeper {
					keeper := NewMockoriginRequestKeeper(gomock.NewController(t))
					keeper.EXPECT().GetOriginRequest().Return(&models.OriginRequest{
						Headers: map[string][]string{
							"Host": {"www.yandex.ru"},
						},
					}, nil)
					return keeper
				},
			},
			want:    "www.yandex.ru",
			wantErr: assert.NoError,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			p := &parser{
				originRequestKeeper: tt.fields.createOriginRequestKeeper(t),
			}

			got, err := p.getHost()
			assert.Equal(t, tt.want, got)
			tt.wantErr(t, err)
		})
	}
}

func Test_parser_parseSearchAppFeaturesAsPostArg(t *testing.T) {
	type testCase struct {
		name        string
		arg         []byte
		want        []searchAppFeature
		wantErrFunc assert.ErrorAssertionFunc
	}

	cases := []testCase{
		{
			name:        "no features arg",
			arg:         []byte("some_other_arg=42"),
			want:        nil,
			wantErrFunc: assert.NoError,
		},
		{
			name: "regular case",
			arg:  []byte(`features=[{"enabled":false,"feature":"ya_plus"},{"enabled":true,"feature":"account"}]`),
			want: []searchAppFeature{
				{
					Name:    "ya_plus",
					Enabled: false,
				},
				{
					Name:    "account",
					Enabled: true,
				},
			},
			wantErrFunc: assert.NoError,
		},
		{
			name: "regular case with parametrized feature",
			arg: []byte(`features=[
					{
						"feature": "widget",
						"enabled": false,
						"parameters": [
							{
								"name": "type",
								"value": "searchlib_4x2"
							}
						]
					},
					{
						"feature": "widget",
						"enabled": false,
						"parameters": [
							{
								"name": "type",
								"value": "zen_subscriptions_4x2"
							}
						]
					},
					{
						"feature": "widget",
						"enabled": true,
						"parameters": [
							{
								"name": "type",
								"value": "2x1"
							}
						]
					}
				]
			`),
			want: []searchAppFeature{
				{
					Name:    "widget",
					Enabled: false,
					Parameters: []searchAppFeatureParameter{
						{
							Name:  "type",
							Value: "searchlib_4x2",
						},
					},
				},
				{
					Name:    "widget",
					Enabled: false,
					Parameters: []searchAppFeatureParameter{
						{
							Name:  "type",
							Value: "zen_subscriptions_4x2",
						},
					},
				},
				{
					Name:    "widget",
					Enabled: true,
					Parameters: []searchAppFeatureParameter{
						{
							Name:  "type",
							Value: "2x1",
						},
					},
				},
			},
			wantErrFunc: assert.NoError,
		},
		{
			name:        "not a json in features key",
			arg:         []byte(`features=some_trash`),
			want:        nil,
			wantErrFunc: assert.Error,
		},
		{
			name:        "json instead of post args",
			arg:         []byte(`{"features": [{"enabled":false,"feature":"ya_plus"},{"enabled":true,"feature":"account"}]}`),
			want:        nil,
			wantErrFunc: assert.NoError,
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			var p parser
			actual, err := p.parseSearchAppFeaturesAsPostArg(tt.arg)
			assert.Equal(t, tt.want, actual, "check parsed features")
			tt.wantErrFunc(t, err, "check parsing error")
		})
	}
}

func Test_parser_parseSearchAppFeaturesAsJSON(t *testing.T) {
	type testCase struct {
		name        string
		arg         []byte
		want        []searchAppFeature
		wantErrFunc assert.ErrorAssertionFunc
	}

	cases := []testCase{
		{
			name:        "empty slice",
			arg:         nil,
			want:        nil,
			wantErrFunc: assert.Error,
		},
		{
			name: "no features keys",
			arg: []byte(`{
				"some_key": 42
			}`),
			want:        nil,
			wantErrFunc: assert.NoError,
		},
		{
			name: "empty feature slice",
			arg: []byte(`{
				"features": []
			}`),
			want:        make([]searchAppFeature, 0),
			wantErrFunc: assert.NoError,
		},
		{
			name: "regular case",
			arg: []byte(`{"features":
				[{"enabled":false,"feature":"ya_plus"},{"enabled":true,"feature":"account"}]
			}`),
			want: []searchAppFeature{
				{
					Name:    "ya_plus",
					Enabled: false,
				},
				{
					Name:    "account",
					Enabled: true,
				},
			},
			wantErrFunc: assert.NoError,
		},
		{
			name: "regular case with parametrized feature",
			arg: []byte(`{"features":
				[
					{
						"feature": "widget",
						"enabled": false,
						"parameters": [
							{
								"name": "type",
								"value": "searchlib_4x2"
							}
						]
					},
					{
						"feature": "widget",
						"enabled": false,
						"parameters": [
							{
								"name": "type",
								"value": "zen_subscriptions_4x2"
							}
						]
					},
					{
						"feature": "widget",
						"enabled": true,
						"parameters": [
							{
								"name": "type",
								"value": "2x1"
							}
						]
					}
				]
			}`),
			want: []searchAppFeature{
				{
					Name:    "widget",
					Enabled: false,
					Parameters: []searchAppFeatureParameter{
						{
							Name:  "type",
							Value: "searchlib_4x2",
						},
					},
				},
				{
					Name:    "widget",
					Enabled: false,
					Parameters: []searchAppFeatureParameter{
						{
							Name:  "type",
							Value: "zen_subscriptions_4x2",
						},
					},
				},
				{
					Name:    "widget",
					Enabled: true,
					Parameters: []searchAppFeatureParameter{
						{
							Name:  "type",
							Value: "2x1",
						},
					},
				},
			},
			wantErrFunc: assert.NoError,
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			var p parser
			actual, err := p.parseSearchAppFeaturesAsJSON(tt.arg)
			assert.Equal(t, tt.want, actual, "check parsed features")
			tt.wantErrFunc(t, err, "check parsing error")
		})
	}
}

func Test_parser_getSearchAppFeatures(t *testing.T) {
	type testCase struct {
		name          string
		originRequest *models.OriginRequest
		want          models.SearchAppFeatures
		wantErrFunc   assert.ErrorAssertionFunc
	}

	cases := []testCase{
		{
			name:          "nil request",
			originRequest: nil,
			want:          nil,
			wantErrFunc:   assert.Error,
		},
		{
			name: "request with GET method",
			originRequest: &models.OriginRequest{
				Method: protoanswers.THttpRequest_Get,
			},
			want:        nil,
			wantErrFunc: assert.NoError,
		},
		{
			name: "empty POST body",
			originRequest: &models.OriginRequest{
				Method:  protoanswers.THttpRequest_Post,
				Content: nil,
			},
			want:        nil,
			wantErrFunc: assert.NoError,
		},
		{
			name: "post args without features",
			originRequest: &models.OriginRequest{
				Method:  protoanswers.THttpRequest_Post,
				Content: []byte(`some_other_key=[{"enabled":false,"feature":"ya_plus"},{"enabled":true,"feature":"account"}]`),
			},
			want:        nil,
			wantErrFunc: assert.NoError,
		},
		{
			name: "post args",
			originRequest: &models.OriginRequest{
				Method: protoanswers.THttpRequest_Post,
				Content: []byte(`features=[{"enabled":false,"feature":"ya_plus"},{"enabled":true,"feature":"account"},
					{
						"feature": "widget",
						"enabled": false,
						"parameters": [
							{
								"name": "type",
								"value": "zen_subscriptions_4x2"
							}
						]
					},
					{
						"feature": "widget",
						"enabled": true,
						"parameters": [
							{
								"name": "type",
								"value": "2x1"
							}
						]
					}]`),
			},
			want: models.SearchAppFeatures{
				{
					Name:    "ya_plus",
					Enabled: false,
				},
				{
					Name:    "account",
					Enabled: true,
				},
				{
					Name:    "widget",
					Enabled: false,
					Parameters: map[string]string{
						"type": "zen_subscriptions_4x2",
					},
				},
				{
					Name:    "widget",
					Enabled: true,
					Parameters: map[string]string{
						"type": "2x1",
					},
				},
			},
			wantErrFunc: assert.NoError,
		},
		{
			name: "post args with incorrect features",
			originRequest: &models.OriginRequest{
				Method:  protoanswers.THttpRequest_Post,
				Content: []byte(`features=some_trash`),
			},
			want:        nil,
			wantErrFunc: assert.NoError,
		},
		{
			name: "json in post body",
			originRequest: &models.OriginRequest{
				Method:  protoanswers.THttpRequest_Post,
				Content: []byte(`{"features": [{"enabled":false,"feature":"ya_plus"},{"enabled":true,"feature":"account"}]}`),
			},
			want: models.SearchAppFeatures{
				{
					Name:    "ya_plus",
					Enabled: false,
				},
				{
					Name:    "account",
					Enabled: true,
				},
			},
			wantErrFunc: assert.NoError,
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			originRequestKeeperMock := NewMockoriginRequestKeeper(ctrl)
			var originRequestErr error = nil
			if tt.originRequest == nil {
				originRequestErr = errors.Error("origin request error")
			}
			originRequestKeeperMock.EXPECT().GetOriginRequest().Return(tt.originRequest, originRequestErr)

			p := &parser{
				originRequestKeeper: originRequestKeeperMock,
			}

			actual, err := p.getSearchAppFeatures()
			assert.Equal(t, tt.want, actual, "check features map")
			tt.wantErrFunc(t, err, "check error")
		})
	}
}
