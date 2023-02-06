package federalcfgapi

import (
	"context"
	"encoding/json"
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

var editConfigTestTable = []struct {
	name           string
	url            string
	inputJSON      string
	expectedConfig models.FederationConfig
}{
	{
		"saml_config_minimal",
		"/1/config/by_config_id/12345/?domain_id=1&domain_id=2&domain_id=3&entity_id=test-entity-id&namespace=test-namespace",
		`{
		"saml_config": {
			"single_sign_on_service": {
				"url": "SSO URL",
				"binding": "SSO BIND"
			},
			"single_logout_service": {
				"url": "SLO URL",
				"binding": "SLO BIND"
			},
			"x509_cert": {
				"new": "CERT NEW",
				"old": "CERT OLD"
			}
		}}`,
		models.FederationConfig{
			EntityID:  "test-entity-id",
			DomainIDs: []uint64{1, 2, 3},
			Namespace: "test-namespace",
			ConfigBody: models.ConfigBody{
				SAMLConfig: models.SAMLConfig{
					SingleSignOnService: models.SAMLService{
						URL:     "SSO URL",
						Binding: "SSO BIND",
					},
					SingleLogoutService: models.SAMLService{
						URL:     "SLO URL",
						Binding: "SLO BIND",
					},
					X509Cert: models.X509Cert{
						New: "CERT NEW",
						Old: "CERT OLD",
					},
					LowercaseUrlencoding:   false,
					DisableJitProvisioning: false,
				},
				Enabled: true,
			},
		},
	},
	{
		"saml_config_full",
		"/1/config/by_config_id/12345/?domain_id=1&domain_id=2&domain_id=3&entity_id=test-entity-id&namespace=test-namespace",
		`{
		"saml_config": {
			"single_sign_on_service": {
				"url": "SSO URL",
				"binding": "SSO BIND"
			},
			"single_logout_service": {
				"url": "SLO URL",
				"binding": "SLO BIND"
			},
			"x509_cert": {
				"new": "CERT NEW",
				"old": "CERT OLD"
			},
			"lowercase_urlencoding": true,
			"disable_jit_provisioning": true
		},
		"enabled": true
		}`,
		models.FederationConfig{
			EntityID:  "test-entity-id",
			DomainIDs: []uint64{1, 2, 3},
			Namespace: "test-namespace",
			ConfigBody: models.ConfigBody{
				SAMLConfig: models.SAMLConfig{
					SingleSignOnService: models.SAMLService{
						URL:     "SSO URL",
						Binding: "SSO BIND",
					},
					SingleLogoutService: models.SAMLService{
						URL:     "SLO URL",
						Binding: "SLO BIND",
					},
					X509Cert: models.X509Cert{
						New: "CERT NEW",
						Old: "CERT OLD",
					},
					LowercaseUrlencoding:   true,
					DisableJitProvisioning: true,
				},
				Enabled: true,
			},
		},
	},
	{
		"oauth_config",
		"/1/config/by_config_id/12345/?domain_id=1&domain_id=2&domain_id=3&entity_id=test-entity-id&namespace=test-namespace",
		`{
		"oauth_config": {
			"client_id": "oauth-client-id"
		},
		"enabled": false
		}`,
		models.FederationConfig{
			EntityID:  "test-entity-id",
			DomainIDs: []uint64{1, 2, 3},
			Namespace: "test-namespace",
			ConfigBody: models.ConfigBody{
				OAuthConfig: models.OAuthConfig{
					ClientID: "oauth-client-id",
				},
				Enabled: false,
			},
		},
	},
}

func TestEditConfigOK(t *testing.T) {
	ctrl := gomock.NewController(t)

	for _, tt := range editConfigTestTable {
		t.Run(
			tt.name,
			func(t *testing.T) {
				e := echo.New()
				configController := mock_controllers.NewMockFederalConfigController(ctrl)
				authController := mock_controllers.NewMockAuthController(ctrl)

				req := httptest.NewRequest(
					http.MethodPut,
					tt.url,
					strings.NewReader(tt.inputJSON),
				)

				rec := httptest.NewRecorder()

				c := e.NewContext(req, rec)
				c.SetParamNames("config_id")
				c.SetParamValues("12345")

				var app FederalConfigAPI
				app.configController = configController
				app.authController = authController

				returnedConfig := tt.expectedConfig
				returnedConfig.ConfigID = 12345

				var ptrEntityID *string
				var ptrDomainIDs *[]uint64

				if tt.expectedConfig.EntityID != "" {
					ptrEntityID = &tt.expectedConfig.EntityID
				}
				if len(tt.expectedConfig.DomainIDs) > 0 {
					ptrDomainIDs = &tt.expectedConfig.DomainIDs
				}

				ctx := context.Background()

				authController.EXPECT().HasRole(ctx, gomock.Any()).Return(true, nil)
				configController.EXPECT().Update(
					ctx,
					"test-namespace",
					ptrEntityID,
					ptrDomainIDs,
					uint64(12345),
					tt.expectedConfig.ConfigBody,
				).Return(
					nil,
				)

				if assert.NoError(t, app.HandleEditConfig()(c)) {
					assert.Equal(t, http.StatusOK, rec.Code)
					responseRaw, err := ioutil.ReadAll(rec.Body)
					if err != nil {
						assert.Error(t, err)
					}
					//assert.Equal(t, "", string(responseRaw))
					var actualConfig models.FederationConfig
					if err := json.Unmarshal(responseRaw, &actualConfig); err != nil {
						assert.Error(t, err)
					}
					assert.Equal(t, returnedConfig, actualConfig)
				}
			},
		)
	}
}

var editConfigFormErrorsTestTable = []struct {
	name      string
	url       string
	configID  string
	inputJSON string
}{
	{
		"no namespace",
		"/config/by_config_id/1/",
		"1",
		``,
	},
	{
		"no config",
		"/1/config/by_config_id//?namespace=test-namespace",
		"",
		``,
	},
	{
		"no config & no namespace",
		"/1/config/by_config_id//",
		"",
		``,
	},
}

func TestEditConfigFormErrors(t *testing.T) {
	ctrl := gomock.NewController(t)

	for _, tt := range editConfigFormErrorsTestTable {
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
				c.SetParamNames("config_id")
				c.SetParamValues(tt.configID)

				var app FederalConfigAPI
				app.configController = configController
				app.authController = authController

				if strings.Contains(tt.url, "namespace=") {
					authController.EXPECT().HasRole(context.Background(), gomock.Any()).Return(true, nil)
				}
				if assert.NoError(t, app.HandleEditConfig()(c)) {
					assert.Equal(t, http.StatusBadRequest, rec.Code)
				}
			},
		)
	}
}
