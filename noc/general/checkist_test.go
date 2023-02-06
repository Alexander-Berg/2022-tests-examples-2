package checkist

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"net/http/httptest"
	"os"
	"path"
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/library/go/test/yatest"
	"a.yandex-team.ru/noc/nalivkin/internal/resource"
)

var testDataPath = yatest.SourcePath("noc/nalivkin/internal/client/checkist/testdata")

type testData struct {
	FileName         string
	CheckistResponse interface{}
	Result           resource.Patch
}

func TestClientGetPatch(t *testing.T) {
	tds, err := readTestData("*-TestClientGetPatch.json")
	if err != nil {
		log.Fatal(err)
	}
	for _, td := range tds {
		t.Run(td.FileName, func(t *testing.T) {
			if err != nil {
				log.Fatal(err)
			}
			serv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				_ = json.NewEncoder(w).Encode(td.CheckistResponse)
			}))
			defer serv.Close()
			checkist := Client{
				httpClient: &http.Client{},
				baseURL:    serv.URL,
			}
			ctx := context.Background()
			resp, err := checkist.GetPatch(ctx, 1, "", true, "", nil, nil)
			if err != nil {
				log.Fatal(err)
			}
			assert.Equal(t, td.Result, resp)
		})
	}
}

func TestClientGetNalivkaUnexpectedResponse(t *testing.T) {
	var responseMap string
	serv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		_, err := w.Write([]byte(responseMap))
		if err != nil {
			log.Fatal("Failed to respond")
		}
	}))
	defer serv.Close()
	checkist := Client{
		httpClient: &http.Client{},
		baseURL:    serv.URL,
	}
	ctx := context.Background()
	var err error
	responseMap = `Not Json`
	_, err = checkist.GetPatch(ctx, 1, "", true, "", nil, nil)
	assert.Error(t, err, "not failed on invalid json")

	responseMap = `{"field1": "val1"}`
	_, err = checkist.GetPatch(ctx, 1, "", true, "", nil, nil)
	assert.Error(t, err, "not failed even without '' field")

	responseMap = `{}`
	_, err = checkist.GetPatch(ctx, 1, "", true, "", nil, nil)
	assert.Error(t, err, "checkist returned empty diff for device 1")
}

func readTestData(glob string) ([]testData, error) {
	ret := make([]testData, 0)
	files, err := filepath.Glob(path.Join(testDataPath, glob))
	if err != nil {
		return ret, nil
	}
	if len(files) == 0 {
		return ret, fmt.Errorf("no files found in '%s'", testDataPath)
	}
	for _, f := range files {
		data, err := os.ReadFile(f)
		var td testData
		if err != nil {
			return ret, err
		}
		if err := json.Unmarshal(data, &td); err != nil {
			return ret, err
		}
		td.FileName = path.Base(f)
		ret = append(ret, td)
	}
	return ret, nil
}
