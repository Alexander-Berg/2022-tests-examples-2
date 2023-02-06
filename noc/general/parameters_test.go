package mur_test

import (
	"bytes"
	"context"
	"net/http"
	"net/http/httptest"
	"net/url"
	"testing"

	"github.com/go-chi/chi/v5"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/ptr"
	"a.yandex-team.ru/noc/cmdb/pkg/mur"
	"a.yandex-team.ru/strm/common/go/pkg/xnet/xhttp/xmiddleware"
)

type Int64Alias int64
type StringAlias string

type Parameters struct {
	Query Query
	Body  Body
}

type Body struct {
	Key string `json:"key"`
}

type Query struct {
	Int64       int64       `mur:"int64"`
	Int64Ptr    *int64      `mur:"int64_ptr"`
	Int64Alias  Int64Alias  `mur:"int64_alias"`
	String      string      `mur:"string"`
	StringAlias StringAlias `mur:"string_alias"`
}

func TestFillParameters(t *testing.T) {
	buffer := bytes.NewBuffer([]byte("{\"key\":\"value\"}"))
	r, err := http.NewRequest("GET", "/users", buffer)
	require.NoError(t, err)
	r.URL.RawQuery = url.Values{
		"int64":        []string{"19"},
		"int64_ptr":    []string{"13"},
		"int64_alias":  []string{"11"},
		"string":       []string{"abc"},
		"string_alias": []string{"def"},
	}.Encode()
	r = WithMiddleware(r, xmiddleware.Arguments)

	var params Parameters
	require.NoError(t, mur.Parameters{
		Path: func(ctx context.Context, s string) *string {
			return ptr.String(chi.URLParamFromCtx(ctx, s))
		},
		Query: func(ctx context.Context, s string) *string {
			return xmiddleware.Args.String(s)(ctx)
		},
		Body: mur.DecodeJSON,
	}.Fill(&params, r))
	require.Equal(t, Parameters{
		Query: Query{
			Int64:       19,
			Int64Ptr:    ptr.Int64(13),
			Int64Alias:  11,
			String:      "abc",
			StringAlias: "def",
		},
		Body: Body{Key: "value"},
	}, params)
}

func WithMiddleware(request *http.Request, middleware func(next http.Handler) http.Handler) (result *http.Request) {
	middleware(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		result = r
	})).ServeHTTP(httptest.NewRecorder(), request)
	return
}
