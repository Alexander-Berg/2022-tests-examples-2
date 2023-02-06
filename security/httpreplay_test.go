package httpreplay_test

import (
	"context"
	"fmt"
	"io"
	"net/http"
	"net/http/httptest"
	"net/url"
	"testing"

	"github.com/go-chi/chi/v5"
	"github.com/go-resty/resty/v2"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/core/log"
	"a.yandex-team.ru/library/go/core/log/zap"
	"a.yandex-team.ru/security/libs/go/boombox/httpmodel"
	"a.yandex-team.ru/security/libs/go/boombox/httpreplay"
	"a.yandex-team.ru/security/libs/go/boombox/tape"
)

func NewTestServer() *httptest.Server {
	r := chi.NewMux()

	r.NotFound(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusNotFound)
		_, _ = w.Write([]byte("404"))
	})

	r.Get("/static", func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		_, _ = w.Write([]byte("static page"))
	})

	r.Get("/query", func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		_, _ = w.Write([]byte(r.URL.Query().Encode()))
	})

	r.Post("/post", func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		_, _ = io.Copy(w, r.Body)
		_ = r.Body.Close()
	})

	r.HandleFunc("/scheme", func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusCreated)
		_, _ = w.Write([]byte(r.Method))
	})

	r.HandleFunc("/redirect", func(w http.ResponseWriter, r *http.Request) {
		http.Redirect(w, r, "/static", http.StatusTemporaryRedirect)
	})

	return httptest.NewServer(r)
}

func TestRecorder(t *testing.T) {
	type testCase struct {
		newReq func(httpc *resty.Client) *resty.Request
		verify func(t *testing.T, rsp *resty.Response, err error)
		opts   []httpreplay.Option
	}

	cases := []testCase{
		{
			newReq: func(httpc *resty.Client) *resty.Request {
				r := httpc.R()
				r.Method = http.MethodGet
				r.URL = "/static"
				return r
			},
			verify: func(t *testing.T, rsp *resty.Response, err error) {
				require.NoError(t, err)
				require.Equal(t, http.StatusOK, rsp.StatusCode())
				require.Equal(t, []byte("static page"), rsp.Body())
			},
		},
		{
			newReq: func(httpc *resty.Client) *resty.Request {
				r := httpc.R().
					SetQueryParams(map[string]string{
						"lol":      "kek",
						"cherubek": "bear",
					})
				r.Method = http.MethodGet
				r.URL = "/query"
				return r
			},
			verify: func(t *testing.T, rsp *resty.Response, err error) {
				require.NoError(t, err)
				require.Equal(t, http.StatusOK, rsp.StatusCode())
				require.Equal(t, []byte(rsp.Request.QueryParam.Encode()), rsp.Body())
			},
		},
		{
			newReq: func(httpc *resty.Client) *resty.Request {
				r := httpc.R()
				r.Method = http.MethodOptions
				r.URL = "/scheme"
				return r
			},
			verify: func(t *testing.T, rsp *resty.Response, err error) {
				require.NoError(t, err)
				require.Equal(t, http.StatusCreated, rsp.StatusCode())
				require.Equal(t, []byte(http.MethodOptions), rsp.Body())
			},
		},
		{
			newReq: func(httpc *resty.Client) *resty.Request {
				r := httpc.R()
				r.Method = http.MethodPatch
				r.URL = "/scheme"
				return r
			},
			verify: func(t *testing.T, rsp *resty.Response, err error) {
				require.NoError(t, err)
				require.Equal(t, http.StatusCreated, rsp.StatusCode())
				require.Equal(t, []byte(http.MethodPatch), rsp.Body())
			},
		},
		{
			newReq: func(httpc *resty.Client) *resty.Request {
				r := httpc.R()
				r.Method = http.MethodHead
				r.URL = "/scheme"
				return r
			},
			verify: func(t *testing.T, rsp *resty.Response, err error) {
				require.NoError(t, err)
				require.Equal(t, http.StatusCreated, rsp.StatusCode())
				require.Empty(t, rsp.Body())
			},
		},
		{
			newReq: func(httpc *resty.Client) *resty.Request {
				r := httpc.R()
				r.URL = "/redirect"
				return r
			},
			verify: func(t *testing.T, rsp *resty.Response, err error) {
				require.Error(t, err)
				urlErr, ok := err.(*url.Error)
				require.True(t, ok, "must be url.Error")
				require.Equal(t, "/static", urlErr.URL)
			},
			opts: []httpreplay.Option{
				httpreplay.WithFollowRedirect(false),
				httpreplay.WithNamespace("bar"),
			},
		},
		{
			newReq: func(httpc *resty.Client) *resty.Request {
				r := httpc.R()
				r.URL = "/redirect"
				return r
			},
			verify: func(t *testing.T, rsp *resty.Response, err error) {
				require.NoError(t, err)
				require.Equal(t, http.StatusOK, rsp.StatusCode())
				require.Equal(t, []byte("static page"), rsp.Body())
			},
			opts: []httpreplay.Option{
				httpreplay.WithFollowRedirect(true),
				httpreplay.WithNamespace("foo"),
			},
		},
		{
			newReq: func(httpc *resty.Client) *resty.Request {
				r := httpc.R()
				r.URL = "/lol/kek/cheburek"
				return r
			},
			verify: func(t *testing.T, rsp *resty.Response, err error) {
				require.NoError(t, err)
				require.Equal(t, http.StatusNotFound, rsp.StatusCode())
				require.Equal(t, []byte("404"), rsp.Body())
			},
		},
	}

	doTest := func(t *testing.T, testTape *tape.Tape, opts ...httpreplay.Option) {
		for i, tc := range cases {
			t.Run(fmt.Sprint(i), func(t *testing.T) {
				recorder, err := httpreplay.NewReplay(testTape, append(opts, tc.opts...)...)
				require.NoError(t, err)

				httpc := resty.New().
					SetBaseURL(recorder.TestURL()).
					SetRedirectPolicy(resty.NoRedirectPolicy())
				req := tc.newReq(httpc)
				t.Run(req.URL, func(t *testing.T) {
					rsp, err := req.Send()
					tc.verify(t, rsp, err)
				})
				err = recorder.Shutdown(context.Background())
				require.NoError(t, err)
			})
		}
	}

	tapePath := "recorder.bolt"
	recorderOpts := []httpreplay.Option{
		httpreplay.WithLogger(zap.Must(zap.ConsoleConfig(log.DebugLevel))),
	}

	t.Run("record", func(t *testing.T) {
		testTape, err := tape.NewTape(tapePath)
		require.NoError(t, err)

		testSrv := NewTestServer()
		defer testSrv.Close()

		doTest(t, testTape, append(recorderOpts, httpreplay.WithProxyMode(testSrv.URL))...)

		err = testTape.Close()
		require.NoError(t, err)
	})

	t.Run("reply", func(t *testing.T) {
		testTape, err := tape.NewTape(tapePath, tape.WithReadOnly())
		require.NoError(t, err)

		doTest(t, testTape, recorderOpts...)

		err = testTape.Close()
		require.NoError(t, err)
	})
}

