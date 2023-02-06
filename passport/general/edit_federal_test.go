package passportapi

import (
	"context"
	"encoding/json"
	"net/http"
	"testing"

	"github.com/stretchr/testify/assert"
)

var editFederalTestClient = []struct {
	name           string
	request        EditFederalRequest
	jsonResponse   BaseResponse
	parsedResponse BaseResponse
	err            bool
}{
	{
		"ok",
		EditFederalRequest{
			FirstName: "Ivan",
			LastName:  "Ivanov",
			Active:    true,
			UID:       12345,
		},
		BaseResponse{
			Status: "ok",
		},
		BaseResponse{
			Status: "ok",
		},
		false,
	},
	{
		"errors",
		EditFederalRequest{
			FirstName: "Ivan",
			LastName:  "Ivanov",
			UID:       12345,
		},
		BaseResponse{
			Status: "error",
			Errors: []string{"error1", "error2"},
		},
		BaseResponse{
			Status: "error",
			Errors: []string{"error1", "error2"},
		},
		false,
	},
}

func TestEditFederal(t *testing.T) {
	for _, tt := range editFederalTestClient {
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
				actualResponse, err := c.EditFederal(context.Background(), Headers{}, tt.request)

				if tt.err {
					assert.True(t, err != nil)
				} else {
					assert.NoError(t, err)
				}
				// после дергания ручки проверяется, что ответ соответствует ожидаемому
				assert.Equal(t, actualResponse, tt.parsedResponse)
			},
		)
	}
}
