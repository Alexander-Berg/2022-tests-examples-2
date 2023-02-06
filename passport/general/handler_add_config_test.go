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

var addConfigTestTable = []struct {
	name           string
	url            string
	inputJSON      string
	expectedConfig models.FederationConfig
}{
	{
		"saml_config_minimal",
		"/config/?domain_id=1&domain_id=2&domain_id=3&entity_id=test-entity-id&namespace=test-namespace",
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
		"/config/?domain_id=1&domain_id=2&domain_id=3&entity_id=test-entity-id&namespace=test-namespace",
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
		"/config/?domain_id=1&domain_id=2&domain_id=3&entity_id=test-entity-id&namespace=test-namespace",
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

func TestAddConfigOK(t *testing.T) {
	ctrl := gomock.NewController(t)

	for _, tt := range addConfigTestTable {
		t.Run(
			tt.name,
			func(t *testing.T) {
				e := echo.New()
				configController := mock_controllers.NewMockFederalConfigController(ctrl)
				authController := mock_controllers.NewMockAuthController(ctrl)

				req := httptest.NewRequest(
					http.MethodPost,
					tt.url,
					strings.NewReader(tt.inputJSON),
				)

				rec := httptest.NewRecorder()

				c := e.NewContext(req, rec)

				var app FederalConfigAPI
				app.configController = configController
				app.authController = authController

				returnedConfig := tt.expectedConfig
				returnedConfig.ConfigID = 12345

				ctx := context.Background()

				authController.EXPECT().HasRole(ctx, gomock.Any()).Return(true, nil)
				configController.EXPECT().Create(ctx, tt.expectedConfig).Return(returnedConfig, nil)

				if assert.NoError(t, app.HandleAddConfig()(c)) {
					assert.Equal(t, http.StatusCreated, rec.Code)
					responseRaw, err := ioutil.ReadAll(rec.Body)
					if err != nil {
						assert.Error(t, err)
					}
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

var addConfigFormErrorsTestTable = []struct {
	name      string
	url       string
	inputJSON string
}{
	{
		"no namespace",
		"/1/config/?domain_id=1&entity_id=1",
		``,
	},
}

func TestAddConfigFormErrors(t *testing.T) {
	ctrl := gomock.NewController(t)

	for _, tt := range addConfigFormErrorsTestTable {
		t.Run(
			tt.name,
			func(t *testing.T) {
				e := echo.New()
				configController := mock_controllers.NewMockFederalConfigController(ctrl)
				authController := mock_controllers.NewMockAuthController(ctrl)

				req := httptest.NewRequest(
					http.MethodPost,
					tt.url,
					strings.NewReader(tt.inputJSON),
				)

				rec := httptest.NewRecorder()

				c := e.NewContext(req, rec)

				var app FederalConfigAPI
				app.configController = configController
				app.authController = authController

				if assert.NoError(t, app.HandleAddConfig()(c)) {
					assert.Equal(t, http.StatusBadRequest, rec.Code)
				}
			},
		)
	}
}
