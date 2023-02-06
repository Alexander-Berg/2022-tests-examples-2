package federalcfgapi

import (
	"context"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/labstack/echo/v4"
	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/passport/backend/federal_config_api/mocks/mock_controllers"
)

var deleteConfigFormErrorsTestTable = []struct {
	name      string
	url       string
	inputJSON string
}{
	{
		"no namespace",
		"/1/config/by_config_id/1/",
		``,
	},
}

func TestDeleteConfigFormErrors(t *testing.T) {
	ctrl := gomock.NewController(t)

	for _, tt := range deleteConfigFormErrorsTestTable {
		t.Run(
			tt.name,
			func(t *testing.T) {
				e := echo.New()
				configController := mock_controllers.NewMockFederalConfigController(ctrl)
				authController := mock_controllers.NewMockAuthController(ctrl)

				req := httptest.NewRequest(
					http.MethodDelete,
					tt.url,
					strings.NewReader(tt.inputJSON),
				)

				rec := httptest.NewRecorder()

				c := e.NewContext(req, rec)

				var app FederalConfigAPI
				app.configController = configController
				app.authController = authController

				if assert.NoError(t, app.HandleDeleteConfig()(c)) {
					assert.Equal(t, http.StatusBadRequest, rec.Code)
				}
			},
		)
	}
}

func TestDeleteConfig(t *testing.T) {
	ctrl := gomock.NewController(t)
	e := echo.New()
	configController := mock_controllers.NewMockFederalConfigController(ctrl)
	authController := mock_controllers.NewMockAuthController(ctrl)

	req := httptest.NewRequest(
		http.MethodDelete,
		"/?namespace=test-namespace",
		strings.NewReader(``),
	)

	rec := httptest.NewRecorder()

	c := e.NewContext(req, rec)
	c.SetParamNames("config_id")
	c.SetParamValues("1")

	var app FederalConfigAPI
	app.configController = configController
	app.authController = authController

	configController.EXPECT().Delete(context.Background(), "test-namespace", uint64(1))
	authController.EXPECT().HasRole(context.Background(), gomock.Any())

	if assert.NoError(t, app.HandleDeleteConfig()(c)) {
		assert.Equal(t, http.StatusOK, rec.Code)
	}
}
