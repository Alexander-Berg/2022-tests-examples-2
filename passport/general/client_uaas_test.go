package uaasproxy

import (
	"bytes"
	"context"
	"io/ioutil"
	"net/http"
	"testing"

	"github.com/stretchr/testify/assert"
)

const ConstTestExpFlags = "W3siSEFORExFUiI6IlBBU1NQT1JUIiwiQ09OVEVYVCI6eyJQQVNTUE9SVCI6eyJmbGFncyI6WyJzaG93LXN1YnNjcmlwdGlvbnMiXX19fV0=,W3siSEFORExFUiI6IlBBU1NQT1JUIiwiQ09OVEVYVCI6eyJQQVNTUE9SVCI6eyJmbGFncyI6WyJkb21pay1jaGFsbGVuZ2UtZXhwIl19fX1d,W3siSEFORExFUiI6IlBBU1NQT1JUIiwiQ09OVEVYVCI6eyJQQVNTUE9SVCI6eyJmbGFncyI6WyJkb21pay1jaGFsbGVuZ2UtYW0tZXhwIl19fX1d,W3siSEFORExFUiI6ICJQQVNTUE9SVCIsICJDT05URVhUIjogeyJQQVNTUE9SVCI6IHsiZmxhZ3MiOiBbInJlZ19vY3JfZXhwIl19fX1d,W3siSEFORExFUiI6IlBBU1NQT1JUIiwiQ09OVEVYVCI6eyJQQVNTUE9SVCI6eyJmbGFncyI6WyJjbGVhbndlYl9leHBfb24iXX19fV0="

func TestParseUaasBoxes(t *testing.T) {
	input := "182998,0,-1;176965,0,-1;186113,0,-1;65472,0,-1;157721,0,-1"
	actual, _ := parseUaasBoxes(input)
	expected := []int{182998, 176965, 186113, 65472, 157721}
	assert.Equal(t, expected, actual)
}

func TestParseUaasBoxesEmpty(t *testing.T) {
	input := ""
	actual, _ := parseUaasBoxes(input)
	assert.Equal(t, 0, len(actual))
}

func TestParseUaasBoxesMalformed(t *testing.T) {
	input := "foo,bar,zar;foo2,bar2,zar2;"
	actual, _ := parseUaasBoxes(input)
	assert.Equal(t, 0, len(actual))
}

func TestParseUaasSingleFlagBlob(t *testing.T) {
	input := "W3siSEFORExFUiI6IlBBU1NQT1JUIiwiQ09OVEVYVCI6eyJQQVNTUE9SVCI6eyJmbGFncyI6WyJzaG93LXN1YnNjcmlwdGlvbnMiXX19fV0="
	actual, _ := createApp(HTTPApiClient{}).parseUaasSingleFlagPool(input)
	expected := UaasResponseExperiments{{
		Handler: "PASSPORT",
		Context: UaasContext{
			Passport: UaasFlags{
				Flags: []string{"show-subscriptions"},
			},
		},
	}}
	assert.Equal(t, expected, actual)
}

func TestParseUaasFlagsMalformed(t *testing.T) {
	boxes := []int{1}
	input := ConstTestExpFlags

	experiments, _ := createApp(HTTPApiClient{}).parseUaasFlags(boxes, input)
	assert.Equal(t, 0, len(experiments))
}

func TestParseUaasFlagsEmpty(t *testing.T) {
	boxes := []int{1}
	input := ""

	actual, _ := createApp(HTTPApiClient{}).parseUaasFlags(boxes, input)
	var expected []Experiment
	assert.Equal(t, expected, actual)
}

func TestParseUaasFlags(t *testing.T) {
	boxes := []int{1, 2, 3, 4, 5}
	input := ConstTestExpFlags
	actual, _ := createApp(HTTPApiClient{}).parseUaasFlags(boxes, input)
	expected := []Experiment{
		{
			Handler: "PASSPORT",
			TestID:  1,
			Context: UaasContext{
				Passport: UaasFlags{
					Flags: []string{"show-subscriptions"},
				},
			},
		},
		{
			Handler: "PASSPORT",
			TestID:  2,
			Context: UaasContext{
				Passport: UaasFlags{
					Flags: []string{"domik-challenge-exp"},
				},
			},
		},
		{
			Handler: "PASSPORT",
			TestID:  3,
			Context: UaasContext{
				Passport: UaasFlags{
					Flags: []string{"domik-challenge-am-exp"},
				},
			},
		},
		{
			Handler: "PASSPORT",
			TestID:  4,
			Context: UaasContext{
				Passport: UaasFlags{
					Flags: []string{"reg_ocr_exp"},
				},
			},
		},
		{
			Handler: "PASSPORT",
			TestID:  5,
			Context: UaasContext{
				Passport: UaasFlags{
					Flags: []string{"cleanweb_exp_on"},
				},
			},
		},
	}
	assert.Equal(t, expected, actual)
}

func TestParseUaasResponse(t *testing.T) {
	expectedURL := "https://test-domain/config"
	headers := make(http.Header)
	headers.Set("X-Yandex-ExpBoxes", "182998,0,-1;176965,0,-1")
	headers.Set("X-Yandex-ExpFlags", "W3siSEFORExFUiI6IlBBU1NQT1JUIiwiQ09OVEVYVCI6eyJQQVNTUE9SVCI6eyJmbGFncyI6WyJzaG93LXN1YnNjcmlwdGlvbnMiXX19fV0=,W3siSEFORExFUiI6IlBBU1NQT1JUIiwiQ09OVEVYVCI6eyJQQVNTUE9SVCI6eyJmbGFncyI6WyJkb21pay1jaGFsbGVuZ2UtZXhwIl19fX1d")

	MockClient := HTTPApiClient{
		Client: NewTestClient(func(req *http.Request) (*http.Response, error) {
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
	actual, _ := createApp(HTTPApiClient{}).QueryUaas(context.Background(), &MockClient, "config", UaasEnvData{})
	expected := ExperimentData{
		Experiments: []Experiment{
			{
				Handler: "PASSPORT",
				TestID:  182998,
				Context: UaasContext{
					Passport: UaasFlags{
						Flags: []string{"show-subscriptions"},
					},
				},
			},
			{
				Handler: "PASSPORT",
				TestID:  176965,
				Context: UaasContext{
					Passport: UaasFlags{
						Flags: []string{"domik-challenge-exp"},
					},
				},
			},
		},
	}
	assert.Equal(t, expected, actual)
}
