package madmcontent

import (
	"net/url"
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/libs/utils/experiments/httpprocessor"
	"a.yandex-team.ru/portal/avocado/libs/utils/staticparams"
	"a.yandex-team.ru/portal/avocado/morda-go/pkg/exports"
)

func Test_parser_checkTouchOnly(t *testing.T) {
	type fields struct {
		domain      models.Domain
		madmOptions exports.Options
		checked     bool
	}

	type args struct {
		path    string
		request models.Request
	}

	tests := []struct {
		name   string
		fields fields
		args   args
		want   bool
	}{
		{
			name: "check handler success",
			fields: fields{
				checked: true,
			},
			args: args{
				path: "/some/path",
			},
			want: true,
		},
		{
			name: "check handler failed",
			fields: fields{
				checked: false,
			},
			args: args{
				path: "/some/path",
				request: models.Request{
					APIInfo: models.APIInfo{Name: "api"},
				},
			},
			want: false,
		},
		{
			name: "check handler success is morda lite",
			fields: fields{
				checked: false,
				domain:  models.Domain{Domain: "ya.ru"},
				madmOptions: exports.Options{
					MordaLiteOptions: exports.MordaLiteOptions{
						EnableWebLiteForYaruByHost: "all",
						WebLiteTestID:              "",
					},
				},
			},
			args: args{
				path: "/some/path",
			},
			want: true,
		},
		{
			name: "check handler success is web",
			fields: fields{
				checked: false,
				domain:  models.Domain{Domain: "yandex.ru"},
			},
			args: args{
				path: "/some/path",
				request: models.Request{
					APIInfo: models.APIInfo{Name: ""},
				},
			},
			want: true,
		},
		{
			name: "check handler success is web",
			fields: fields{
				checked: false,
				domain:  models.Domain{Domain: "yandex.ru"},
			},
			args: args{
				path: "/some/path",
				request: models.Request{
					APIInfo: models.APIInfo{Name: "api"},
				},
			},
			want: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)

			handlerCheckerMock := NewMockhandlerChecker(ctrl)
			handlerCheckerMock.EXPECT().Check(gomock.Any()).Return(tt.fields.checked)

			domainGetterMock := NewMockdomainGetter(ctrl)
			domainGetterMock.EXPECT().GetDomain().Return(tt.fields.domain).MaxTimes(1)

			madmOptionsGetterMock := NewMockmadmOptionsGetter(ctrl)
			madmOptionsGetterMock.EXPECT().GetMadmOptions().Return(tt.fields.madmOptions).MaxTimes(1)

			p := &parser{
				domainGetter:      domainGetterMock,
				madmOptionsGetter: madmOptionsGetterMock,
				handlerChecker:    handlerCheckerMock,
			}

			assert.Equal(t, tt.want, p.checkTouchOnly(tt.args.request, tt.args.path))
		})
	}
}

func Test_parser_checkAPIBroPP(t *testing.T) {
	type args struct {
		request models.Request
	}

	tests := []struct {
		name string
		args args
		want bool
	}{
		{
			name: "success",
			args: args{
				request: models.Request{
					CGI: url.Values{
						"bropp": {"1"},
					},
				},
			},
			want: true,
		},
		{
			name: "failed",
			args: args{
				request: models.Request{
					CGI: url.Values{
						"bropp": {"0"},
					},
				},
			},
			want: false,
		},
		{
			name: "no value",
			args: args{
				request: models.Request{
					CGI: url.Values{},
				},
			},
			want: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			p := &parser{}

			assert.Equal(t, tt.want, p.checkAPIBroPP(tt.args.request))
		})
	}
}

