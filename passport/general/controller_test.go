package controllers

import (
	"context"
	"errors"
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/passport/backend/federal_config_api/internal/core/interfaces"
	"a.yandex-team.ru/passport/backend/federal_config_api/internal/core/models"
	"a.yandex-team.ru/passport/backend/federal_config_api/mocks/mock_adapters"
)

func TestCreateReturnsConfigWithConfigID(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	cfgAdapter := mock_adapters.NewMockFederalConfigAdapter(ctrl)
	pddAdapter := mock_adapters.NewMockPDDAdapter(ctrl)

	var testConfig models.FederationConfig
	testConfig.DomainIDs = []uint64{1, 2, 3}
	testConfig.EntityID = "test-entity-id"
	testConfig.SAMLConfig.SingleSignOnService.URL = "sso-url"
	testConfig.SAMLConfig.SingleSignOnService.Binding = "sso-binding"
	testConfig.SAMLConfig.SingleLogoutService.URL = "slo-url"
	testConfig.SAMLConfig.SingleLogoutService.Binding = "slo-binding"

	configID := uint64(12345)

	expectedConfig := testConfig
	expectedConfig.ConfigID = configID

	ctx := context.Background()

	cfgAdapter.EXPECT().Create(ctx, testConfig).Return(configID, nil)
	pddAdapter.EXPECT().Exists(ctx, testConfig.DomainIDs).Return(true, nil)

	configController := NewConfigController(nil, cfgAdapter, pddAdapter)

	actualConfig, err := configController.Create(ctx, testConfig)
	assert.Equal(t, expectedConfig, actualConfig)
	assert.Equal(t, nil, err)
}

func TestCreatePDDReturnsError(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	cfgAdapter := mock_adapters.NewMockFederalConfigAdapter(ctrl)
	pddAdapter := mock_adapters.NewMockPDDAdapter(ctrl)

	var testConfig models.FederationConfig

	ctx := context.Background()

	testError := errors.New("test error")
	pddAdapter.EXPECT().Exists(ctx, gomock.Any()).Return(true, testError)

	configController := NewConfigController(nil, cfgAdapter, pddAdapter)

	actualConfig, err := configController.Create(ctx, testConfig)
	assert.Equal(t, testConfig, actualConfig)
	assert.Equal(t, testError, err)
}

func TestCreatePDDReturnsFalse(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	cfgAdapter := mock_adapters.NewMockFederalConfigAdapter(ctrl)
	pddAdapter := mock_adapters.NewMockPDDAdapter(ctrl)

	var testConfig models.FederationConfig

	ctx := context.Background()

	pddAdapter.EXPECT().Exists(ctx, gomock.Any()).Return(false, nil)

	configController := NewConfigController(nil, cfgAdapter, pddAdapter)

	actualConfig, err := configController.Create(ctx, testConfig)
	assert.Equal(t, testConfig, actualConfig)
	assert.Equal(t, interfaces.ErrNotFound, err)
}

func TestCreateReturnsError(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	cfgAdapter := mock_adapters.NewMockFederalConfigAdapter(ctrl)
	pddAdapter := mock_adapters.NewMockPDDAdapter(ctrl)

	var testConfig models.FederationConfig
	configID := uint64(12345)

	ctx := context.Background()

	testError := errors.New("test error")
	cfgAdapter.EXPECT().Create(ctx, testConfig).Return(configID, testError)
	pddAdapter.EXPECT().Exists(ctx, gomock.Any()).Return(true, nil)

	configController := NewConfigController(nil, cfgAdapter, pddAdapter)

	actualConfig, err := configController.Create(ctx, testConfig)
	assert.Equal(t, testConfig, actualConfig)
	assert.Equal(t, testError, err)
}

func TestGetReturnsConfig(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	cfgAdapter := mock_adapters.NewMockFederalConfigAdapter(ctrl)
	pddAdapter := mock_adapters.NewMockPDDAdapter(ctrl)

	configID := uint64(12345)
	var testConfig models.FederationConfig
	testConfig.Namespace = "namespace"
	testConfig.ConfigID = configID
	testConfig.DomainIDs = []uint64{1, 2, 3}
	testConfig.EntityID = "test-entity-id"
	testConfig.SAMLConfig.SingleSignOnService.URL = "sso-url"
	testConfig.SAMLConfig.SingleSignOnService.Binding = "sso-binding"
	testConfig.SAMLConfig.SingleLogoutService.URL = "slo-url"
	testConfig.SAMLConfig.SingleLogoutService.Binding = "slo-binding"

	ctx := context.Background()

	expectedConfig := testConfig
	cfgAdapter.EXPECT().GetByConfigID(ctx, "namespace", configID).Return(testConfig, nil)

	configController := NewConfigController(nil, cfgAdapter, pddAdapter)

	actualConfig, err := configController.GetByConfigID(ctx, "namespace", configID)
	assert.Equal(t, expectedConfig, actualConfig)
	assert.Equal(t, nil, err)
}

