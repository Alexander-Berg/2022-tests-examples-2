package searchapp

import (
	"net/http"
	"testing"

	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/require"

	protoanswers "a.yandex-team.ru/apphost/lib/proto_answers"
	"a.yandex-team.ru/portal/avocado/avocado/pkg/new-internal/geohelper"
	"a.yandex-team.ru/portal/morda-go/pkg/dto"
	"a.yandex-team.ru/portal/morda-go/tests/helpers"
	"a.yandex-team.ru/portal/morda-go/tests/mocks"
)

func Test_prepare(t *testing.T) {
	tests := []struct {
		name     string
		testCase prepareTestCase
		wantErr  bool
	}{
		{
			name: "No skipped blocks; auth not valid",
			testCase: prepareTestCase{
				blackboxResponse: &protoanswers.THttpResponse{
					StatusCode: http.StatusOK,
					Content:    []byte(`{"error":"some kind of error"}`),
				},
				putAuth:             &dto.Auth{},
				body:                []byte(`{}`),
				skippedBlocks:       []string{},
				geohelperRequest:    &protoanswers.THttpRequest{},
				url:                 &testURL,
				wantGeoRequest:      &protoanswers.THttpRequest{Path: "http://test.com/smth?skip_blocks="},
				wantDebugGeoRequest: nil,
			},
			wantErr: false,
		},
		{
			name: "Got autoru as skipped block; auth valid",
			testCase: prepareTestCase{
				blackboxResponse: &protoanswers.THttpResponse{
					StatusCode: http.StatusOK,
					Content:    []byte(`{"error": "OK", "status": {"value": "VALID"}, "user_ticket": "test_ticket"}`),
				},
				putAuth: &dto.Auth{
					Valid:      true,
					UserTicket: "test_ticket",
				},
				body:             []byte(`{"autoru_div": "test_div"}`),
				skippedBlocks:    []string{"autoru_div"},
				geohelperRequest: &protoanswers.THttpRequest{},
				url:              &testURL,
				wantGeoRequest: &protoanswers.THttpRequest{
					Path:    "http://test.com/smth?skip_blocks=autoru_div",
					Headers: []*protoanswers.THeader{{Name: "x-ya-user-ticket", Value: "test_ticket"}},
				},
				wantDebugGeoRequest: &protoanswers.THttpRequest{
					Path:    "http://test.com?blocks=autoru_div",
					Headers: []*protoanswers.THeader{{Name: "x-ya-user-ticket", Value: "test_ticket"}},
				},
			},
			wantErr: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ctxMock := &mocks.GeohelperContext{}
			initMockByPrepareCase(ctxMock, tt.testCase)

			err := prepare(ctxMock)

			if tt.wantErr {
				require.Error(t, err)
			} else {
				require.NoError(t, err)
			}
		})
	}
}

type prepareTestCase struct {
	blackboxResponse    *protoanswers.THttpResponse
	putAuth             *dto.Auth
	body                []byte
	skippedBlocks       []string
	geohelperRequest    *protoanswers.THttpRequest
	url                 *string
	wantGeoRequest      *protoanswers.THttpRequest
	wantDebugGeoRequest *protoanswers.THttpRequest
}

func initMockByPrepareCase(ctxMock *mocks.GeohelperContext, c prepareTestCase) {
	if c.blackboxResponse != nil {
		ctxMock.On("GetBlackboxResponse").Return(c.blackboxResponse, nil).Once()
	}

	if c.putAuth != nil {
		ctxMock.On("PutAuth", *c.putAuth).Return(nil).Once()
	}

	if c.body != nil {
		ctxMock.On("GetBody").Return(c.body).Once()
	}

	if c.skippedBlocks != nil {
		ctxMock.On("PutSkippedBlocks", c.skippedBlocks).Return(nil).Once()
	}

	if c.geohelperRequest != nil {
		ctxMock.On("GetHTTPAdapterInputRequest").Return(c.geohelperRequest, nil).Once()
	}

	if c.url != nil {
		ctxMock.On("GetURL").Return(*c.url)
	}

	if c.wantGeoRequest != nil {
		ctxMock.On("AddPB", geohelper.ProtoHTTPRequest, c.wantGeoRequest).Return(nil).Once()
	}

	if c.wantDebugGeoRequest != nil {
		ctxMock.On("AddPB", geohelper.DebugURLsHTTPRequest, c.wantDebugGeoRequest).Return(nil).Once()
	}

	ctxMock.On("LogWarn", mock.Anything, mock.Anything).Return()
}

func Test_findSkippedBlocks(t *testing.T) {
	tests := []struct {
		name    string
		body    string
		want    []string
		wantErr bool
	}{
		{
			name: "Got empty json",
			body: "{}",
			want: []string{},
		},
		{
			name: "Got autoru id in json",
			body: `{"autoru_div": "test"}`,
			want: []string{"autoru_div"},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := findSkippedBlocks([]byte(tt.body))

			if tt.wantErr {
				require.Error(t, err)
			} else {
				require.NoError(t, err)
				require.Equal(t, tt.want, got)
			}
		})
	}
}

func Test_fixAuthHeader(t *testing.T) {
	type args struct {
		geohelperRequest *protoanswers.THttpRequest
		auth             dto.Auth
	}
	tests := []struct {
		name string
		args args
		want *protoanswers.THttpRequest
	}{
		{
			name: "No 'User ticket' in header",
			args: args{
				geohelperRequest: &protoanswers.THttpRequest{},
				auth: dto.Auth{
					UserTicket: "test-ticket",
				},
			},
			want: &protoanswers.THttpRequest{
				Headers: []*protoanswers.THeader{{Name: "x-ya-user-ticket", Value: "test-ticket"}},
			},
		},
		{
			name: "Got 'User ticket' in header",
			args: args{
				geohelperRequest: &protoanswers.THttpRequest{
					Headers: []*protoanswers.THeader{{Name: "X-Ya-User-Ticket", Value: "pre-ticket"}},
				},
				auth: dto.Auth{
					UserTicket: "test-ticket",
				},
			},
			want: &protoanswers.THttpRequest{
				Headers: []*protoanswers.THeader{{Name: "X-Ya-User-Ticket", Value: "test-ticket"}},
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			fixAuthHeader(tt.args.geohelperRequest, tt.args.auth)

			require.True(t, helpers.THttpRequestCompare(tt.want, tt.args.geohelperRequest))
		})
	}
}

var testURL = "http://test.com/smth"
