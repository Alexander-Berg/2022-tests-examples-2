// Code generated by MockGen. DO NOT EDIT.
// Source: interfaces.go

// Package clids is a generated GoMock package.
package clids

import (
	models "a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	gomock "github.com/golang/mock/gomock"
	reflect "reflect"
)

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

// MockcookieGetter is a mock of cookieGetter interface.
type MockcookieGetter struct {
	ctrl     *gomock.Controller
	recorder *MockcookieGetterMockRecorder
}

// MockcookieGetterMockRecorder is the mock recorder for MockcookieGetter.
type MockcookieGetterMockRecorder struct {
	mock *MockcookieGetter
}

// NewMockcookieGetter creates a new mock instance.
func NewMockcookieGetter(ctrl *gomock.Controller) *MockcookieGetter {
	mock := &MockcookieGetter{ctrl: ctrl}
	mock.recorder = &MockcookieGetterMockRecorder{mock}
	return mock
}

// EXPECT returns an object that allows the caller to indicate expected use.
func (m *MockcookieGetter) EXPECT() *MockcookieGetterMockRecorder {
	return m.recorder
}

// GetCookie mocks base method.
func (m *MockcookieGetter) GetCookie() models.Cookie {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetCookie")
	ret0, _ := ret[0].(models.Cookie)
	return ret0
}

// GetCookie indicates an expected call of GetCookie.
func (mr *MockcookieGetterMockRecorder) GetCookie() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetCookie", reflect.TypeOf((*MockcookieGetter)(nil).GetCookie))
}

// MockclidParser is a mock of clidParser interface.
type MockclidParser struct {
	ctrl     *gomock.Controller
	recorder *MockclidParserMockRecorder
}

// MockclidParserMockRecorder is the mock recorder for MockclidParser.
type MockclidParserMockRecorder struct {
	mock *MockclidParser
}

// NewMockclidParser creates a new mock instance.
func NewMockclidParser(ctrl *gomock.Controller) *MockclidParser {
	mock := &MockclidParser{ctrl: ctrl}
	mock.recorder = &MockclidParserMockRecorder{mock}
	return mock
}

// EXPECT returns an object that allows the caller to indicate expected use.
func (m *MockclidParser) EXPECT() *MockclidParserMockRecorder {
	return m.recorder
}

// parse mocks base method.
func (m *MockclidParser) parse() models.Clid {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "parse")
	ret0, _ := ret[0].(models.Clid)
	return ret0
}

// parse indicates an expected call of parse.
func (mr *MockclidParserMockRecorder) parse() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "parse", reflect.TypeOf((*MockclidParser)(nil).parse))
}
