package searchapp

import (
	"net/http"
	"testing"

	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/require"

	protoanswers "a.yandex-team.ru/apphost/lib/proto_answers"
	"a.yandex-team.ru/portal/avocado/avocado/pkg/new-internal/blackbox"
	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/libs/utils/log2"
	"a.yandex-team.ru/portal/morda-go/tests/helpers"
	"a.yandex-team.ru/portal/morda-go/tests/mocks"
)

func Test_Parser(t *testing.T) {
	tests := []struct {
		name string
		parserTestCase
	}{
		{
			name: "OAuthHeader is empty & SessionID is empty",
			parserTestCase: parserTestCase{
				wantAdd: false,
				wantErr: false,
			},
		},
		{
			name: "OAuthHeader is not empty",
			parserTestCase: parserTestCase{
				additionalHeaders: map[string]string{"Authorization": "test"},
				wantAdd:           true,
				wantTypePB:        "blackbox_proto_http_request",
				wantAddedPB: &protoanswers.THttpRequest{
					Method:  protoanswers.THttpRequest_Get,
					Scheme:  protoanswers.THttpRequest_Https,
					Path:    "/blackbox?attributes=1016&dbfields=subscription.suid.669&emails=getdefault&format=json&get_user_ticket=yes&host=yandex.ru&method=oauth&multisession=1&userip=%3A%3A1",
					Headers: []*protoanswers.THeader{{Name: "Authorization", Value: "test"}},
				},
				wantErr: false,
			},
		},
		{
			name: "SessionID is not empty",
			parserTestCase: parserTestCase{
				sessionID:  "19428",
				wantAdd:    true,
				wantTypePB: "blackbox_proto_http_request",
				wantAddedPB: &protoanswers.THttpRequest{
					Method: protoanswers.THttpRequest_Get,
					Scheme: protoanswers.THttpRequest_Https,
					Path:   "/blackbox?attributes=1016&dbfields=subscription.suid.669&emails=getdefault&format=json&get_user_ticket=yes&host=yandex.ru&multisession=1&sessionid=19428&sslsessionid=&userip=%3A%3A1",
				},
				wantErr: false,
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			require.NoError(t, log2.Init(log2.WithStdout()))
			tt.initMocks()

			err := Parser(tt.ctxMock)

			tt.ctxMock.AssertExpectations(t)
			if tt.wantErr {
				require.Error(t, err)
			} else {
				require.NoError(t, err)
			}
		})
	}
}

type parserTestCase struct {
	ctxMock           *mocks.ApphostContext
	additionalHeaders map[string]string
	sessionID         string
	wantAdd           bool
	wantTypePB        string
	wantAddedPB       *protoanswers.THttpRequest
	wantErr           bool
}

func (c *parserTestCase) initMocks() {
	c.ctxMock = &mocks.ApphostContext{}
	c.ctxMock.On("Path").Return("")

	// работа Wrapper
	mockGeo(c.ctxMock, c.additionalHeaders, c.sessionID)
	if c.wantAdd {
		c.ctxMock.
			On("AddPB", c.wantTypePB,
				mock.MatchedBy(func(obj *protoanswers.THttpRequest) bool {
					return helpers.THttpRequestCompare(obj, c.wantAddedPB)
				})).
			Return(nil).
			Once()
	}
}

func Test_parse(t *testing.T) {
	type args struct {
		header  *http.Header
		cookies *models.YaCookies
		ip      *string
	}
	var tests = []struct {
		name    string
		args    args
		want    *protoanswers.THttpRequest
		wantErr bool
	}{
		{
			name: "OAuthHeader is empty & SessionID is empty",
			args: args{
				header:  &http.Header{},
				cookies: &models.YaCookies{},
			},
			wantErr: false,
		},
		{
			name: "OAuthHeader is not empty",
			args: args{
				header: &testAuthHeader,
				ip:     &testIP,
			},
			want: &protoanswers.THttpRequest{
				Method:  protoanswers.THttpRequest_Get,
				Scheme:  protoanswers.THttpRequest_Https,
				Path:    "/blackbox?attributes=1016&dbfields=subscription.suid.669&emails=getdefault&format=json&get_user_ticket=yes&host=yandex.ru&method=oauth&multisession=1&userip=%3A%3A1",
				Headers: []*protoanswers.THeader{{Name: "Authorization", Value: "test"}},
			},
		},
		{
			name: "SessionID is not empty",
			args: args{
				header: &http.Header{},
				cookies: &models.YaCookies{
					SessionID:  "19428",
					SessionID2: "81",
				},
				ip: &testIP,
			},
			want: &protoanswers.THttpRequest{
				Method: protoanswers.THttpRequest_Get,
				Scheme: protoanswers.THttpRequest_Https,
				Path:   "/blackbox?attributes=1016&dbfields=subscription.suid.669&emails=getdefault&format=json&get_user_ticket=yes&host=yandex.ru&multisession=1&sessionid=19428&sslsessionid=81&userip=%3A%3A1",
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ctxMock := &mocks.GeohelperContext{}
			initMockByParseCase(ctxMock, tt.args.header, tt.args.cookies, tt.args.ip, tt.want)

			err := parse(ctxMock)

			ctxMock.AssertExpectations(t)
			if tt.wantErr {
				require.Error(t, err)
			} else {
				require.NoError(t, err)
			}
		})
	}
}

func initMockByParseCase(ctxMock *mocks.GeohelperContext, header *http.Header, cookies *models.YaCookies, ip *string, want *protoanswers.THttpRequest) {
	if header != nil {
		ctxMock.On("GetHeaders").Return(*header).Once()
	}

	if cookies != nil {
		ctxMock.On("GetCookies").Return(*cookies).Once()
	}

	if ip != nil {
		ctxMock.On("GetIP").Return(*ip).Once()
	}

	if want != nil {
		ctxMock.On("AddPB", blackbox.ProtoHTTPRequest, mock.MatchedBy(func(obj *protoanswers.THttpRequest) bool {
			return helpers.THttpRequestCompare(obj, want)
		})).Return(nil).Once()
	}
}

var testAuthHeader = http.Header(map[string][]string{"Authorization": {"test"}})
var testIP = "::1"
