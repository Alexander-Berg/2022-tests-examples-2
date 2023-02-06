package httpcache

import (
	"bytes"
	"context"
	"io/ioutil"
	"net/http"
	"net/url"
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func Test_rereader(t *testing.T) {
	testCases := []struct {
		name    string
		content string
	}{
		{
			name:    "variant 1",
			content: "asdasdasdasd",
		},
		{
			name:    "variant 2",
			content: "sdasdasdasda",
		},
	}
	for _, testCase := range testCases {
		t.Run(testCase.name, func(t *testing.T) {
			reader := bytes.NewReader([]byte(testCase.content))
			rereader, err := newRereader(reader)
			require.NoError(t, err)
			result1, err := ioutil.ReadAll(rereader)
			require.NoError(t, err)
			err = rereader.Close()
			require.NoError(t, err)
			result2, err := ioutil.ReadAll(rereader)
			require.NoError(t, err)
			assert.Equal(t, result1, result2)
		})
	}
}

func Test_keyReducer(t *testing.T) {
	testCases := []struct {
		name        string
		request     *http.Request
		expectedKey innerKey
	}{
		{
			name: "variant 1",
			request: &http.Request{
				Header: http.Header{
					requestIDHeader: []string{"abc"},
					urlHeader:       []string{"https://yandex.ru/123?a=1&b=2&"},
				},
			},
			expectedKey: innerKey{
				requestID: "abc",
				url:       "https://yandex.ru/123?a=1&b=2",
			},
		},
		{
			name: "variant 2",
			request: &http.Request{
				Header: http.Header{
					requestIDHeader: []string{"123"},
					urlHeader:       []string{"https://yandex.ru/?c=1&b=2"},
				},
			},
			expectedKey: innerKey{
				requestID: "123",
				url:       "https://yandex.ru/?b=2&c=1",
			},
		},
	}
	for _, testCase := range testCases {
		t.Run(testCase.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			logCtx := NewMocklogCtx(ctrl)
			assert.Equal(t, testCase.expectedKey, newKeyReducer().ReduceKey(testCase.request, logCtx))
		})
	}
}

type transportForValueRetriever struct {
	t            *testing.T
	expectMethod string
	expectURL    string
	expectHeader http.Header
	expectHost   string
	expectBody   string
	returnBody   string
}

func (t *transportForValueRetriever) RoundTrip(r *http.Request) (*http.Response, error) {
	assert.Equal(t.t, t.expectMethod, r.Method)
	assert.Equal(t.t, t.expectURL, r.URL.String())
	assert.Equal(t.t, t.expectHeader, r.Header)
	assert.Equal(t.t, t.expectHost, r.Host)
	body, err := ioutil.ReadAll(r.Body)
	require.NoError(t.t, err)
	assert.Equal(t.t, t.expectBody, string(body))
	return &http.Response{
		Body: ioutil.NopCloser(bytes.NewReader([]byte(t.returnBody))),
	}, nil
}

func Test_valueRetriever(t *testing.T) {
	testCases := []struct {
		name                string
		request             *http.Request
		requestURL          string
		requestBodyContent  string
		expectURL           string
		expectHeader        http.Header
		expectHost          string
		responseBodyContent string
	}{
		{
			name: "get request",
			request: &http.Request{
				Method: "GET",
				Header: http.Header{
					requestIDHeader:       []string{"123"},
					urlHeader:             []string{"http://yandex.ru"},
					hostHeader:            []string{"anything"},
					"random-other-header": []string{"asd", "dsa"},
				},
			},
			requestURL:         "http://not.yandex.ru",
			requestBodyContent: "somebody once told me",
			expectURL:          "http://yandex.ru",
			expectHeader: http.Header{
				requestIDHeader:       []string{"123"},
				"random-other-header": []string{"asd", "dsa"},
			},
			expectHost:          "anything",
			responseBodyContent: "that world is gonna roll me",
		},
		{
			name: "put request",
			request: &http.Request{
				Method: "PUT",
				Header: http.Header{
					requestIDHeader: []string{"123asdasd"},
					urlHeader:       []string{"https://yabs.yandex.ru"},
					hostHeader:      []string{"something"},
				},
			},
			requestURL:         "http://localhost:80",
			requestBodyContent: "abc",
			expectURL:          "https://yabs.yandex.ru",
			expectHeader: http.Header{
				requestIDHeader: []string{"123asdasd"},
			},
			expectHost:          "something",
			responseBodyContent: "cda",
		},
	}

	for _, testCase := range testCases {
		t.Run(testCase.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			logCtx := NewMocklogCtx(ctrl)
			logCtx.EXPECT().AddOutgoingRequest(gomock.Any()).Return()
			logCtx.EXPECT().AddIncomingResponse(gomock.Any(), gomock.Any()).Return()
			transport := &transportForValueRetriever{
				t:            t,
				expectMethod: testCase.request.Method,
				expectURL:    testCase.expectURL,
				expectHeader: testCase.expectHeader,
				expectHost:   testCase.expectHost,
				expectBody:   testCase.requestBodyContent,
				returnBody:   testCase.responseBodyContent,
			}
			client := &http.Client{
				Transport: transport,
			}
			var err error
			testCase.request.URL, err = url.Parse(testCase.requestURL)
			require.NoError(t, err)
			testCase.request.Body = ioutil.NopCloser(bytes.NewReader([]byte(testCase.requestBodyContent)))

			valueRetriever := newValueRetriever(client, testCase.request, logCtx)
			response, err := valueRetriever.Retrieve(context.Background())
			require.NoError(t, err)
			body, err := ioutil.ReadAll(response.Body)
			require.NoError(t, err)
			assert.Equal(t, testCase.responseBodyContent, string(body))
		})
	}
}
