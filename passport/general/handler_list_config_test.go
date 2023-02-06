package federalcfgapi

import (
	"context"
	"encoding/json"
	"io/ioutil"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/labstack/echo/v4"
	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/passport/backend/federal_config_api/internal/core/models"
	"a.yandex-team.ru/passport/backend/federal_config_api/mocks/mock_controllers"
)

var testTableList = []struct {
	name          string
	queryParams   string
	startConfigID uint64
	limit         uint64
}{
	{
		name:          "list by default",
		queryParams:   "namespace=test-namespace",
		startConfigID: 0,
		limit:         100,
	},
	{
		name:          "list not from the start",
		queryParams:   "start_config_id=100&namespace=test-namespace",
		startConfigID: 100,
		limit:         100,
	},
	{
		name:          "list with limit",
		queryParams:   "start_config_id=100&limit=200&namespace=test-namespace",
		startConfigID: 100,
		limit:         200,
	},
}

func TestList(t *testing.T) {
	ctrl := gomock.NewController(t)

	for _, tt := range testTableList {
		t.Run(
			tt.name,
			func(t *testing.T) {
				e := echo.New()
				configController := mock_controllers.NewMockFederalConfigController(ctrl)
				authController := mock_controllers.NewMockAuthController(ctrl)

				req := httptest.NewRequest(
					http.MethodGet,
					"/1/config/?"+tt.queryParams,
					nil,
				)
				rec := httptest.NewRecorder()

				c := e.NewContext(req, rec)

				var app FederalConfigAPI
				app.configController = configController
				app.authController = authController

				expectedConfig := buildTestConfig()
				expectedConfigs := []models.FederationConfig{expectedConfig}

				ctx := context.Background()

				namespace := "test-namespace"
				authController.EXPECT().HasRole(ctx, gomock.Any()).Return(true, nil)
				configController.EXPECT().List(ctx, namespace, tt.startConfigID, tt.limit).Return(expectedConfigs, nil)

				if assert.NoError(t, app.HandleListConfig()(c)) {
					assert.Equal(t, http.StatusOK, rec.Code)
					responseRaw, err := ioutil.ReadAll(rec.Body)
					if err != nil {
						assert.Error(t, err)
					}
					var parsedResponse ResponseList
					if err := json.Unmarshal(responseRaw, &parsedResponse); err != nil {
						assert.Error(t, err)
					}
					assert.Equal(t, expectedConfigs, parsedResponse.Configs)
				}
			},
		)
	}
}
