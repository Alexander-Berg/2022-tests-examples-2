// Code generated by MockGen. DO NOT EDIT.
// Source: interfaces.go

// Package yabs is a generated GoMock package.
package yabs

import (
	reflect "reflect"

	models "a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	gomock "github.com/golang/mock/gomock"
)

// MockcomponentsGetter is a mock of componentsGetter interface.
type MockcomponentsGetter struct {
	ctrl     *gomock.Controller
	recorder *MockcomponentsGetterMockRecorder
}

// MockcomponentsGetterMockRecorder is the mock recorder for MockcomponentsGetter.
type MockcomponentsGetterMockRecorder struct {
	mock *MockcomponentsGetter
}

// NewMockcomponentsGetter creates a new mock instance.
func NewMockcomponentsGetter(ctrl *gomock.Controller) *MockcomponentsGetter {
	mock := &MockcomponentsGetter{ctrl: ctrl}
	mock.recorder = &MockcomponentsGetterMockRecorder{mock}
	return mock
}

// EXPECT returns an object that allows the caller to indicate expected use.
func (m *MockcomponentsGetter) EXPECT() *MockcomponentsGetterMockRecorder {
	return m.recorder
}

// GetAADB mocks base method.
func (m *MockcomponentsGetter) GetAADB() models.AADB {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetAADB")
	ret0, _ := ret[0].(models.AADB)
	return ret0
}

// GetAADB indicates an expected call of GetAADB.
func (mr *MockcomponentsGetterMockRecorder) GetAADB() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetAADB", reflect.TypeOf((*MockcomponentsGetter)(nil).GetAADB))
}

// GetAppInfo mocks base method.
func (m *MockcomponentsGetter) GetAppInfo() models.AppInfo {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetAppInfo")
	ret0, _ := ret[0].(models.AppInfo)
	return ret0
}

// GetAppInfo indicates an expected call of GetAppInfo.
func (mr *MockcomponentsGetterMockRecorder) GetAppInfo() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetAppInfo", reflect.TypeOf((*MockcomponentsGetter)(nil).GetAppInfo))
}

// GetAuthOrErr mocks base method.
func (m *MockcomponentsGetter) GetAuthOrErr() (models.Auth, error) {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetAuthOrErr")
	ret0, _ := ret[0].(models.Auth)
	ret1, _ := ret[1].(error)
	return ret0, ret1
}

// GetAuthOrErr indicates an expected call of GetAuthOrErr.
func (mr *MockcomponentsGetterMockRecorder) GetAuthOrErr() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetAuthOrErr", reflect.TypeOf((*MockcomponentsGetter)(nil).GetAuthOrErr))
}

// GetClid mocks base method.
func (m *MockcomponentsGetter) GetClid() models.Clid {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetClid")
	ret0, _ := ret[0].(models.Clid)
	return ret0
}

// GetClid indicates an expected call of GetClid.
func (mr *MockcomponentsGetterMockRecorder) GetClid() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetClid", reflect.TypeOf((*MockcomponentsGetter)(nil).GetClid))
}

// GetDevice mocks base method.
func (m *MockcomponentsGetter) GetDevice() models.Device {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetDevice")
	ret0, _ := ret[0].(models.Device)
	return ret0
}

// GetDevice indicates an expected call of GetDevice.
func (mr *MockcomponentsGetterMockRecorder) GetDevice() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetDevice", reflect.TypeOf((*MockcomponentsGetter)(nil).GetDevice))
}

// GetFlags mocks base method.
func (m *MockcomponentsGetter) GetFlags() models.ABFlags {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetFlags")
	ret0, _ := ret[0].(models.ABFlags)
	return ret0
}

// GetFlags indicates an expected call of GetFlags.
func (mr *MockcomponentsGetterMockRecorder) GetFlags() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetFlags", reflect.TypeOf((*MockcomponentsGetter)(nil).GetFlags))
}

// GetGeo mocks base method.
func (m *MockcomponentsGetter) GetGeo() models.Geo {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetGeo")
	ret0, _ := ret[0].(models.Geo)
	return ret0
}

// GetGeo indicates an expected call of GetGeo.
func (mr *MockcomponentsGetterMockRecorder) GetGeo() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetGeo", reflect.TypeOf((*MockcomponentsGetter)(nil).GetGeo))
}

// GetLocale mocks base method.
func (m *MockcomponentsGetter) GetLocale() models.Locale {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetLocale")
	ret0, _ := ret[0].(models.Locale)
	return ret0
}

// GetLocale indicates an expected call of GetLocale.
func (mr *MockcomponentsGetterMockRecorder) GetLocale() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetLocale", reflect.TypeOf((*MockcomponentsGetter)(nil).GetLocale))
}

