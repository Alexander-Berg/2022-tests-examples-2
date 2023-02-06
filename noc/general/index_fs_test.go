package ebn

import (
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/stretchr/testify/require"
)

func Test_IndexFS_Open_dir(t *testing.T) {
	fs := indexFS{http.Dir("./web")}
	f, err := fs.Open("static")
	require.NoError(t, err)
	s, err := f.Stat()
	require.NoError(t, err)
	require.Equal(t, true, s.IsDir())
	require.Equal(t, "web", s.Name())
	err = f.Close()
	require.NoError(t, err)
}

func Test_IndexFS_Open_file(t *testing.T) {
	fs := indexFS{http.Dir("./web")}
	f, err := fs.Open("static/test.txt")
	require.NoError(t, err)
	p := make([]byte, 1)
	n, err := f.Read(p)
	require.NoError(t, err)
	require.Equal(t, 1, n)
	require.Equal(t, []byte(`2`), p)
	err = f.Close()
	require.NoError(t, err)
}

func Test_IndexFS_Open_no_file(t *testing.T) {
	fs := indexFS{http.Dir("./web")}
	f, err := fs.Open("static/test2.txt")
	require.NoError(t, err)
	p := make([]byte, 1)
	n, err := f.Read(p)
	require.NoError(t, err)
	require.Equal(t, 1, n)
	require.Equal(t, []byte(`1`), p)
	err = f.Close()
	require.NoError(t, err)
}

func Test_IndexFS_request_index(t *testing.T) {
	r := httptest.NewRequest("GET", "/", nil)
	w := httptest.NewRecorder()
	h := http.FileServer(indexFS{http.Dir("./web")})
	h.ServeHTTP(w, r)
	require.Equal(t, "1\n", w.Body.String())
	require.Equal(t, 200, w.Code)
}
