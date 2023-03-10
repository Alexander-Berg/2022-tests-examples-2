// Code generated by MockGen. DO NOT EDIT.
// Source: getters.go

// Package log3 is a generated GoMock package.
package log3

import (
	reflect "reflect"

	apphost "a.yandex-team.ru/apphost/api/service/go/apphost"
	models "a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	gomock "github.com/golang/mock/gomock"
)

// MockdeviceGetter is a mock of deviceGetter interface.
type MockdeviceGetter struct {
	ctrl     *gomock.Controller
	recorder *MockdeviceGetterMockRecorder
}

// MockdeviceGetterMockRecorder is the mock recorder for MockdeviceGetter.
type MockdeviceGetterMockRecorder struct {
	mock *MockdeviceGetter
}

// NewMockdeviceGetter creates a new mock instance.
func NewMockdeviceGetter(ctrl *gomock.Controller) *MockdeviceGetter {
	mock := &MockdeviceGetter{ctrl: ctrl}
	mock.recorder = &MockdeviceGetterMockRecorder{mock}
	return mock
}

// EXPECT returns an object that allows the caller to indicate expected use.
func (m *MockdeviceGetter) EXPECT() *MockdeviceGetterMockRecorder {
	return m.recorder
}

// GetDevice mocks base method.
func (m *MockdeviceGetter) GetDevice() models.Device {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetDevice")
	ret0, _ := ret[0].(models.Device)
	return ret0
}

// GetDevice indicates an expected call of GetDevice.
func (mr *MockdeviceGetterMockRecorder) GetDevice() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetDevice", reflect.TypeOf((*MockdeviceGetter)(nil).GetDevice))
}

// MockrequestGetter is a mock of requestGetter interface.
type MockrequestGetter struct {
	ctrl     *gomock.Controller
	recorder *MockrequestGetterMockRecorder
}

// MockrequestGetterMockRecorder is the mock recorder for MockrequestGetter.
type MockrequestGetterMockRecorder struct {
	mock *MockrequestGetter
}

// NewMockrequestGetter creates a new mock instance.
func NewMockrequestGetter(ctrl *gomock.Controller) *MockrequestGetter {
	mock := &MockrequestGetter{ctrl: ctrl}
	mock.recorder = &MockrequestGetterMockRecorder{mock}
	return mock
}

// EXPECT returns an object that allows the caller to indicate expected use.
func (m *MockrequestGetter) EXPECT() *MockrequestGetterMockRecorder {
	return m.recorder
}

// GetRequest mocks base method.
func (m *MockrequestGetter) GetRequest() models.Request {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetRequest")
	ret0, _ := ret[0].(models.Request)
	return ret0
}

// GetRequest indicates an expected call of GetRequest.
func (mr *MockrequestGetterMockRecorder) GetRequest() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetRequest", reflect.TypeOf((*MockrequestGetter)(nil).GetRequest))
}

// MockgeoGetter is a mock of geoGetter interface.
type MockgeoGetter struct {
	ctrl     *gomock.Controller
	recorder *MockgeoGetterMockRecorder
}

// MockgeoGetterMockRecorder is the mock recorder for MockgeoGetter.
type MockgeoGetterMockRecorder struct {
	mock *MockgeoGetter
}

// NewMockgeoGetter creates a new mock instance.
func NewMockgeoGetter(ctrl *gomock.Controller) *MockgeoGetter {
	mock := &MockgeoGetter{ctrl: ctrl}
	mock.recorder = &MockgeoGetterMockRecorder{mock}
	return mock
}

// EXPECT returns an object that allows the caller to indicate expected use.
func (m *MockgeoGetter) EXPECT() *MockgeoGetterMockRecorder {
	return m.recorder
}

// GetGeo mocks base method.
func (m *MockgeoGetter) GetGeo() models.Geo {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetGeo")
	ret0, _ := ret[0].(models.Geo)
	return ret0
}

// GetGeo indicates an expected call of GetGeo.
func (mr *MockgeoGetterMockRecorder) GetGeo() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetGeo", reflect.TypeOf((*MockgeoGetter)(nil).GetGeo))
}

