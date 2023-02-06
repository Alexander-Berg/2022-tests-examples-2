package handlers

import (
	"encoding/json"
	"fmt"
	"net/http"
	"runtime"
	"sort"
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/library/go/core/metrics/solomon"
	"a.yandex-team.ru/passport/infra/daemons/tvmtool/internal/httpclientmock"
	"a.yandex-team.ru/passport/infra/daemons/tvmtool/internal/tvmversion"
)

type testMetricsData struct {
	Metrics []struct {
		Type      string            `json:"type"`
		Labels    map[string]string `json:"labels"`
		Value     float64           `json:"value"`
		Histogram struct {
			Bounds  []float64 `json:"bounds"`
			Buckets []int64   `json:"buckets"`
			Inf     int64     `json:"inf"`
		} `json:"hist"`
	} `json:"metrics"`
}

func TestSolomonMetrics(t *testing.T) {
	solomonOpts := solomon.NewRegistryOpts()
	solomonReg := solomon.NewRegistry(solomonOpts)

	handler := NewSolomonMetricsHandler(solomonReg, nil)

	oldGMP := runtime.GOMAXPROCS(1)
	defer runtime.GOMAXPROCS(oldGMP)

	body, resp := httpclientmock.TestResponseStatus(t, handler,
		httpclientmock.MakeRequest("", nil),
		http.StatusOK,
	)

	assert.Equal(t, "application/json", resp.Header.Get("Content-Type"))

	expectMetrics := fmt.Sprintf(
		`{
	   		"metrics": [
				{
					"type": "DGAUGE",
					"labels": {
					  "sensor": "version",
                      "version": "%s"
					},
					"value": 1.0
				},
				{
					"type": "DGAUGE",
					"labels": {
					  "sensor": "process.goMaxProcs"
					},
					"value": 1.0
				}
 	    	]
		}`,
		tvmversion.GetVersion(),
	)
	assertMetrics(t, expectMetrics, body)
}

func assertMetrics(t *testing.T, expectBody string, givenBody string) {
	var expectedObj, givenObj testMetricsData
	err := json.Unmarshal([]byte(expectBody), &expectedObj)
	assert.NoError(t, err)
	err = json.Unmarshal([]byte(givenBody), &givenObj)
	assert.NoError(t, err)

	sort.Slice(expectedObj.Metrics, func(i, j int) bool {
		return expectedObj.Metrics[i].Labels["sensor"] < expectedObj.Metrics[j].Labels["sensor"]
	})
	sort.Slice(givenObj.Metrics, func(i, j int) bool {
		return givenObj.Metrics[i].Labels["sensor"] < givenObj.Metrics[j].Labels["sensor"]
	})

	assert.EqualValues(t, expectedObj, givenObj)
}
