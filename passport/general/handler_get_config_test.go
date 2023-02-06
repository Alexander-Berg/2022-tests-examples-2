package federalcfgapi

import (
	"context"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/labstack/echo/v4"
	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/passport/backend/federal_config_api/internal/core/models"
	"a.yandex-team.ru/passport/backend/federal_config_api/mocks/mock_controllers"
)

func buildTestConfig() models.FederationConfig {
	var config models.FederationConfig
	config.EntityID = "http://test-entity-id"
	config.DomainIDs = []uint64{1, 2, 3}
	config.SAMLConfig.SingleSignOnService.URL = "SSO URL"
	config.SAMLConfig.SingleSignOnService.Binding = "SSO BIND"
	config.SAMLConfig.SingleLogoutService.URL = "SLO URL"
	config.SAMLConfig.SingleLogoutService.Binding = "SLO BIND"
	config.SAMLConfig.X509Cert.New = "CERT NEW"
	config.SAMLConfig.X509Cert.Old = "CERT OLD"
	config.SAMLConfig.LowercaseUrlencoding = false
	config.SAMLConfig.DisableJitProvisioning = false
	config.Enabled = true
	config.ConfigID = uint64(1)
	return config
}

type LookupType int

const (
	GetByConfigID LookupType = iota
	GetByEntityID
	GetByDomainID
)

var testTableGetByConfigID = []struct {
	name        string
	ID          string
	queryParams string
	lookupType  LookupType
}{
	{
		name:        "get by config id",
		ID:          "1",
		queryParams: "namespace=test-namespace",
		lookupType:  GetByConfigID,
	},
	{
		name:        "get by entity id",
		ID:          "http:%2F%2Ftest-entity-id",
		queryParams: "namespace=test-namespace",
		lookupType:  GetByEntityID,
	},
	{
		name:        "get by domain id",
		ID:          "1",
		queryParams: "namespace=test-namespace",
		lookupType:  GetByDomainID,
	},
}

func TestGetByID(t *testing.T) {
	ctrl := gomock.NewController(t)

	for _, tt := range testTableGetByConfigID {
		t.Run(
			tt.name,
			func(t *testing.T) {

				e := echo.New()
				configController := mock_controllers.NewMockFederalConfigController(ctrl)
				authController := mock_controllers.NewMockAuthController(ctrl)

				req := httptest.NewRequest(
					http.MethodGet,
					"/?"+tt.queryParams,
					nil,
				)
				rec := httptest.NewRecorder()

				c := e.NewContext(req, rec)

				var app FederalConfigAPI
				app.configController = configController
				app.authController = authController

				expectedConfig := buildTestConfig()

				ctx := context.Background()

				authController.EXPECT().HasRole(ctx, gomock.Any()).Return(true, nil)
				switch tt.lookupType {
				case GetByConfigID:
					configController.EXPECT().GetByConfigID(ctx, "test-namespace", uint64(1)).Return(expectedConfig, nil)
					c.SetParamNames("config_id")
					c.SetParamValues(tt.ID)
					assert.NoError(t, app.HandleGetByConfigIDConfig()(c))
				case GetByEntityID:
					configController.EXPECT().GetByEntityID(ctx, "test-namespace", "http://test-entity-id").Return(expectedConfig, nil)
					c.SetParamNames("entity_id")
					c.SetParamValues(tt.ID)
					assert.NoError(t, app.HandleGetByEntityIDConfig()(c))
				case GetByDomainID:
					configController.EXPECT().GetByDomainID(ctx, "test-namespace", uint64(1)).Return(expectedConfig, nil)
					c.SetParamNames("domain_id")
					c.SetParamValues(tt.ID)
					assert.NoError(t, app.HandleGetByDomainIDConfig()(c))
				default:
					panic(fmt.Errorf("unexpected lookup type %+v", tt.lookupType))
				}

				assert.Equal(t, http.StatusOK, rec.Code)
				responseRaw, err := ioutil.ReadAll(rec.Body)
				if err != nil {
					assert.Error(t, err)
				}
				var actualConfig models.FederationConfig
				if err := json.Unmarshal(responseRaw, &actualConfig); err != nil {
					assert.Error(t, err)
				}
				assert.Equal(t, expectedConfig, actualConfig)
			},
		)
	}
}

var getConfigFormErrorsTestTable = []struct {
	name       string
	url        string
	lookupType LookupType
	inputJSON  string
}{
	{
		"get by config id & no namespace",
		"/1/config/",
		GetByConfigID,
		``,
	},
	{
		"get by entity id & no namespace",
		"/1/config/",
		GetByEntityID,
		``,
	},
	{
		"get by domain id & no namespace",
		"/1/config/",
		GetByDomainID,
		``,
	},
}

func TestGetConfigFormErrors(t *testing.T) {
	ctrl := gomock.NewController(t)

	for _, tt := range getConfigFormErrorsTestTable {
		t.Run(
			tt.name,
			func(t *testing.T) {
				e := echo.New()
				configController := mock_controllers.NewMockFederalConfigController(ctrl)
				authController := mock_controllers.NewMockAuthController(ctrl)

				req := httptest.NewRequest(
					http.MethodGet,
					tt.url,
					strings.NewReader(tt.inputJSON),
				)

				rec := httptest.NewRecorder()

				c := e.NewContext(req, rec)
				switch tt.lookupType {
				case GetByConfigID:
					c.SetParamNames("config_id")
					c.SetParamValues("1")
				case GetByEntityID:
					c.SetParamValues("entity_id")
					c.SetParamValues("http:%2F%2Ftest-entity-id")
				case GetByDomainID:
					c.SetParamNames("domain_id")
					c.SetParamValues("1")
				default:
					panic(fmt.Errorf("unexpected lookup type %+v", tt.lookupType))
				}

				var app FederalConfigAPI
				app.configController = configController
				app.authController = authController

				switch tt.lookupType {
				case GetByConfigID:
					assert.NoError(t, app.HandleGetByConfigIDConfig()(c))
				case GetByEntityID:
					assert.NoError(t, app.HandleGetByEntityIDConfig()(c))
				case GetByDomainID:
					assert.NoError(t, app.HandleGetByDomainIDConfig()(c))
				}

				assert.Equal(t, http.StatusBadRequest, rec.Code)
			},
		)
	}
}