func TestRecorder_keyFunc(t *testing.T) {
	type testCase struct {
		keyFunc     httpreplay.KeyFunc
		expectedKey string
	}

	cases := []testCase{
		{
			keyFunc: func(r *httpmodel.Request) string {
				return "custom-key"
			},
			expectedKey: "custom-key",
		},
		{
			keyFunc:     httpreplay.DefaultKeyFunc,
			expectedKey: "POST@/post",
		},
		{
			keyFunc:     httpreplay.BodyKeyFunc,
			expectedKey: "POST@5116c28e651a19013822c09e5c70c9fc425a66dc@/post",
		},
	}

	doTest := func(t *testing.T, testTape *tape.Tape, opts ...httpreplay.Option) {
		for _, tc := range cases {
			t.Run(tc.expectedKey, func(t *testing.T) {
				recorder, err := httpreplay.NewReplay(testTape, append(opts, httpreplay.WithKeyFunc(tc.keyFunc))...)
				require.NoError(t, err)

				body := []byte(`kek`)
				httpRsp, err := resty.New().
					SetBaseURL(recorder.TestURL()).
					R().
					SetBody(body).
					Post("/post")
				require.NoError(t, err)
				require.Equal(t, http.StatusOK, httpRsp.StatusCode())
				require.Equal(t, body, httpRsp.Body())

				rsp, err := testTape.GetHTTPResponse(httpreplay.DefaultNamespace, tc.expectedKey)
				require.NoError(t, err)
				require.Equal(t, http.StatusOK, int(rsp.StatusCode))
				require.Equal(t, body, rsp.Body)

				err = recorder.Shutdown(context.Background())
				require.NoError(t, err)
			})
		}
	}

	tapePath := "recorder.bolt"
	recorderOpts := []httpreplay.Option{
		httpreplay.WithLogger(zap.Must(zap.ConsoleConfig(log.DebugLevel))),
	}

	t.Run("record", func(t *testing.T) {
		testTape, err := tape.NewTape(tapePath)
		require.NoError(t, err)

		testSrv := NewTestServer()
		defer testSrv.Close()

		doTest(t, testTape, append(recorderOpts, httpreplay.WithProxyMode(testSrv.URL))...)

		err = testTape.Close()
		require.NoError(t, err)
	})

	t.Run("reply", func(t *testing.T) {
		testTape, err := tape.NewTape(tapePath, tape.WithReadOnly())
		require.NoError(t, err)

		doTest(t, testTape, recorderOpts...)

		err = testTape.Close()
		require.NoError(t, err)
	})
}