// MockapphostInfoGetter is a mock of apphostInfoGetter interface.
type MockapphostInfoGetter struct {
	ctrl     *gomock.Controller
	recorder *MockapphostInfoGetterMockRecorder
}

// MockapphostInfoGetterMockRecorder is the mock recorder for MockapphostInfoGetter.
type MockapphostInfoGetterMockRecorder struct {
	mock *MockapphostInfoGetter
}

// NewMockapphostInfoGetter creates a new mock instance.
func NewMockapphostInfoGetter(ctrl *gomock.Controller) *MockapphostInfoGetter {
	mock := &MockapphostInfoGetter{ctrl: ctrl}
	mock.recorder = &MockapphostInfoGetterMockRecorder{mock}
	return mock
}

// EXPECT returns an object that allows the caller to indicate expected use.
func (m *MockapphostInfoGetter) EXPECT() *MockapphostInfoGetterMockRecorder {
	return m.recorder
}

// ApphostParams mocks base method.
func (m *MockapphostInfoGetter) ApphostParams() (apphost.ServiceParams, error) {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "ApphostParams")
	ret0, _ := ret[0].(apphost.ServiceParams)
	ret1, _ := ret[1].(error)
	return ret0, ret1
}

// ApphostParams indicates an expected call of ApphostParams.
func (mr *MockapphostInfoGetterMockRecorder) ApphostParams() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "ApphostParams", reflect.TypeOf((*MockapphostInfoGetter)(nil).ApphostParams))
}

// Path mocks base method.
func (m *MockapphostInfoGetter) Path() string {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "Path")
	ret0, _ := ret[0].(string)
	return ret0
}

// Path indicates an expected call of Path.
func (mr *MockapphostInfoGetterMockRecorder) Path() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "Path", reflect.TypeOf((*MockapphostInfoGetter)(nil).Path))
}

// MockyaCookieGetter is a mock of yaCookieGetter interface.
type MockyaCookieGetter struct {
	ctrl     *gomock.Controller
	recorder *MockyaCookieGetterMockRecorder
}

// MockyaCookieGetterMockRecorder is the mock recorder for MockyaCookieGetter.
type MockyaCookieGetterMockRecorder struct {
	mock *MockyaCookieGetter
}

// NewMockyaCookieGetter creates a new mock instance.
func NewMockyaCookieGetter(ctrl *gomock.Controller) *MockyaCookieGetter {
	mock := &MockyaCookieGetter{ctrl: ctrl}
	mock.recorder = &MockyaCookieGetterMockRecorder{mock}
	return mock
}

// EXPECT returns an object that allows the caller to indicate expected use.
func (m *MockyaCookieGetter) EXPECT() *MockyaCookieGetterMockRecorder {
	return m.recorder
}

// GetYaCookies mocks base method.
func (m *MockyaCookieGetter) GetYaCookies() models.YaCookies {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetYaCookies")
	ret0, _ := ret[0].(models.YaCookies)
	return ret0
}

// GetYaCookies indicates an expected call of GetYaCookies.
func (mr *MockyaCookieGetterMockRecorder) GetYaCookies() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetYaCookies", reflect.TypeOf((*MockyaCookieGetter)(nil).GetYaCookies))
}

// MockabFlagsGetter is a mock of abFlagsGetter interface.
type MockabFlagsGetter struct {
	ctrl     *gomock.Controller
	recorder *MockabFlagsGetterMockRecorder
}

// MockabFlagsGetterMockRecorder is the mock recorder for MockabFlagsGetter.
type MockabFlagsGetterMockRecorder struct {
	mock *MockabFlagsGetter
}

// NewMockabFlagsGetter creates a new mock instance.
func NewMockabFlagsGetter(ctrl *gomock.Controller) *MockabFlagsGetter {
	mock := &MockabFlagsGetter{ctrl: ctrl}
	mock.recorder = &MockabFlagsGetterMockRecorder{mock}
	return mock
}

// EXPECT returns an object that allows the caller to indicate expected use.
func (m *MockabFlagsGetter) EXPECT() *MockabFlagsGetterMockRecorder {
	return m.recorder
}

// GetFlags mocks base method.
func (m *MockabFlagsGetter) GetFlags() models.ABFlags {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetFlags")
	ret0, _ := ret[0].(models.ABFlags)
	return ret0
}

