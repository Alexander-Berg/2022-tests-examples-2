package passportapi

import (
	"context"
	"encoding/json"
	"net/http"
	"testing"

	"github.com/stretchr/testify/assert"
)

var deleteAccountTestTable = []struct {
	name     string
	response BaseResponse
}{
	{
		"ok", BaseResponse{
			Status: "ok",
		},
	},
	{
		"errors",
		BaseResponse{
			Status: "error",
			Errors: []string{"error1", "error2"},
		},
	},
}

func TestDeleteAccount(t *testing.T) {
	for _, tt := range deleteAccountTestTable {
		t.Run(
			tt.name,
			func(t *testing.T) {
				// ожидаемый ответ запаковывается в json...
				jsonResponse, err := json.Marshal(tt.response)
				assert.NoError(t, err)

				// ...и подсовывается тестовому http-клиенту...
				expectedHTTPResponse := TestResponse(
					http.StatusOK,
					string(jsonResponse),
				)
				c := TestPassportClient(t, expectedHTTPResponse)
				actualResponse, err := c.DeleteAccount(context.Background(), Headers{}, 12345)

				if assert.NoError(t, err) {
					// после дергания ручки проверяется, что ответ соответствует ожидаемому
					assert.Equal(t, actualResponse, tt.response)
				}
			},
		)
	}
}
