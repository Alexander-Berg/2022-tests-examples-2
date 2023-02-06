package hbaseapi

import (
	"context"
	"encoding/json"
	"testing"

	"github.com/jarcoal/httpmock"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/passport/infra/daemons/historydb_api2/internal/reqs"
)

func TestClient_GetSmsByGlobalID(t *testing.T) {
	expectedBody := `{
		"status": "ok",
		"global_smsid": "123",
		"items": [
			{
				"action": "deliveredtosmsc",
				"sms": "1",
				"number": "+77777777777",
				"global_smsid": "123",
				"timestamp": 1645678811.92
			},
			{
				"action": "senttosmsc",
				"local_smsid": "129",
				"masked_number": "+7777777****",
				"sms": "1",
				"number": "+77777777777",
				"global_smsid": "123",
				"timestamp": 1645678811.5
			},
			{
				"action": "enqueued",
				"local_smsid": "129",
				"sender": "sender",
				"masked_number": "+7777777****",
				"segments": "1",
				"chars": "5",
				"encoding": "utf16",
				"timestamp": 1645678810.5,
				"global_smsid": "123",
				"number": "+77777777777",
				"consumer_ip": "::1",
				"gate": "77",
				"sms": "1",
				"text": "Тест."
			}
		]
	}`

	httpmock.RegisterResponder(
		"GET",
		"http://localhost:8201/yasms/2/sms/by_globalid/",
		newTestQueryHandler(expectedBody, map[string]string{
			"consumer":     "me, mario",
			"global_smsid": "123",
		}),
	)

	actualResponse, err := testClient.GetSmsByGlobalID(context.Background(), &reqs.SmsByGlobalIDRequest{
		GlobalSmsID: "123",
	})
	require.NoError(t, err)

	jsonResponse, err := json.Marshal(actualResponse)
	require.NoError(t, err)
	require.JSONEq(t, expectedBody, string(jsonResponse))
}

func TestClient_GetSmsByPhone(t *testing.T) {
	expectedBody := `{
		"number": "77777777777",
		"status": "ok",
		"items": {
			"123": [
				{
					"action": "deliveredtosmsc",
					"sms": "1",
					"number": "+77777777777",
					"global_smsid": "123",
					"timestamp": 1645678811.92
				},
				{
					"action": "senttosmsc",
					"local_smsid": "129",
					"masked_number": "+7777777****",
					"sms": "1",
					"number": "+77777777777",
					"global_smsid": "123",
					"timestamp": 1645678811.5
				},
				{
					"action": "enqueued",
					"local_smsid": "129",
					"sender": "sender",
					"masked_number": "+7777777****",
					"segments": "1",
					"chars": "5",
					"encoding": "utf16",
					"timestamp": 1645678810.5,
					"global_smsid": "123",
					"number": "+77777777777",
					"consumer_ip": "::1",
					"gate": "77",
					"sms": "1",
					"text": "Тест."
				}
    		],
			"100500": [
				{
					"action": "deliveredtosmsc",
					"sms": "1",
					"number": "+77777777777",
					"global_smsid": "100500",
					"timestamp": 1645678811.77
				}
			]
		}
	}`

	httpmock.RegisterResponder(
		"GET",
		"http://localhost:8201/yasms/2/sms/by_phone/",
		newTestQueryHandler(expectedBody, map[string]string{
			"consumer": "me, mario",
			"phone":    "+77777777",
			"from_ts":  "160011",
			"to_ts":    "160101",
		}),
	)

	phone := "+77777777"
	fromTS := uint64(160011)
	toTS := uint64(160101)
	actualResponse, err := testClient.GetSmsByPhone(context.Background(), &reqs.SmsByFieldsRequest{
		Phone:  &phone,
		FromTS: &fromTS,
		ToTS:   &toTS,
	})
	require.NoError(t, err)

	jsonResponse, err := json.Marshal(actualResponse)
	require.NoError(t, err)
	require.JSONEq(t, expectedBody, string(jsonResponse))
}
