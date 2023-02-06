// Code generated by MockGen. DO NOT EDIT.
// Source: interfaces.go

// Package requests is a generated GoMock package.
package requests

import (
	url "net/url"
	reflect "reflect"

	models "a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	gomock "github.com/golang/mock/gomock"
)

// MockoriginRequestKeeper is a mock of originRequestKeeper interface.
type MockoriginRequestKeeper struct {
	ctrl     *gomock.Controller
	recorder *MockoriginRequestKeeperMockRecorder
}

// MockoriginRequestKeeperMockRecorder is the mock recorder for MockoriginRequestKeeper.
type MockoriginRequestKeeperMockRecorder struct {
	mock *MockoriginRequestKeeper
}

// NewMockoriginRequestKeeper creates a new mock instance.
func NewMockoriginRequestKeeper(ctrl *gomock.Controller) *MockoriginRequestKeeper {
	mock := &MockoriginRequestKeeper{ctrl: ctrl}
	mock.recorder = &MockoriginRequestKeeperMockRecorder{mock}
	return mock
}

// EXPECT returns an object that allows the caller to indicate expected use.
func (m *MockoriginRequestKeeper) EXPECT() *MockoriginRequestKeeperMockRecorder {
	return m.recorder
}

// GetOriginRequest mocks base method.
func (m *MockoriginRequestKeeper) GetOriginRequest() (*models.OriginRequest, error) {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetOriginRequest")
	ret0, _ := ret[0].(*models.OriginRequest)
	ret1, _ := ret[1].(error)
	return ret0, ret1
}

// GetOriginRequest indicates an expected call of GetOriginRequest.
func (mr *MockoriginRequestKeeperMockRecorder) GetOriginRequest() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetOriginRequest", reflect.TypeOf((*MockoriginRequestKeeper)(nil).GetOriginRequest))
}

// MockrequestParser is a mock of requestParser interface.
type MockrequestParser struct {
	ctrl     *gomock.Controller
	recorder *MockrequestParserMockRecorder
}

// MockrequestParserMockRecorder is the mock recorder for MockrequestParser.
type MockrequestParserMockRecorder struct {
	mock *MockrequestParser
}

// NewMockrequestParser creates a new mock instance.
func NewMockrequestParser(ctrl *gomock.Controller) *MockrequestParser {
	mock := &MockrequestParser{ctrl: ctrl}
	mock.recorder = &MockrequestParserMockRecorder{mock}
	return mock
}

// EXPECT returns an object that allows the caller to indicate expected use.
func (m *MockrequestParser) EXPECT() *MockrequestParserMockRecorder {
	return m.recorder
}

// IsSID669ByAuth mocks base method.
func (m *MockrequestParser) IsSID669ByAuth() bool {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "IsSID669ByAuth")
	ret0, _ := ret[0].(bool)
	return ret0
}

// IsSID669ByAuth indicates an expected call of IsSID669ByAuth.
func (mr *MockrequestParserMockRecorder) IsSID669ByAuth() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "IsSID669ByAuth", reflect.TypeOf((*MockrequestParser)(nil).IsSID669ByAuth))
}

// IsStaffLogin mocks base method.
func (m *MockrequestParser) IsStaffLogin(cgi url.Values, isInternal bool) (bool, error) {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "IsStaffLogin", cgi, isInternal)
	ret0, _ := ret[0].(bool)
	ret1, _ := ret[1].(error)
	return ret0, ret1
}

// IsStaffLogin indicates an expected call of IsStaffLogin.
func (mr *MockrequestParserMockRecorder) IsStaffLogin(cgi, isInternal interface{}) *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "IsStaffLogin", reflect.TypeOf((*MockrequestParser)(nil).IsStaffLogin), cgi, isInternal)
}

// Parse mocks base method.
func (m *MockrequestParser) Parse() (models.Request, error) {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "Parse")
	ret0, _ := ret[0].(models.Request)
	ret1, _ := ret[1].(error)
	return ret0, ret1
}

// Parse indicates an expected call of Parse.
func (mr *MockrequestParserMockRecorder) Parse() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "Parse", reflect.TypeOf((*MockrequestParser)(nil).Parse))
}

// MockapiParser is a mock of apiParser interface.
type MockapiParser struct {
	ctrl     *gomock.Controller
	recorder *MockapiParserMockRecorder
}

// MockapiParserMockRecorder is the mock recorder for MockapiParser.
type MockapiParserMockRecorder struct {
	mock *MockapiParser
}

// NewMockapiParser creates a new mock instance.
func NewMockapiParser(ctrl *gomock.Controller) *MockapiParser {
	mock := &MockapiParser{ctrl: ctrl}
	mock.recorder = &MockapiParserMockRecorder{mock}
	return mock
}

// EXPECT returns an object that allows the caller to indicate expected use.
func (m *MockapiParser) EXPECT() *MockapiParserMockRecorder {
	return m.recorder
}

// Parse mocks base method.
func (m *MockapiParser) Parse(url string) models.APIInfo {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "Parse", url)
	ret0, _ := ret[0].(models.APIInfo)
	return ret0
}

// Parse indicates an expected call of Parse.
func (mr *MockapiParserMockRecorder) Parse(url interface{}) *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "Parse", reflect.TypeOf((*MockapiParser)(nil).Parse), url)
}

// MockstaffLoginChecker is a mock of staffLoginChecker interface.
type MockstaffLoginChecker struct {
	ctrl     *gomock.Controller
	recorder *MockstaffLoginCheckerMockRecorder
}

// MockstaffLoginCheckerMockRecorder is the mock recorder for MockstaffLoginChecker.
type MockstaffLoginCheckerMockRecorder struct {
	mock *MockstaffLoginChecker
}

// NewMockstaffLoginChecker creates a new mock instance.
func NewMockstaffLoginChecker(ctrl *gomock.Controller) *MockstaffLoginChecker {
	mock := &MockstaffLoginChecker{ctrl: ctrl}
	mock.recorder = &MockstaffLoginCheckerMockRecorder{mock}
	return mock
}

// EXPECT returns an object that allows the caller to indicate expected use.
func (m *MockstaffLoginChecker) EXPECT() *MockstaffLoginCheckerMockRecorder {
	return m.recorder
}

// IsSID669ByAuth mocks base method.
func (m *MockstaffLoginChecker) IsSID669ByAuth() bool {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "IsSID669ByAuth")
	ret0, _ := ret[0].(bool)
	return ret0
}

// IsSID669ByAuth indicates an expected call of IsSID669ByAuth.
func (mr *MockstaffLoginCheckerMockRecorder) IsSID669ByAuth() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "IsSID669ByAuth", reflect.TypeOf((*MockstaffLoginChecker)(nil).IsSID669ByAuth))
}

// IsStaffLogin mocks base method.
func (m *MockstaffLoginChecker) IsStaffLogin(cgi url.Values, isInternal bool) (bool, error) {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "IsStaffLogin", cgi, isInternal)
	ret0, _ := ret[0].(bool)
	ret1, _ := ret[1].(error)
	return ret0, ret1
}

// IsStaffLogin indicates an expected call of IsStaffLogin.
func (mr *MockstaffLoginCheckerMockRecorder) IsStaffLogin(cgi, isInternal interface{}) *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "IsStaffLogin", reflect.TypeOf((*MockstaffLoginChecker)(nil).IsStaffLogin), cgi, isInternal)
}