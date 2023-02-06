package uaasproxy

import (
	"bytes"
	"context"
	"encoding/base64"
	"encoding/json"
	"io/ioutil"
	"net/http"
	"net/http/httptest"
	"net/url"
	"testing"

	"github.com/labstack/echo/v4"
	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/passport/backend/uaas_proxy/testutils"
	"a.yandex-team.ru/passport/shared/golibs/logger"
)

var handlerTests = []struct {
	name        string
	queryParams string
	boxes       string
	flags       string
	expected    []interface{}
}{
	{
		"ok",
		"",
		"182998,0,-1",
		b64("[{\"HANDLER\":\"PASSPORT\",\"CONTEXT\":{\"PASSPORT\":{\"flags\":[\"show-subscriptions\"]}}}]"),
		[]interface{}{
			map[string]interface{}{
				"handler": "PASSPORT",
				"test_id": float64(182998),
				"PASSPORT": map[string]interface{}{
					"flags": []interface{}{"show-subscriptions"},
				},
			},
		},
	},
	{
		"no experiments",
		"",
		"",
		"",
		[]interface{}{},
	},
	{
		"nothing new to add",
		"?app_id=unit-tests&am_version=unit-tests",
		"182998,0,-1",
		b64("[{\"HANDLER\":\"PASSPORT\",\"CONTEXT\":{\"PASSPORT\":{\"flags\":[\"hello-unit-tests\"]}}}]"),
		[]interface{}{
			map[string]interface{}{
				"handler": "PASSPORT",
				"test_id": float64(182998),
				"PASSPORT": map[string]interface{}{
					"flags": []interface{}{"hello-unit-tests"},
				},
			},
		},
	},
	{
		"experiments not only in passport",
		"?app_id=unit-tests&am_version=unit-tests",
		"182998,0,-1",
		b64("[{\"HANDLER\":\"PASSPORT\",\"CONTEXT\":{\"NOT_PASSPORT\":{\"flags\":[]}}}]"),
		[]interface{}{
			map[string]interface{}{
				"handler": "PASSPORT",
				"test_id": float64(182998),
				"PASSPORT": map[string]interface{}{
					"flags": []interface{}{},
				},
			},
			map[string]interface{}{
				"handler": "PASSPORT",
				"test_id": float64(-1),
				"PASSPORT": map[string]interface{}{
					"flags": []interface{}{"hello-unit-tests"},
				},
			},
		},
	},
}

func b64(s string) string {
	return base64.StdEncoding.EncodeToString([]byte(s))
}

func assertResponse(t *testing.T, statusCode int, rec *httptest.ResponseRecorder, body map[string]interface{}) {
	assert.Equal(t, statusCode, rec.Code)

	var actual map[string]interface{}
	assert.NotEqual(t, rec.Body.String(), "")
	err := json.Unmarshal(rec.Body.Bytes(), &actual)
	assert.Equal(t, nil, err)
	assert.Equal(t, body, actual)
}

func createApp(mockClient HTTPApiClient) *UaasProxy {
	app := &UaasProxy{
		unistat:    InitUnistat(),
		uaasClient: mockClient,
		logger:     logger.Log(),
	}
	app.InitPools()
	return app
}

func TestUaasHandler(t *testing.T) {
	for _, tt := range handlerTests {
		t.Run(
			tt.name,
			func(t *testing.T) {
				expectedURL := "https://test-domain/passport_am"
				req, err := http.NewRequest("GET", "/uaas"+tt.queryParams, nil)
				if err != nil {
					t.Fatal(err)
				}

				rec := httptest.NewRecorder()
				// мок ответа
				headers := make(http.Header)
				headers.Set("X-Yandex-ExpBoxes", tt.boxes)
				headers.Set("X-Yandex-ExpFlags", tt.flags)

				MockClient := HTTPApiClient{
					Client: testutils.NewTestClient(func(req *http.Request) (*http.Response, error) {
						if req.URL.String() != expectedURL {
							t.Errorf("URL mismatch %s != %s", req.URL.String(), expectedURL)
						}
						return &http.Response{
							StatusCode: http.StatusOK,
							Body:       ioutil.NopCloser(bytes.NewBufferString("USERSPLIT")),
							Header:     headers,
						}, nil
					}),
					BaseURL: "https://test-domain",
				}

				expected := map[string]interface{}{
					"status":      "ok",
					"experiments": tt.expected,
				}

				e := echo.New()
				c := e.NewContext(req, rec)

				app := createApp(MockClient)
				if assert.NoError(t, app.HandlerUaas()(c)) {
					assertResponse(t, http.StatusOK, rec, expected)
				}
			},
		)
	}
}

func TestUaasHandlerCancel(t *testing.T) {
	expectedURL := "https://test-domain/passport_am"
	req, err := http.NewRequest("GET", "/uaas", nil)
	if err != nil {
		t.Fatal(err)
	}

	rec := httptest.NewRecorder()

	MockClient := HTTPApiClient{
		Client: testutils.NewTestClient(func(req *http.Request) (*http.Response, error) {
			if req.URL.String() != expectedURL {
				t.Errorf("URL mismatch %s != %s", req.URL.String(), expectedURL)
			}
			return nil, context.Canceled
		}),
		BaseURL: "https://test-domain",
	}

	expected := map[string]interface{}{
		"status": "error",
		"errors": []interface{}{"backend.uaas_failed"},
	}

	e := echo.New()
	c := e.NewContext(req, rec)

	app := createApp(MockClient)
	if assert.NoError(t, app.HandlerUaas()(c)) {
		assertResponse(t, http.StatusOK, rec, expected)
	}
}

