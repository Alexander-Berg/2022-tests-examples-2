package passportapi

import (
	"context"
	"encoding/json"
	"net/http"
	"testing"

	"github.com/stretchr/testify/assert"
)

var registerFederalTestClient = []struct {
	name           string
	request        RegisterFederalRequest
	jsonResponse   rawRegisterFederalResponse
	parsedResponse RegisterFederalResponse
	err            bool
}{
	{
		"ok",
		RegisterFederalRequest{
			FirstName: "Ivan",
			LastName:  "Ivanov",
			DomainID:  6789,
			Active:    true,
		},
		rawRegisterFederalResponse{
			BaseResponse: BaseResponse{
				Status: "ok",
			},
			UID: 12345,
		},
		RegisterFederalResponse{
			BaseResponse: BaseResponse{
				Status: "ok",
			},
			UID: 12345,
		},
		false,
	},
	{
		"errors",
		RegisterFederalRequest{
			FirstName: "Ivan",
			LastName:  "Ivanov",
		},
		rawRegisterFederalResponse{
			BaseResponse: BaseResponse{
				Status: "error",
				Errors: []string{"error1", "error2"},
			},
		},
		RegisterFederalResponse{
			BaseResponse: BaseResponse{
				Status: "error",
				Errors: []string{"error1", "error2"},
			},
		},
		false,
	},
	{
		"missing uid",
		RegisterFederalRequest{
			FirstName: "Ivan",
			LastName:  "Ivanov",
			DomainID:  6789,
			Active:    true,
		},
		rawRegisterFederalResponse{
			BaseResponse: BaseResponse{
				Status: "ok",
			},
		},
		RegisterFederalResponse{
			BaseResponse: BaseResponse{
				Status: "ok",
			},
		},
		true,
	},
}

func TestRegisterFederal(t *testing.T) {
	for _, tt := range registerFederalTestClient {
		t.Run(
			tt.name,
			func(t *testing.T) {
				// ожидаемый ответ запаковывается в json...
				jsonResponse, err := json.Marshal(tt.jsonResponse)
				assert.NoError(t, err)

				// ...и подсовывается тестовому http-клиенту...
				expectedHTTPResponse := TestResponse(
					http.StatusOK,
					string(jsonResponse),
				)
				c := TestPassportClient(t, expectedHTTPResponse)
				actualResponse, err := c.RegisterFederal(context.Background(), Headers{}, tt.request)

				if tt.err {
					assert.NotEqual(t, nil, err)
				} else {
					assert.NoError(t, err)
				}
				// после дергания ручки проверяется, что ответ соответствует ожидаемому
				assert.Equal(t, actualResponse, tt.parsedResponse)
			},
		)
	}
}
