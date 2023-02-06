package fedcfgclient

import (
	"context"
	"encoding/json"
	"net/http"
	"testing"

	"github.com/stretchr/testify/assert"
)

var getConfigByDomainIDOkTestTable = []struct {
	name       string
	httpStatus int
	response   FedCfgConfigResponse
}{
	{
		"simple",
		http.StatusOK,
		FedCfgConfigResponse{
			Enabled: true,
			SamlConfig: SamlConfig{
				ConfigID:  1,
				EntityID:  "2",
				DomainIDs: []uint64{3, 4},
			},
			OAuthConfig: OAuthConfig{
				ClientID: "5",
			},
		},
	},
}

func TestGetConfigByDomainIdOk(t *testing.T) {
	for _, tt := range getConfigByDomainIDOkTestTable {
		t.Run(
			tt.name,
			func(t *testing.T) {
				// ожидаемый ответ запаковывается в json...
				jsonResponse, err := json.Marshal(tt.response)
				assert.NoError(t, err)

				// ...и подсовывается тестовому http-клиенту...
				rawHTTPResponse := TestResponse(
					tt.httpStatus,
					string(jsonResponse),
				)
				c := TestFedCfgClient(t, rawHTTPResponse)
				actualResponse, err := c.GetConfigByDomainID(context.Background(), 3)

				if assert.NoError(t, err) {
					// после дергания ручки проверяется, что ответ соответствует ожидаемому
					assert.Equal(t, actualResponse, tt.response)
				}
			},
		)
	}
}

var getConfigByDomainIDErrorTestTable = []struct {
	name          string
	httpStatus    int
	responseText  string
	expectedError string
}{
	{
		"server_error",
		http.StatusInternalServerError,
		"Something went wrong",
		"fedcfg_api responded with status=500 ('Something went wrong')",
	},
}

func TestGetConfigByDomainIdError(t *testing.T) {
	for _, tt := range getConfigByDomainIDErrorTestTable {
		t.Run(
			tt.name,
			func(t *testing.T) {
				rawHTTPResponse := TestResponse(
					tt.httpStatus,
					tt.responseText,
				)
				c := TestFedCfgClient(t, rawHTTPResponse)
				_, err := c.GetConfigByDomainID(context.Background(), 3)

				assert.EqualError(t, err, tt.expectedError)
			},
		)
	}
}
