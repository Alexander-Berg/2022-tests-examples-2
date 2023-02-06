package hbaseapi

import (
	"context"
	"encoding/json"
	"testing"

	"github.com/jarcoal/httpmock"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/passport/infra/daemons/historydb_api2/internal/reqs"
)

func TestClient_GetAuths(t *testing.T) {
	expectedBody := `{
		"status": "ok",
		"uid":    123,
		"auths": [
			{
				"type": "oauthcheck",
				"comment": "some_comment",
				"status": "successful",
				"host_id": "127",
				"client_name": "bb",
				"user_ip": "0.0.0.0",
				"timestamp": 1397559039.239351
			},
			{
				"type": "oauthcheck",
				"comment": "comment",
				"status": "successful",
				"host_id": "127",
				"client_name": "bb",
				"user_ip": "127.0.0.1",
				"timestamp": 1397559038.968003
			}
		]
	}`

	httpmock.RegisterResponder(
		"GET",
		"http://localhost:8201/2/auths/",
		newTestQueryHandler(expectedBody, map[string]string{
			"consumer":    "me, mario",
			"uid":         "123",
			"from_ts":     "160011",
			"to_ts":       "160050",
			"order_by":    "asc",
			"limit":       "1000",
			"status":      "some_status,some_other_status",
			"type":        "some_type,some_other_type",
			"client_name": "some_name,some_other_name",
		}),
	)

	actualResponse, err := testClient.GetAuths(context.Background(), &reqs.AuthsRequest{
		UID:        123,
		FromTS:     160011,
		ToTS:       160101,
		OrderBy:    reqs.OrderByAsc,
		Limit:      1000,
		Status:     []string{"some_status", "some_other_status"},
		Type:       []string{"some_type", "some_other_type"},
		ClientName: []string{"some_name", "some_other_name"},
	}, false, 160051)
	require.NoError(t, err)

	jsonResponse, err := json.Marshal(actualResponse)
	require.NoError(t, err)
	require.JSONEq(t, expectedBody, string(jsonResponse))
}

func TestClient_GetAuthsAggregated(t *testing.T) {
	expectedBody := `{
		"status": "ok",
		"uid": 4000886691,
		"next": "//ni/3dlYw==",
		"auths": [
			{
				"auth": {
					"authtype": "web",
					"browser": {
						"name": "Chromium",
						"version": "37.0.2062"
					},
					"ip": {
						"AS": 13238,
						"geoid": 9999,
						"ip": "2a02:6b8:0:40c:7c4a:2d06:8ebf:f80b"
					},
					"token": {
						"clientId": "7a54f58d4ebe431c4aaa53895522bf2d",
						"deviceId": "77f6c30606a8438c187be94ca4557c9f",
						"deviceName": "HTC",
						"scopes": "mobile:all,mobmail:all,yadisk:disk,cloud_api:disk.app_folder,cloud_api:disk.read,cloud_api:disk.write",
						"tokenId": "123",
						"AP": true
					},
					"os": {
						"name": "Ubuntu",
						"version": "10.04"
					}
				},
				"count": 1,
				"timestamps": [
					1432216311.37
				]
			}
		]
	}`

	httpmock.RegisterResponder(
		"GET",
		"http://localhost:8201/3/auths/aggregated/",
		newTestQueryHandler(expectedBody, map[string]string{
			"consumer":       "me, mario",
			"uid":            "123",
			"limit":          "1000",
			"hours_limit":    "24",
			"from":           "from everywhere",
			"password_auths": "true",
		}),
	)

	limit := uint64(1000)
	hoursLimit := uint64(24)
	from := "from everywhere"
	actualResponse, err := testClient.GetAuthsAggregated(context.Background(), &reqs.AuthsAggregatedRequest{
		UID:           123,
		Limit:         &limit,
		From:          &from,
		HoursLimit:    &hoursLimit,
		PasswordAuths: true,
	})
	require.NoError(t, err)

	jsonResponse, err := json.Marshal(actualResponse)
	require.NoError(t, err)
	require.JSONEq(t, expectedBody, string(jsonResponse))
}

func TestClient_GetAuthsRuntimeAggregated(t *testing.T) {
	expectedBody := `{
		"status": "ok",
		"uid": 4000886691,
		"history": [
			{
				"auths": [
					{
						"auth": {
							"authtype": "web",
							"browser": {
								"name": "Chromium",
								"version": "37.0.2062",
								"yandexuid": "9396620471389698324"
							},
							"ip": {
								"AS": 13238,
								"geoid": 9999,
								"ip": "2a02:6b8:0:40c:7c4a:2d06:8ebf:f80b"
							},
							"os": {
								"name": "Ubuntu"
							},
							"status": "ses_create"
						},
						"count": 1
					}
				],
				"timestamp": 1432166400
			}
		]
	}`

	httpmock.RegisterResponder(
		"GET",
		"http://localhost:8201/2/auths/aggregated/runtime/",
		newTestQueryHandler(expectedBody, map[string]string{
			"consumer": "me, mario",
			"uid":      "123",
			"from_ts":  "160011",
			"to_ts":    "160050",
			"limit":    "1000",
		}),
	)

	actualResponse, err := testClient.GetAuthsRuntimeAggregated(context.Background(), &reqs.AuthsRuntimeAggregatedRequest{
		UID:    123,
		FromTS: 160011,
		ToTS:   160101,
		Limit:  1000,
	}, 160051)
	require.NoError(t, err)

	jsonResponse, err := json.Marshal(actualResponse)
	require.NoError(t, err)
	require.JSONEq(t, expectedBody, string(jsonResponse))
}