func Test_parser_resolveTouch(t *testing.T) {
	type fields struct {
		madmOptions          exports.Options
		domain               models.Domain
		createHandlerChecker func(t *testing.T) *MockhandlerChecker
	}

	type args struct {
		request models.Request
		appInfo models.AppInfo
	}

	tests := []struct {
		name    string
		fields  fields
		args    args
		want    []string
		wantErr require.ErrorAssertionFunc
	}{
		{
			name: "parse url error",
			fields: fields{
				createHandlerChecker: func(t *testing.T) *MockhandlerChecker {
					return nil
				},
			},
			args: args{
				request: models.Request{URL: "\\http:"},
			},
			want:    nil,
			wantErr: require.Error,
		},
		{
			name: "is touch only",
			fields: fields{
				createHandlerChecker: func(t *testing.T) *MockhandlerChecker {
					checker := NewMockhandlerChecker(gomock.NewController(t))
					checker.EXPECT().Check(gomock.Any()).Return(true)
					return checker
				},
			},
			args: args{
				request: models.Request{URL: "/some/url"},
			},
			want:    []string{TouchOnly, TouchCommon},
			wantErr: require.NoError,
		},
		{
			name: "is touch only lite",
			fields: fields{
				madmOptions: exports.Options{
					MordaLiteOptions: exports.MordaLiteOptions{
						EnableWebLiteForYaruByHost: "all",
						WebLiteTestID:              "",
					},
				},
				domain: models.Domain{Domain: "ya.ru"},
				createHandlerChecker: func(t *testing.T) *MockhandlerChecker {
					checker := NewMockhandlerChecker(gomock.NewController(t))
					checker.EXPECT().Check(gomock.Any()).Return(true)
					return checker
				},
			},
			args: args{
				request: models.Request{URL: "/some/url"},
			},
			want:    []string{TouchOnly, TouchLite},
			wantErr: require.NoError,
		},
		{
			name: "is api search",
			fields: fields{
				createHandlerChecker: func(t *testing.T) *MockhandlerChecker {
					checker := NewMockhandlerChecker(gomock.NewController(t))
					checker.EXPECT().Check(gomock.Any()).Return(false)
					return checker
				},
			},
			args: args{
				request: models.Request{
					URL: "/portal/api/search/2",
					APIInfo: models.APIInfo{
						Name:    "search",
						Version: 2,
					},
				},
			},
			want:    []string{APISearch2Only, APISearch2Strict, APISearch2},
			wantErr: require.NoError,
		},
		{
			name: "is api search not strict",
			fields: fields{
				createHandlerChecker: func(t *testing.T) *MockhandlerChecker {
					checker := NewMockhandlerChecker(gomock.NewController(t))
					checker.EXPECT().Check(gomock.Any()).Return(false)
					return checker
				},
			},
			args: args{
				request: models.Request{
					URL: "/portal/api/search/2",
					APIInfo: models.APIInfo{
						Name:    "search",
						Version: 2,
					},
					CGI: url.Values{"start_app": {"1"}},
				},
			},
			want:    []string{APISearch2Only, APISearch2},
			wantErr: require.NoError,
		},
		{
			name: "is api search with api broopp",
			fields: fields{
				createHandlerChecker: func(t *testing.T) *MockhandlerChecker {
					checker := NewMockhandlerChecker(gomock.NewController(t))
					checker.EXPECT().Check(gomock.Any()).Return(false)
					return checker
				},
			},
			args: args{
				request: models.Request{
					URL: "/portal/api/search/2?bropp=1",
					CGI: url.Values{
						"bropp": {"1"},
					},
					APIInfo: models.APIInfo{
						Name:    "search",
						Version: 2,
					},
				},
			},
			want:    []string{APIBropp, APISearch2Only, APISearch2Strict, APISearch2},
			wantErr: require.NoError,
		},
		{
			name: "is api search with api search prod",
			fields: fields{
				createHandlerChecker: func(t *testing.T) *MockhandlerChecker {
					checker := NewMockhandlerChecker(gomock.NewController(t))
					checker.EXPECT().Check(gomock.Any()).Return(false)
					return checker
				},
			},
			args: args{
				request: models.Request{
					URL: "/portal/api/search/2",
					APIInfo: models.APIInfo{
						Name:    "search",
						Version: 2,
					},
				},
				appInfo: models.AppInfo{
					ID: "ru.yandex.searchplugin",
				},
			},
			want:    []string{APISearch2Only, APISearch2Strict, APISearchProd, APISearch2},
			wantErr: require.NoError,
		},
		{
			name: "is api search with api search beta",
			fields: fields{
				createHandlerChecker: func(t *testing.T) *MockhandlerChecker {
					checker := NewMockhandlerChecker(gomock.NewController(t))
					checker.EXPECT().Check(gomock.Any()).Return(false)
					return checker
				},
			},
			args: args{
				request: models.Request{
					URL: "/portal/api/search/2",
					APIInfo: models.APIInfo{
						Name:    "search",
						Version: 2,
					},
				},
				appInfo: models.AppInfo{
					ID: "ru.yandex.searchplugin.beta",
				},
			},
			want:    []string{APISearch2Only, APISearch2Strict, APISearchBeta, APISearch2},
			wantErr: require.NoError,
		},
		{
			name: "no contents",
			fields: fields{
				createHandlerChecker: func(t *testing.T) *MockhandlerChecker {
					checker := NewMockhandlerChecker(gomock.NewController(t))
					checker.EXPECT().Check(gomock.Any()).Return(false)
					return checker
				},
			},
			args: args{
				request: models.Request{URL: "/some/url", APIInfo: models.APIInfo{Name: "api"}},
			},
			want:    nil,
			wantErr: require.NoError,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)

			requestGetterMock := NewMockrequestGetter(ctrl)
			requestGetterMock.EXPECT().GetRequest().Return(tt.args.request).MaxTimes(2)

			madmOptionsMock := NewMockmadmOptionsGetter(ctrl)
			madmOptionsMock.EXPECT().GetMadmOptions().Return(tt.fields.madmOptions).MaxTimes(1)

			domainGetterMock := NewMockdomainGetter(ctrl)
			domainGetterMock.EXPECT().GetDomain().Return(tt.fields.domain).MaxTimes(1)

			p := &parser{
				requestGetter:     requestGetterMock,
				madmOptionsGetter: madmOptionsMock,
				handlerChecker:    tt.fields.createHandlerChecker(t),
				domainGetter:      domainGetterMock,
			}

			got, err := p.parseTouch(tt.args.request, tt.args.appInfo)
			tt.wantErr(t, err)
			assert.Equal(t, tt.want, got)
		})
	}
}

