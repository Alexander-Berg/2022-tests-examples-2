// Code generated by MockGen. DO NOT EDIT.
// Source: interfaces.go

// Package appinfo is a generated GoMock package.
package appinfo

import (
	models "a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	gomock "github.com/golang/mock/gomock"
	reflect "reflect"
)

// MockappInfoParser is a mock of appInfoParser interface.
type MockappInfoParser struct {
	ctrl     *gomock.Controller
	recorder *MockappInfoParserMockRecorder
}

// MockappInfoParserMockRecorder is the mock recorder for MockappInfoParser.
type MockappInfoParserMockRecorder struct {
	mock *MockappInfoParser
}

// NewMockappInfoParser creates a new mock instance.
func NewMockappInfoParser(ctrl *gomock.Controller) *MockappInfoParser {
	mock := &MockappInfoParser{ctrl: ctrl}
	mock.recorder = &MockappInfoParserMockRecorder{mock}
	return mock
}

// EXPECT returns an object that allows the caller to indicate expected use.
func (m *MockappInfoParser) EXPECT() *MockappInfoParserMockRecorder {
	return m.recorder
}

// Parse mocks base method.
func (m *MockappInfoParser) Parse() models.AppInfo {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "Parse")
	ret0, _ := ret[0].(models.AppInfo)
	return ret0
}

// Parse indicates an expected call of Parse.
func (mr *MockappInfoParserMockRecorder) Parse() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "Parse", reflect.TypeOf((*MockappInfoParser)(nil).Parse))
}

// MockrequestKeeper is a mock of requestKeeper interface.
type MockrequestKeeper struct {
	ctrl     *gomock.Controller
	recorder *MockrequestKeeperMockRecorder
}

// MockrequestKeeperMockRecorder is the mock recorder for MockrequestKeeper.
type MockrequestKeeperMockRecorder struct {
	mock *MockrequestKeeper
}

// NewMockrequestKeeper creates a new mock instance.
func NewMockrequestKeeper(ctrl *gomock.Controller) *MockrequestKeeper {
	mock := &MockrequestKeeper{ctrl: ctrl}
	mock.recorder = &MockrequestKeeperMockRecorder{mock}
	return mock
}

// EXPECT returns an object that allows the caller to indicate expected use.
func (m *MockrequestKeeper) EXPECT() *MockrequestKeeperMockRecorder {
	return m.recorder
}

// GetRequest mocks base method.
func (m *MockrequestKeeper) GetRequest() models.Request {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetRequest")
	ret0, _ := ret[0].(models.Request)
	return ret0
}

// GetRequest indicates an expected call of GetRequest.
func (mr *MockrequestKeeperMockRecorder) GetRequest() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetRequest", reflect.TypeOf((*MockrequestKeeper)(nil).GetRequest))
}

// MockyaCookiesKeeper is a mock of yaCookiesKeeper interface.
type MockyaCookiesKeeper struct {
	ctrl     *gomock.Controller
	recorder *MockyaCookiesKeeperMockRecorder
}

// MockyaCookiesKeeperMockRecorder is the mock recorder for MockyaCookiesKeeper.
type MockyaCookiesKeeperMockRecorder struct {
	mock *MockyaCookiesKeeper
}

// NewMockyaCookiesKeeper creates a new mock instance.
func NewMockyaCookiesKeeper(ctrl *gomock.Controller) *MockyaCookiesKeeper {
	mock := &MockyaCookiesKeeper{ctrl: ctrl}
	mock.recorder = &MockyaCookiesKeeperMockRecorder{mock}
	return mock
}

// EXPECT returns an object that allows the caller to indicate expected use.
func (m *MockyaCookiesKeeper) EXPECT() *MockyaCookiesKeeperMockRecorder {
	return m.recorder
}

// GetYaCookies mocks base method.
func (m *MockyaCookiesKeeper) GetYaCookies() models.YaCookies {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetYaCookies")
	ret0, _ := ret[0].(models.YaCookies)
	return ret0
}

// GetYaCookies indicates an expected call of GetYaCookies.
func (mr *MockyaCookiesKeeperMockRecorder) GetYaCookies() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetYaCookies", reflect.TypeOf((*MockyaCookiesKeeper)(nil).GetYaCookies))
}
