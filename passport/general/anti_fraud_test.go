package fraud

import (
	"bytes"
	"context"
	"encoding/json"
	"io"
	"io/ioutil"
	"net"
	"net/http"
	"testing"
	"time"

	"github.com/golang/mock/gomock"
	"github.com/jarcoal/httpmock"
	"github.com/stretchr/testify/require"

	mock_tvm "a.yandex-team.ru/library/go/yandex/tvm/mocks"
)

type testCase struct {
	request  AntiFraudRequest
	response AntiFraudResponse
}

func compareRequests(a *AntiFraudRequest, b *AntiFraudRequest) bool {
	if a == nil || b == nil {
		return a == b
	}

	return a.UserPhone == b.UserPhone && a.UserIP == b.UserIP && a.Timestamp == b.Timestamp && a.Service == b.Service && a.Scenario == b.Scenario && a.RequestPath == b.RequestPath && a.UID == b.UID && a.UserAgent == b.UserAgent && a.DeviceID == b.DeviceID
}

func newAntiFraudResponder(t *testing.T) httpmock.Responder {
	tests := []testCase{
		{
			request: AntiFraudRequest{
				Timestamp: 1640998861000,
			},
			response: AntiFraudResponse{
				Action: AntiFraudActionAllow,
			},
		},
		{
			request: AntiFraudRequest{
				Timestamp: 1671625272000,
				UserIP:    "192.168.1.1",
				UserPhone: "+12345678",
			},
			response: AntiFraudResponse{
				Action: "DENY",
			},
		},
		{
			request: AntiFraudRequest{
				Timestamp: 1671625272000,
				UserIP:    "192.168.1.1",
				UserPhone: "+987654321",
			},
			response: AntiFraudResponse{
				Action: AntiFraudActionAllow,
			},
		},
		{
			request: AntiFraudRequest{
				Timestamp: 1671625272000,
				UserIP:    "192.168.1.1",
				UserPhone: "+987654321",
			},
			response: AntiFraudResponse{
				Action: AntiFraudActionAllow,
			},
		},
		{
			request: AntiFraudRequest{
				Timestamp:   58612087000,
				UserIP:      "2001:db8:3333:4444:5555:6666:102:304",
				UserPhone:   "+987654321",
				Service:     "some_service",
				Scenario:    "some_scenario",
				RequestPath: "/2/bundle/phone/confirm_and_bind_secure/submit/",
				UID:         100500,
				UserAgent:   "firefox",
				DeviceID:    "sdf79273f9g8ew7fh0q83",
			},
			response: AntiFraudResponse{
				Action: "DENY",
			},
		},
	}

	return func(req *http.Request) (*http.Response, error) {
		body, err := ioutil.ReadAll(req.Body)
		require.NoError(t, err)

		request := AntiFraudRequest{}
		err = json.Unmarshal(body, &request)
		require.NoError(t, err)

		var response *AntiFraudResponse

		for _, test := range tests {
			if compareRequests(&request, &test.request) {
				response = &test.response
				break
			}
		}

		if response == nil {
			return &http.Response{
				StatusCode: 400,
			}, nil
		}

		body, err = json.Marshal(response)
		require.NoError(t, err)
		return &http.Response{
			StatusCode: 200,
			Body:       io.NopCloser(bytes.NewReader(body)),
		}, nil
	}
}

func withTestFraud(t *testing.T, callback func(antiFraud *AntiFraudChecker)) {
	tvmMock := mock_tvm.NewMockClient(gomock.NewController(t))
	checker, err := NewAntiFraudChecker(&AntiFraudConfig{
		Host: "https://antifraud-so.yandex.net",
		Port: 443,
	}, tvmMock)
	require.NoError(t, err)

	tvmMock.EXPECT().GetServiceTicketForAlias(context.Background(), gomock.Eq("antifraud")).Return("ticket", nil).AnyTimes()

	httpmock.ActivateNonDefault(checker.httpClient.GetClient())
	defer httpmock.DeactivateAndReset()

	httpmock.RegisterResponder("POST", "https://antifraud-so.yandex.net:443/score", newAntiFraudResponder(t))
	callback(checker)
}