func Test_parser_Parse(t *testing.T) {
	type fields struct {
		request              models.Request
		mordaContent         models.MordaContent
		madmOptions          exports.Options
		location             staticparams.Location
		expBoxes             []httpprocessor.ExperimentBox
		domain               models.Domain
		createHandlerChecker func(t *testing.T) *MockhandlerChecker
	}

	tests := []struct {
		name    string
		fields  fields
		want    models.MadmContent
		wantErr require.ErrorAssertionFunc
	}{
		{
			name: "default content",
			fields: fields{
				request: models.Request{
					URL: "some/url",
				},
				mordaContent: models.MordaContent{
					Value: "some_content",
				},
				createHandlerChecker: func(t *testing.T) *MockhandlerChecker {
					return nil
				},
			},
			want: models.MadmContent{
				Values: []string{"some_content", All},
			},
			wantErr: require.NoError,
		},
		{
			name: "resolver touch",
			fields: fields{
				request: models.Request{
					URL: "some/url",
				},
				mordaContent: models.MordaContent{
					Value: "touch",
				},
				createHandlerChecker: func(t *testing.T) *MockhandlerChecker {
					checker := NewMockhandlerChecker(gomock.NewController(t))
					checker.EXPECT().Check(gomock.Any()).Return(true)
					return checker
				},
			},
			want: models.MadmContent{
				Values: []string{TouchOnly, TouchCommon, Touch, All},
			},
			wantErr: require.NoError,
		},
		{
			name: "resolver touch error",
			fields: fields{
				request: models.Request{
					URL: "\\http:",
				},
				mordaContent: models.MordaContent{
					Value: "touch",
				},
				createHandlerChecker: func(t *testing.T) *MockhandlerChecker {
					return nil
				},
			},
			want: models.MadmContent{
				Values: []string{Touch, All},
			},
			wantErr: require.Error,
		},
		{
			name: "big content",
			fields: fields{
				request: models.Request{
					URL: "some/url",
				},
				mordaContent: models.MordaContent{
					Value: "big",
				},
				createHandlerChecker: func(t *testing.T) *MockhandlerChecker {
					return nil
				},
			},
			want: models.MadmContent{
				Values: []string{BigCommon, BigOrYabrotab, Big, All},
			},
			wantErr: require.NoError,
		},
		{
			name: "big lite content enable for vla",
			fields: fields{
				domain: models.Domain{Domain: "ya.ru"},
				mordaContent: models.MordaContent{
					Value: "big",
				},
				madmOptions: exports.Options{
					MordaLiteOptions: exports.MordaLiteOptions{
						EnableWebLiteForYaruByHost: "fdsfsd vla fsdf",
						WebLiteTestID:              "",
					},
				},
				location: staticparams.VlaLocation,
				createHandlerChecker: func(t *testing.T) *MockhandlerChecker {
					return nil
				},
			},
			want: models.MadmContent{
				Values: []string{BigLite, BigOrYabrotab, Big, All},
			},
			wantErr: require.NoError,
		},
		{
			name: "big lite content enable all",
			fields: fields{
				domain: models.Domain{Domain: "ya.ru"},
				mordaContent: models.MordaContent{
					Value: "big",
				},
				madmOptions: exports.Options{
					MordaLiteOptions: exports.MordaLiteOptions{
						EnableWebLiteForYaruByHost: "all",
						WebLiteTestID:              "",
					},
				},
				createHandlerChecker: func(t *testing.T) *MockhandlerChecker {
					return nil
				},
			},
			want: models.MadmContent{
				Values: []string{BigLite, BigOrYabrotab, Big, All},
			},
			wantErr: require.NoError,
		},
		{
			name: "big lite content enable test id",
			fields: fields{
				domain: models.Domain{Domain: "ya.ru"},
				mordaContent: models.MordaContent{
					Value: "big",
				},
				madmOptions: exports.Options{
					MordaLiteOptions: exports.MordaLiteOptions{
						EnableWebLiteForYaruByHost: "fdsfsd vla fsdf",
						WebLiteTestID:              "1,3,5",
					},
				},
				location: staticparams.SasLocation,
				expBoxes: []httpprocessor.ExperimentBox{
					{
						TestID: 2,
					},
					{
						TestID: 4,
					},
					{
						TestID: 3,
					},
				},
				createHandlerChecker: func(t *testing.T) *MockhandlerChecker {
					return nil
				},
			},
			want: models.MadmContent{
				Values: []string{BigLite, BigOrYabrotab, Big, All},
			},
			wantErr: require.NoError,
		},
		{
			name: "yabrotab content",
			fields: fields{
				request: models.Request{
					URL: "some/url",
				},
				mordaContent: models.MordaContent{
					Value: "yabrotab",
				},
				createHandlerChecker: func(t *testing.T) *MockhandlerChecker {
					return nil
				},
			},
			want: models.MadmContent{
				Values: []string{BigOrYabrotab, Yabrotab, All},
			},
			wantErr: require.NoError,
		},
		{
			name: "yabrotab content start app",
			fields: fields{
				request: models.Request{
					URL: "some/url",
					CGI: url.Values{"start_app": {"1"}},
				},
				mordaContent: models.MordaContent{
					Value: "yabrotab",
				},
				createHandlerChecker: func(t *testing.T) *MockhandlerChecker {
					return nil
				},
			},
			want: models.MadmContent{
				Values: []string{BigOrYabrotab, StartApp, Yabrotab, All},
			},
			wantErr: require.NoError,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)

			requestGetterMock := NewMockrequestGetter(ctrl)
			requestGetterMock.EXPECT().GetRequest().Return(tt.fields.request).AnyTimes()

			appInfoGetterMock := NewMockappInfoGetter(gomock.NewController(t))
			appInfoGetterMock.EXPECT().GetAppInfo().Return(models.AppInfo{}).Times(1)

			mordaContentGetterMock := NewMockmordaContentGetter(gomock.NewController(t))
			mordaContentGetterMock.EXPECT().GetMordaContent().Return(tt.fields.mordaContent).Times(1)

			madmOptionsMock := NewMockmadmOptionsGetter(ctrl)
			madmOptionsMock.EXPECT().GetMadmOptions().Return(tt.fields.madmOptions).MaxTimes(2)

			httpWrapperMock := NewMockhttpWrapper(ctrl)
			httpWrapperMock.EXPECT().GetExpBoxes(gomock.Any()).Return("").MaxTimes(1)

			httpProcessorMock := NewMockhttpFlagsProcessor(ctrl)
			httpProcessorMock.EXPECT().ParseExperimentBoxes(gomock.Any()).Return(tt.fields.expBoxes, nil).MaxTimes(1)

			domainGetterMock := NewMockdomainGetter(ctrl)
			domainGetterMock.EXPECT().GetDomain().Return(tt.fields.domain).MaxTimes(1)

			p := NewParser(
				tt.fields.location,
				requestGetterMock,
				appInfoGetterMock,
				mordaContentGetterMock,
				tt.fields.createHandlerChecker(t),
				madmOptionsMock,
				httpWrapperMock,
				httpProcessorMock,
				domainGetterMock,
			)

			got, err := p.Parse()
			tt.wantErr(t, err)
			assert.Equal(t, tt.want, got)
		})
	}
}
