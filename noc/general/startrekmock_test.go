package startrekmock

import (
	"net/http"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestServer(t *testing.T) {
	ts := NewServer()
	defer ts.Close()

	res, err := http.Get(ts.URL + "/non/existent")
	assert.NoError(t, err)
	defer func() {
		err := res.Body.Close()
		if err != nil {
			t.Fatal(err)
		}
	}()

	assert.Equal(t, res.StatusCode, 404)
}