// GetFlags indicates an expected call of GetFlags.
func (mr *MockabFlagsGetterMockRecorder) GetFlags() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetFlags", reflect.TypeOf((*MockabFlagsGetter)(nil).GetFlags))
}

// MockmordazoneGetter is a mock of mordazoneGetter interface.
type MockmordazoneGetter struct {
	ctrl     *gomock.Controller
	recorder *MockmordazoneGetterMockRecorder
}

// MockmordazoneGetterMockRecorder is the mock recorder for MockmordazoneGetter.
type MockmordazoneGetterMockRecorder struct {
	mock *MockmordazoneGetter
}

// NewMockmordazoneGetter creates a new mock instance.
func NewMockmordazoneGetter(ctrl *gomock.Controller) *MockmordazoneGetter {
	mock := &MockmordazoneGetter{ctrl: ctrl}
	mock.recorder = &MockmordazoneGetterMockRecorder{mock}
	return mock
}

// EXPECT returns an object that allows the caller to indicate expected use.
func (m *MockmordazoneGetter) EXPECT() *MockmordazoneGetterMockRecorder {
	return m.recorder
}

// GetMordaZone mocks base method.
func (m *MockmordazoneGetter) GetMordaZone() models.MordaZone {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetMordaZone")
	ret0, _ := ret[0].(models.MordaZone)
	return ret0
}

// GetMordaZone indicates an expected call of GetMordaZone.
func (mr *MockmordazoneGetterMockRecorder) GetMordaZone() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetMordaZone", reflect.TypeOf((*MockmordazoneGetter)(nil).GetMordaZone))
}

// MockmordaContentGetter is a mock of mordaContentGetter interface.
type MockmordaContentGetter struct {
	ctrl     *gomock.Controller
	recorder *MockmordaContentGetterMockRecorder
}

// MockmordaContentGetterMockRecorder is the mock recorder for MockmordaContentGetter.
type MockmordaContentGetterMockRecorder struct {
	mock *MockmordaContentGetter
}

// NewMockmordaContentGetter creates a new mock instance.
func NewMockmordaContentGetter(ctrl *gomock.Controller) *MockmordaContentGetter {
	mock := &MockmordaContentGetter{ctrl: ctrl}
	mock.recorder = &MockmordaContentGetterMockRecorder{mock}
	return mock
}

// EXPECT returns an object that allows the caller to indicate expected use.
func (m *MockmordaContentGetter) EXPECT() *MockmordaContentGetterMockRecorder {
	return m.recorder
}

// GetMordaContent mocks base method.
func (m *MockmordaContentGetter) GetMordaContent() models.MordaContent {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetMordaContent")
	ret0, _ := ret[0].(models.MordaContent)
	return ret0
}

// GetMordaContent indicates an expected call of GetMordaContent.
func (mr *MockmordaContentGetterMockRecorder) GetMordaContent() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetMordaContent", reflect.TypeOf((*MockmordaContentGetter)(nil).GetMordaContent))
}

// MockrobotGetter is a mock of robotGetter interface.
type MockrobotGetter struct {
	ctrl     *gomock.Controller
	recorder *MockrobotGetterMockRecorder
}

// MockrobotGetterMockRecorder is the mock recorder for MockrobotGetter.
type MockrobotGetterMockRecorder struct {
	mock *MockrobotGetter
}

// NewMockrobotGetter creates a new mock instance.
func NewMockrobotGetter(ctrl *gomock.Controller) *MockrobotGetter {
	mock := &MockrobotGetter{ctrl: ctrl}
	mock.recorder = &MockrobotGetterMockRecorder{mock}
	return mock
}

// EXPECT returns an object that allows the caller to indicate expected use.
func (m *MockrobotGetter) EXPECT() *MockrobotGetterMockRecorder {
	return m.recorder
}

// GetRobot mocks base method.
func (m *MockrobotGetter) GetRobot() models.Robot {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetRobot")
	ret0, _ := ret[0].(models.Robot)
	return ret0
}

// GetRobot indicates an expected call of GetRobot.
func (mr *MockrobotGetterMockRecorder) GetRobot() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetRobot", reflect.TypeOf((*MockrobotGetter)(nil).GetRobot))
}