func TestUaasHandler500FromUaas(t *testing.T) {
	expectedURL := "https://test-domain/passport_am"
	req, err := http.NewRequest("GET", "/uaas", nil)
	if err != nil {
		t.Fatal(err)
	}

	rec := httptest.NewRecorder()

	MockClient := HTTPApiClient{
		Client: testutils.NewTestClient(func(req *http.Request) (*http.Response, error) {
			if req.URL.String() != expectedURL {
				t.Errorf("URL mismatch %s != %s", req.URL.String(), expectedURL)
			}
			return &http.Response{
				StatusCode: http.StatusInternalServerError,
				Body:       ioutil.NopCloser(bytes.NewBufferString("")),
				Header:     nil,
			}, nil
		}),
		BaseURL: "https://test-domain",
	}

	expected := map[string]interface{}{
		"status": "error",
		"errors": []interface{}{"backend.uaas_failed"},
	}

	e := echo.New()
	c := e.NewContext(req, rec)

	app := createApp(MockClient)
	if assert.NoError(t, app.HandlerUaas()(c)) {
		assertResponse(t, http.StatusOK, rec, expected)
	}
}

func TestUaasHandlerInvalidForm(t *testing.T) {
	req, err := http.NewRequest("GET", "/uaas?key;value", nil)
	if err != nil {
		t.Fatal(err)
	}

	rec := httptest.NewRecorder()

	expected := map[string]interface{}{
		"status": "error",
		"errors": []interface{}{"form.invalid"},
	}

	e := echo.New()
	c := e.NewContext(req, rec)

	app := createApp(HTTPApiClient{})
	if assert.NoError(t, app.HandlerUaas()(c)) {
		assertResponse(t, http.StatusOK, rec, expected)
	}
}

func TestUaasHandlerInvalidTestIDs(t *testing.T) {
	req, err := http.NewRequest("GET", "/uaas?test_ids=invalid", nil)
	if err != nil {
		t.Fatal(err)
	}

	rec := httptest.NewRecorder()

	expected := map[string]interface{}{
		"status": "error",
		"errors": []interface{}{"test_ids.invalid"},
	}

	e := echo.New()
	c := e.NewContext(req, rec)

	app := createApp(HTTPApiClient{})
	if assert.NoError(t, app.HandlerUaas()(c)) {
		assertResponse(t, http.StatusOK, rec, expected)
	}
}

func TestUaasHandlerInvalidRealIP(t *testing.T) {
	req, err := http.NewRequest("GET", "/uaas?real_ip=invalid", nil)
	if err != nil {
		t.Fatal(err)
	}

	rec := httptest.NewRecorder()

	expected := map[string]interface{}{
		"status": "error",
		"errors": []interface{}{"real_ip.invalid"},
	}

	e := echo.New()
	c := e.NewContext(req, rec)

	app := createApp(HTTPApiClient{})
	if assert.NoError(t, app.HandlerUaas()(c)) {
		assertResponse(t, http.StatusOK, rec, expected)
	}
}

var handlerParamsTests = []struct {
	name        string
	queryParams string
	uaasParams  url.Values
	headers     http.Header
}{
	{
		"default",
		"",
		url.Values{},
		http.Header{},
	},
	{
		"device_id",
		"?device_id=foobar",
		url.Values{"uuid": []string{"foobar"}},
		http.Header{},
	},
	{
		"test_ids",
		"?test_ids=1,2,3",
		url.Values{
			"test-id": []string{"1_2_3"},
		},
		http.Header{"X-Yandex-Uaas": []string{"testing"}},
	},
	{
		"real_ip",
		"?real_ip=127.0.0.1",
		url.Values{},
		http.Header{"X-Forwarded-For-Y": []string{"127.0.0.1"}},
	},
}

func TestUaasHandlerAdditionalParams(t *testing.T) {
	for _, tt := range handlerParamsTests {
		t.Run(
			tt.name,
			func(t *testing.T) {
				req, err := http.NewRequest("GET", "/uaas"+tt.queryParams, nil)
				if err != nil {
					t.Fatal(err)
				}

				rec := httptest.NewRecorder()
				// мок ответа
				headers := make(http.Header)
				headers.Set("X-Yandex-ExpBoxes", "")
				headers.Set("X-Yandex-ExpFlags", "")

				MockClient := HTTPApiClient{
					Client: testutils.NewTestClient(func(req *http.Request) (*http.Response, error) {
						if assert.NoError(t, req.ParseForm()) {
							assert.Equal(t, tt.uaasParams, req.Form)
							assert.Equal(t, tt.headers, req.Header)
						}
						return &http.Response{
							StatusCode: http.StatusOK,
							Body:       ioutil.NopCloser(bytes.NewBufferString("USERSPLIT")),
							Header:     headers,
						}, nil
					}),
					BaseURL: "https://test-domain",
				}

				expected := map[string]interface{}{
					"status":      "ok",
					"experiments": []interface{}{},
				}

				e := echo.New()
				c := e.NewContext(req, rec)

				app := createApp(MockClient)
				if assert.NoError(t, app.HandlerUaas()(c)) {
					assertResponse(t, http.StatusOK, rec, expected)
				}
			},
		)
	}
}