func TestGetReturnsError(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	cfgAdapter := mock_adapters.NewMockFederalConfigAdapter(ctrl)
	pddAdapter := mock_adapters.NewMockPDDAdapter(ctrl)

	configID := uint64(12345)
	var testConfig models.FederationConfig

	expectedConfig := testConfig

	ctx := context.Background()

	testError := errors.New("test error")
	cfgAdapter.EXPECT().GetByConfigID(ctx, "namespace", configID).Return(testConfig, testError)

	configController := NewConfigController(nil, cfgAdapter, pddAdapter)

	actualConfig, err := configController.GetByConfigID(ctx, "namespace", configID)
	assert.Equal(t, expectedConfig, actualConfig)
	assert.Equal(t, testError, err)
}

func TestUpdateOK(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	cfgAdapter := mock_adapters.NewMockFederalConfigAdapter(ctrl)
	pddAdapter := mock_adapters.NewMockPDDAdapter(ctrl)

	var configBody models.ConfigBody
	configBody.SAMLConfig.SingleSignOnService.URL = "sso-url"
	configBody.SAMLConfig.SingleSignOnService.Binding = "sso-binding"
	configBody.SAMLConfig.SingleLogoutService.URL = "slo-url"
	configBody.SAMLConfig.SingleLogoutService.Binding = "slo-binding"

	entityID := "test-entity-id"
	domainIDs := []uint64{1, 2, 3}
	configID := uint64(12345)

	ctx := context.Background()

	cfgAdapter.EXPECT().Update(ctx, "test-namespace", &entityID, &domainIDs, configID, configBody).Return(nil)
	pddAdapter.EXPECT().Exists(ctx, domainIDs).Return(true, nil)

	configController := NewConfigController(nil, cfgAdapter, pddAdapter)

	err := configController.Update(ctx, "test-namespace", &entityID, &domainIDs, configID, configBody)
	assert.Equal(t, nil, err)
}

func TestUpdatePDDError(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	cfgAdapter := mock_adapters.NewMockFederalConfigAdapter(ctrl)
	pddAdapter := mock_adapters.NewMockPDDAdapter(ctrl)

	var configBody models.ConfigBody

	entityID := "test-entity-id"
	domainIDs := []uint64{1, 2, 3}
	configID := uint64(12345)

	ctx := context.Background()

	testError := errors.New("test error")
	pddAdapter.EXPECT().Exists(ctx, domainIDs).Return(true, testError)

	configController := NewConfigController(nil, cfgAdapter, pddAdapter)

	err := configController.Update(ctx, "test-namespace", &entityID, &domainIDs, configID, configBody)
	assert.Equal(t, testError, err)
}

func TestUpdatePDDFalse(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	cfgAdapter := mock_adapters.NewMockFederalConfigAdapter(ctrl)
	pddAdapter := mock_adapters.NewMockPDDAdapter(ctrl)

	var configBody models.ConfigBody

	entityID := "test-entity-id"
	domainIDs := []uint64{1, 2, 3}
	configID := uint64(12345)

	ctx := context.Background()

	pddAdapter.EXPECT().Exists(ctx, domainIDs).Return(false, nil)

	configController := NewConfigController(nil, cfgAdapter, pddAdapter)

	err := configController.Update(ctx, "test-namespace", &entityID, &domainIDs, configID, configBody)
	assert.Equal(t, interfaces.ErrNotFound, err)
}

func TestUpdateError(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	cfgAdapter := mock_adapters.NewMockFederalConfigAdapter(ctrl)
	pddAdapter := mock_adapters.NewMockPDDAdapter(ctrl)

	var configBody models.ConfigBody

	entityID := "test-entity-id"
	domainIDs := []uint64{1, 2, 3}
	configID := uint64(12345)

	ctx := context.Background()

	testError := errors.New("test error")
	cfgAdapter.EXPECT().Update(ctx, "test-namespace", &entityID, &domainIDs, configID, configBody).Return(testError)
	pddAdapter.EXPECT().Exists(ctx, domainIDs).Return(true, nil)

	configController := NewConfigController(nil, cfgAdapter, pddAdapter)

	err := configController.Update(ctx, "test-namespace", &entityID, &domainIDs, configID, configBody)
	assert.Equal(t, testError, err)
}

func TestDeleteOK(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	cfgAdapter := mock_adapters.NewMockFederalConfigAdapter(ctrl)
	pddAdapter := mock_adapters.NewMockPDDAdapter(ctrl)

	configID := uint64(12345)

	ctx := context.Background()

	cfgAdapter.EXPECT().Delete(ctx, "test-namespace", configID).Return(nil)

	configController := NewConfigController(nil, cfgAdapter, pddAdapter)

	err := configController.Delete(ctx, "test-namespace", configID)
	assert.Equal(t, nil, err)
}

func TestDeleteError(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	cfgAdapter := mock_adapters.NewMockFederalConfigAdapter(ctrl)
	pddAdapter := mock_adapters.NewMockPDDAdapter(ctrl)

	configID := uint64(12345)

	ctx := context.Background()

	testError := errors.New("test error")
	cfgAdapter.EXPECT().Delete(ctx, "test-namespace", configID).Return(testError)

	configController := NewConfigController(nil, cfgAdapter, pddAdapter)

	err := configController.Delete(ctx, "test-namespace", configID)
	assert.Equal(t, testError, err)
}