// GetMordaContent mocks base method.
func (m *MockcomponentsGetter) GetMordaContent() models.MordaContent {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetMordaContent")
	ret0, _ := ret[0].(models.MordaContent)
	return ret0
}

// GetMordaContent indicates an expected call of GetMordaContent.
func (mr *MockcomponentsGetterMockRecorder) GetMordaContent() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetMordaContent", reflect.TypeOf((*MockcomponentsGetter)(nil).GetMordaContent))
}

// GetOriginRequest mocks base method.
func (m *MockcomponentsGetter) GetOriginRequest() (*models.OriginRequest, error) {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetOriginRequest")
	ret0, _ := ret[0].(*models.OriginRequest)
	ret1, _ := ret[1].(error)
	return ret0, ret1
}

// GetOriginRequest indicates an expected call of GetOriginRequest.
func (mr *MockcomponentsGetterMockRecorder) GetOriginRequest() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetOriginRequest", reflect.TypeOf((*MockcomponentsGetter)(nil).GetOriginRequest))
}

// GetRequest mocks base method.
func (m *MockcomponentsGetter) GetRequest() models.Request {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetRequest")
	ret0, _ := ret[0].(models.Request)
	return ret0
}

// GetRequest indicates an expected call of GetRequest.
func (mr *MockcomponentsGetterMockRecorder) GetRequest() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetRequest", reflect.TypeOf((*MockcomponentsGetter)(nil).GetRequest))
}

// GetYaCookies mocks base method.
func (m *MockcomponentsGetter) GetYaCookies() models.YaCookies {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetYaCookies")
	ret0, _ := ret[0].(models.YaCookies)
	return ret0
}

// GetYaCookies indicates an expected call of GetYaCookies.
func (mr *MockcomponentsGetterMockRecorder) GetYaCookies() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetYaCookies", reflect.TypeOf((*MockcomponentsGetter)(nil).GetYaCookies))
}

// MockyabsMadmGetter is a mock of yabsMadmGetter interface.
type MockyabsMadmGetter struct {
	ctrl     *gomock.Controller
	recorder *MockyabsMadmGetterMockRecorder
}

// MockyabsMadmGetterMockRecorder is the mock recorder for MockyabsMadmGetter.
type MockyabsMadmGetterMockRecorder struct {
	mock *MockyabsMadmGetter
}

// NewMockyabsMadmGetter creates a new mock instance.
func NewMockyabsMadmGetter(ctrl *gomock.Controller) *MockyabsMadmGetter {
	mock := &MockyabsMadmGetter{ctrl: ctrl}
	mock.recorder = &MockyabsMadmGetterMockRecorder{mock}
	return mock
}

// EXPECT returns an object that allows the caller to indicate expected use.
func (m *MockyabsMadmGetter) EXPECT() *MockyabsMadmGetterMockRecorder {
	return m.recorder
}

// Get mocks base method.
func (m *MockyabsMadmGetter) Get() ([]string, error) {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "Get")
	ret0, _ := ret[0].([]string)
	ret1, _ := ret[1].(error)
	return ret0, ret1
}

// Get indicates an expected call of Get.
func (mr *MockyabsMadmGetterMockRecorder) Get() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "Get", reflect.TypeOf((*MockyabsMadmGetter)(nil).Get))
}

// MockgeoSettingsGetter is a mock of geoSettingsGetter interface.
type MockgeoSettingsGetter struct {
	ctrl     *gomock.Controller
	recorder *MockgeoSettingsGetterMockRecorder
}

// MockgeoSettingsGetterMockRecorder is the mock recorder for MockgeoSettingsGetter.
type MockgeoSettingsGetterMockRecorder struct {
	mock *MockgeoSettingsGetter
}

// NewMockgeoSettingsGetter creates a new mock instance.
func NewMockgeoSettingsGetter(ctrl *gomock.Controller) *MockgeoSettingsGetter {
	mock := &MockgeoSettingsGetter{ctrl: ctrl}
	mock.recorder = &MockgeoSettingsGetterMockRecorder{mock}
	return mock
}

// EXPECT returns an object that allows the caller to indicate expected use.
func (m *MockgeoSettingsGetter) EXPECT() *MockgeoSettingsGetterMockRecorder {
	return m.recorder
}

// Get mocks base method.
func (m *MockgeoSettingsGetter) Get() (*geoSettings, error) {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "Get")
	ret0, _ := ret[0].(*geoSettings)
	ret1, _ := ret[1].(error)
	return ret0, ret1
}

// Get indicates an expected call of Get.
func (mr *MockgeoSettingsGetterMockRecorder) Get() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "Get", reflect.TypeOf((*MockgeoSettingsGetter)(nil).Get))
}