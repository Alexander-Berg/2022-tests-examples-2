// Code generated by MockGen. DO NOT EDIT.
// Source: interfaces.go

// Package plus is a generated GoMock package.
package plus

import (
	reflect "reflect"

	contexts "a.yandex-team.ru/portal/avocado/morda-go/pkg/contexts"
	gomock "github.com/golang/mock/gomock"
)

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
func (m *MockgeoSettingsGetter) Get(arg0 contexts.Base) (*geoSettings, error) {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "Get", arg0)
	ret0, _ := ret[0].(*geoSettings)
	ret1, _ := ret[1].(error)
	return ret0, ret1
}

// Get indicates an expected call of Get.
func (mr *MockgeoSettingsGetterMockRecorder) Get(arg0 interface{}) *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "Get", reflect.TypeOf((*MockgeoSettingsGetter)(nil).Get), arg0)
}

// MocklocalizationGetter is a mock of localizationGetter interface.
type MocklocalizationGetter struct {
	ctrl     *gomock.Controller
	recorder *MocklocalizationGetterMockRecorder
}

// MocklocalizationGetterMockRecorder is the mock recorder for MocklocalizationGetter.
type MocklocalizationGetterMockRecorder struct {
	mock *MocklocalizationGetter
}

// NewMocklocalizationGetter creates a new mock instance.
func NewMocklocalizationGetter(ctrl *gomock.Controller) *MocklocalizationGetter {
	mock := &MocklocalizationGetter{ctrl: ctrl}
	mock.recorder = &MocklocalizationGetterMockRecorder{mock}
	return mock
}

// EXPECT returns an object that allows the caller to indicate expected use.
func (m *MocklocalizationGetter) EXPECT() *MocklocalizationGetterMockRecorder {
	return m.recorder
}

// Get mocks base method.
func (m *MocklocalizationGetter) Get(arg0 contexts.Base, arg1 string) string {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "Get", arg0, arg1)
	ret0, _ := ret[0].(string)
	return ret0
}

// Get indicates an expected call of Get.
func (mr *MocklocalizationGetterMockRecorder) Get(arg0, arg1 interface{}) *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "Get", reflect.TypeOf((*MocklocalizationGetter)(nil).Get), arg0, arg1)
}