func TestAntiFraudChecker_CheckFraudStatus(t *testing.T) {
	withTestFraud(t, func(checker *AntiFraudChecker) {
		response, retry, err := checker.CheckFraudStatus(Metadata{
			Timestamp: time.Date(2022, 01, 01, 01, 01, 01, 0, time.UTC),
		})
		require.NoError(t, err)
		require.NotNil(t, response)
		require.Nil(t, retry)
		require.Equal(t, AntiFraudActionAllow, response.Action)

		response, retry, err = checker.CheckFraudStatus(Metadata{
			Timestamp: time.Date(2022, 12, 21, 12, 21, 12, 0, time.UTC),
			UserIP:    net.IPv4(192, 168, 1, 1),
			UserPhone: "+12345678",
		})
		require.NoError(t, err)
		require.NotNil(t, response)
		require.Nil(t, retry)
		require.Equal(t, AntiFraudActionDeny, response.Action)

		response, retry, err = checker.CheckFraudStatus(Metadata{
			Timestamp: time.Date(2022, 12, 21, 12, 21, 12, 0, time.UTC),
			UserIP:    net.IPv4(192, 168, 1, 1),
			UserPhone: "+987654321",
		})
		require.NoError(t, err)
		require.NotNil(t, response)
		require.Nil(t, retry)
		require.Equal(t, AntiFraudActionAllow, response.Action)

		response, retry, err = checker.CheckFraudStatus(Metadata{
			Timestamp:   time.Date(1971, 11, 10, 9, 8, 7, 0, time.UTC),
			UserIP:      net.ParseIP("2001:db8:3333:4444:5555:6666:1.2.3.4"),
			UserPhone:   "+987654321",
			Service:     "some_service",
			Scenario:    "some_scenario",
			RequestPath: "/2/bundle/phone/confirm_and_bind_secure/submit/",
			UID:         100500,
			UserAgent:   "firefox",
			DeviceID:    "sdf79273f9g8ew7fh0q83",
		})
		require.NoError(t, err)
		require.NotNil(t, response)
		require.Nil(t, retry)
		require.Equal(t, AntiFraudActionDeny, response.Action)
	})
}

func TestAntiFraudChecker_CheckParseAntiFraudDelay(t *testing.T) {
	check := func(i int, data string, expected *AntiFraudRetry) {
		response := &AntiFraudResponse{}
		err := json.Unmarshal([]byte(data), response)
		if err != nil {
			t.Errorf("json-%d parse error: %s", i, err)
			return
		}

		actual := parseAntiFraudRetry(response.Tags)
		if expected == nil && actual != nil {
			t.Errorf("parseAntiFraudRetry error expected: nil, actual: %v", actual)
		} else if expected != nil && actual == nil {
			t.Errorf("parseAntiFraudRetry error expected: %v, actual: nil", expected)
		} else if expected != nil && *expected != *actual {
			t.Errorf("parseAntiFraudRetry error expected %v, actual: %v", expected, actual)
		}
	}

	nildata := []string{
		`{ "one": 1 }`,
		`{ "tags": [] }`,
		`{ "tags": [
			{ "one": 1 }
		] }`,
		`{ "tags": [
			{ "one": 1 },
			{
				"type": "delay"
			}
		] }`,
		`{ "tags": [
			{ "one": 1 },
			{
				"type": "delay",
				"data": {
					"retry": 1
				}
			}
		] }`,
		`{ "tags": [
			{ "one": 1 },
			{
				"type": "delay",
				"data": {
					"retry": 1,
					"delay": "two"
				}
			}
		] }`,
	}

	for i, data := range nildata {
		check(i, data, nil)
	}

	data := `{ "tags": [
		"kek",
		{ "one": 1 },
		{
			"type": "retry",
			"data": {
				"count": 42,
				"delay": 24
			}
		}
	] }`

	check(1000, data, &AntiFraudRetry{
		Delay: time.Duration(24) * time.Millisecond,
		Count: 42,
	})
}

func TestAntiFraudChecker_CheckPrettifyReason(t *testing.T) {
	reason := "aaa\nbbb\nccc"
	for i := 0; i <= 12; i++ {
		pretty := prettifyReason(reason, i)
		if i <= 2 {
			require.Equal(t, "", pretty)
		} else if i <= 6 {
			require.Equal(t, "aaa", pretty)
		} else if i <= 10 {
			require.Equal(t, "aaa bbb", pretty)
		} else {
			require.Equal(t, "aaa bbb ccc", pretty)
		}
	}
	require.Equal(t, "aaa bbb ccc", prettifyReason(reason, 100500))

	reason = ""
	require.Equal(t, "", prettifyReason(reason, 0))
	require.Equal(t, "", prettifyReason(reason, 100500))

	reason = "\n\na\n\n"
	for i := 0; i <= len(reason)+1; i++ {
		_ = prettifyReason(reason, i)
	}
	require.True(t, true)
}
