package hbaseapi

import (
	"context"
	"encoding/json"
	"testing"

	"github.com/jarcoal/httpmock"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/passport/infra/daemons/historydb_api2/internal/reqs"
)

func TestClient_GetEvents(t *testing.T) {
	expectedBody := `{
		"status": "ok",
		"uid":    129,
		"events": [
			{
				"value":       "1645535892",
				"client_name": "passport",
				"name":        "info.glogout",
				"timestamp":   1645535892.619035
			},
			{
				"client_name": "passport",
				"host_id":     "126",
				"ip.as_list":  "AS43247",
				"ip.geoid":    "225",
				"name":        "action",
				"timestamp":   1431579660.685827,
				"user_ip":     "77.75.158.91",
				"value":       "subscription"
			}
		]
	}`

	httpmock.RegisterResponder(
		"GET",
		"http://localhost:8201/2/events/",
		newTestQueryHandler(expectedBody, map[string]string{
			"consumer": "me, mario",
			"uid":      "123",
			"from_ts":  "160011",
			"to_ts":    "160101",
			"order_by": "asc",
			"limit":    "1000",
			"name":     "some_name,some_other_name",
		}),
	)

	limit := uint64(1000)
	actualResponse, err := testClient.GetEvents(context.Background(), &reqs.EventsRequest{
		UID:     123,
		FromTS:  160011,
		ToTS:    160101,
		OrderBy: reqs.OrderByAsc,
		Limit:   &limit,
		Name:    []string{"some_name", "some_other_name"},
	})
	require.NoError(t, err)

	jsonResponse, err := json.Marshal(actualResponse)
	require.NoError(t, err)
	require.JSONEq(t, expectedBody, string(jsonResponse))
}

func TestClient_GetEventsRestore(t *testing.T) {
	expectedBody := `{
		"status": "ok",
		"uid":    129,
		"restore_events": [
			{
				"action":     "restore_semi_auto_request",
				"data_json":  "....",
				"restore_id": "7E,18088,1425562596.0,3000386169,7fee24744865b7c278e26b160f7d3ed07e",
				"timestamp":  1425562596.005433
			}
		]
	}`

	httpmock.RegisterResponder(
		"GET",
		"http://localhost:8201/2/events/restore/",
		newTestQueryHandler(expectedBody, map[string]string{
			"consumer": "me, mario",
			"uid":      "123",
			"from_ts":  "160011",
			"to_ts":    "160101",
			"order_by": "desc",
			"limit":    "1000",
		}),
	)

	actualResponse, err := testClient.GetEventsRestore(context.Background(), &reqs.EventsRestoreRequest{
		UID:     123,
		FromTS:  160011,
		ToTS:    160101,
		OrderBy: reqs.OrderByDesc,
		Limit:   1000,
	})
	require.NoError(t, err)

	jsonResponse, err := json.Marshal(actualResponse)
	require.NoError(t, err)
	require.JSONEq(t, expectedBody, string(jsonResponse))
}

func TestClient_GetEventsByIPRegistrations(t *testing.T) {
	expectedBody := `{
		"status": "ok",
		"subnet": "2.95.5.0",
		"registrations": [
			{
				"timestamp":   1362088826,
				"client_name": "passport",
				"name":        "userinfo_ft",
				"uid":         "201732157"
			},
			{
				"timestamp":   1356160093,
				"client_name": "passport",
				"name":        "userinfo_ft",
				"uid":         "194321501"
			}
		]
	}`

	httpmock.RegisterResponder(
		"GET",
		"http://localhost:8201/2/events/by_ip/registrations/",
		newTestQueryHandler(expectedBody, map[string]string{
			"consumer": "me, mario",
			"subnet":   "2.95.5.0",
			"from_ts":  "160011",
			"to_ts":    "160101",
			"order_by": "asc",
			"limit":    "1000",
		}),
	)

	limit := uint64(1000)
	actualResponse, err := testClient.GetEventsByIPRegistrations(context.Background(), &reqs.EventsByIPRegistrationsRequest{
		SubNet:  "2.95.5.0",
		FromTS:  160011,
		ToTS:    160101,
		OrderBy: reqs.OrderByAsc,
		Limit:   &limit,
	})
	require.NoError(t, err)

	jsonResponse, err := json.Marshal(actualResponse)
	require.NoError(t, err)
	require.JSONEq(t, expectedBody, string(jsonResponse))
}

func TestClient_GetEventsPasswords(t *testing.T) {
	expectedBody := `{
		"status": "ok",
		"password_found": true,
		"active_ranges": [
			[
				1399989263.535794,
				null
			],
			[
				1390296535.791702,
				1390296698.936477
			],
			[
				1316203939.888088,
				1388411206.853863
			]
		]
	}`

	httpmock.RegisterResponder(
		"POST",
		"http://localhost:8201/2/events/passwords/",
		newTestQueryHandler(expectedBody, map[string]string{
			"consumer": "me, mario",
			"password": "qwerty",
			"uid":      "129",
			"from_ts":  "160011",
			"to_ts":    "160101",
			"limit":    "1000",
		}),
	)

	limit := uint64(1000)
	actualResponse, err := testClient.GetEventsPasswords(context.Background(), &reqs.EventsPasswordsRequest{
		Password: "qwerty",
		UID:      129,
		FromTS:   160011,
		ToTS:     160101,
		Limit:    &limit,
	})
	require.NoError(t, err)

	jsonResponse, err := json.Marshal(actualResponse)
	require.NoError(t, err)
	require.JSONEq(t, expectedBody, string(jsonResponse))
}
