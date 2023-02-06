package fedcfgclient

import (
	"bytes"
	"io/ioutil"
	"net/http"
	"testing"

	"github.com/golang/mock/gomock"

	"a.yandex-team.ru/library/go/yandex/tvm"
	"a.yandex-team.ru/passport/backend/library/passportapi/mocks/tvm_mock"
)

type RoundTripFunc func(req *http.Request) *http.Response

func (f RoundTripFunc) RoundTrip(req *http.Request) (*http.Response, error) {
	return f(req), nil
}

func NewTestClient(fn RoundTripFunc) *http.Client {
	return &http.Client{
		Transport: fn,
	}
}

func TestResponse(statusCode int, body string) *http.Response {
	return &http.Response{
		StatusCode: statusCode,
		Body:       ioutil.NopCloser(bytes.NewBufferString(body)),
		Header:     make(http.Header),
	}
}

func TestFedCfgClient(t *testing.T, resp *http.Response) *fedCfgClient {
	httpClient := NewTestClient(func(req *http.Request) *http.Response {
		return resp
	})
	ctrl := gomock.NewController(t)
	tvmClient := tvm_mock.NewMockClient(ctrl)
	var tvmID tvm.ClientID = 42
	tvmClient.EXPECT().GetServiceTicketForID(gomock.Any(), tvmID)
	return &fedCfgClient{
		Client:    httpClient,
		TvmClient: tvmClient,
		URL:       "http://localhost/fedcfgapi",
		TVMID:     tvmID,
	}
}
