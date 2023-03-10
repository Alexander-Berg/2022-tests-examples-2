// Code generated by MockGen. DO NOT EDIT.
// Source: interfaces.go

// Package handler is a generated GoMock package.
package handler

import (
	reflect "reflect"

	proto "a.yandex-team.ru/ads/bsyeti/eagle/collect/proto"
	proto_answers "a.yandex-team.ru/apphost/lib/proto_answers"
	models "a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	blackbox "a.yandex-team.ru/portal/avocado/libs/utils/blackbox"
	log3 "a.yandex-team.ru/portal/avocado/libs/utils/log3"
	yabs "a.yandex-team.ru/portal/avocado/libs/utils/yabs"
	compare "a.yandex-team.ru/portal/avocado/morda-go/internal/compare"
	contexts "a.yandex-team.ru/portal/avocado/morda-go/pkg/contexts"
	exports "a.yandex-team.ru/portal/avocado/morda-go/pkg/exports"
	its "a.yandex-team.ru/portal/avocado/morda-go/pkg/its"
	gomock "github.com/golang/mock/gomock"
)

// MockhandlerContext is a mock of handlerContext interface.
type MockhandlerContext struct {
	ctrl     *gomock.Controller
	recorder *MockhandlerContextMockRecorder
}

// MockhandlerContextMockRecorder is the mock recorder for MockhandlerContext.
type MockhandlerContextMockRecorder struct {
	mock *MockhandlerContext
}

// NewMockhandlerContext creates a new mock instance.
func NewMockhandlerContext(ctrl *gomock.Controller) *MockhandlerContext {
	mock := &MockhandlerContext{ctrl: ctrl}
	mock.recorder = &MockhandlerContextMockRecorder{mock}
	return mock
}

// EXPECT returns an object that allows the caller to indicate expected use.
func (m *MockhandlerContext) EXPECT() *MockhandlerContextMockRecorder {
	return m.recorder
}

// GetAuthInfoForCompare mocks base method.
func (m *MockhandlerContext) GetAuthInfoForCompare() ([]blackbox.AuthInfo, error) {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetAuthInfoForCompare")
	ret0, _ := ret[0].([]blackbox.AuthInfo)
	ret1, _ := ret[1].(error)
	return ret0, ret1
}

// GetAuthInfoForCompare indicates an expected call of GetAuthInfoForCompare.
func (mr *MockhandlerContextMockRecorder) GetAuthInfoForCompare() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetAuthInfoForCompare", reflect.TypeOf((*MockhandlerContext)(nil).GetAuthInfoForCompare))
}

// GetPerlReqForCompare mocks base method.
func (m *MockhandlerContext) GetPerlReqForCompare() (*proto_answers.THttpResponse, error) {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetPerlReqForCompare")
	ret0, _ := ret[0].(*proto_answers.THttpResponse)
	ret1, _ := ret[1].(error)
	return ret0, ret1
}

// GetPerlReqForCompare indicates an expected call of GetPerlReqForCompare.
func (mr *MockhandlerContextMockRecorder) GetPerlReqForCompare() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetPerlReqForCompare", reflect.TypeOf((*MockhandlerContext)(nil).GetPerlReqForCompare))
}

// MockitsComparatorOptionsGetter is a mock of itsComparatorOptionsGetter interface.
type MockitsComparatorOptionsGetter struct {
	ctrl     *gomock.Controller
	recorder *MockitsComparatorOptionsGetterMockRecorder
}

// MockitsComparatorOptionsGetterMockRecorder is the mock recorder for MockitsComparatorOptionsGetter.
type MockitsComparatorOptionsGetterMockRecorder struct {
	mock *MockitsComparatorOptionsGetter
}

// NewMockitsComparatorOptionsGetter creates a new mock instance.
func NewMockitsComparatorOptionsGetter(ctrl *gomock.Controller) *MockitsComparatorOptionsGetter {
	mock := &MockitsComparatorOptionsGetter{ctrl: ctrl}
	mock.recorder = &MockitsComparatorOptionsGetterMockRecorder{mock}
	return mock
}

// EXPECT returns an object that allows the caller to indicate expected use.
func (m *MockitsComparatorOptionsGetter) EXPECT() *MockitsComparatorOptionsGetterMockRecorder {
	return m.recorder
}

// GetComparatorOptions mocks base method.
func (m *MockitsComparatorOptionsGetter) GetComparatorOptions() its.ComparatorOptions {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetComparatorOptions")
	ret0, _ := ret[0].(its.ComparatorOptions)
	return ret0
}

// GetComparatorOptions indicates an expected call of GetComparatorOptions.
func (mr *MockitsComparatorOptionsGetterMockRecorder) GetComparatorOptions() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetComparatorOptions", reflect.TypeOf((*MockitsComparatorOptionsGetter)(nil).GetComparatorOptions))
}

// MockyabsURLBuilder is a mock of yabsURLBuilder interface.
type MockyabsURLBuilder struct {
	ctrl     *gomock.Controller
	recorder *MockyabsURLBuilderMockRecorder
}

// MockyabsURLBuilderMockRecorder is the mock recorder for MockyabsURLBuilder.
type MockyabsURLBuilderMockRecorder struct {
	mock *MockyabsURLBuilder
}

// NewMockyabsURLBuilder creates a new mock instance.
func NewMockyabsURLBuilder(ctrl *gomock.Controller) *MockyabsURLBuilder {
	mock := &MockyabsURLBuilder{ctrl: ctrl}
	mock.recorder = &MockyabsURLBuilderMockRecorder{mock}
	return mock
}

// EXPECT returns an object that allows the caller to indicate expected use.
func (m *MockyabsURLBuilder) EXPECT() *MockyabsURLBuilderMockRecorder {
	return m.recorder
}

// BuildRequest mocks base method.
func (m *MockyabsURLBuilder) BuildRequest(ctx contexts.Base) yabs.Request {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "BuildRequest", ctx)
	ret0, _ := ret[0].(yabs.Request)
	return ret0
}

// BuildRequest indicates an expected call of BuildRequest.
func (mr *MockyabsURLBuilderMockRecorder) BuildRequest(ctx interface{}) *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "BuildRequest", reflect.TypeOf((*MockyabsURLBuilder)(nil).BuildRequest), ctx)
}

// MockbigBURLBuilder is a mock of bigBURLBuilder interface.
type MockbigBURLBuilder struct {
	ctrl     *gomock.Controller
	recorder *MockbigBURLBuilderMockRecorder
}

// MockbigBURLBuilderMockRecorder is the mock recorder for MockbigBURLBuilder.
type MockbigBURLBuilderMockRecorder struct {
	mock *MockbigBURLBuilder
}

// NewMockbigBURLBuilder creates a new mock instance.
func NewMockbigBURLBuilder(ctrl *gomock.Controller) *MockbigBURLBuilder {
	mock := &MockbigBURLBuilder{ctrl: ctrl}
	mock.recorder = &MockbigBURLBuilderMockRecorder{mock}
	return mock
}

// EXPECT returns an object that allows the caller to indicate expected use.
func (m *MockbigBURLBuilder) EXPECT() *MockbigBURLBuilderMockRecorder {
	return m.recorder
}

// BuildRequest mocks base method.
func (m *MockbigBURLBuilder) BuildRequest(auth models.Auth, appInfo models.AppInfo, yaCookies models.YaCookies, logger log3.LoggerAlterable) (*proto.TQueryParams, error) {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "BuildRequest", auth, appInfo, yaCookies, logger)
	ret0, _ := ret[0].(*proto.TQueryParams)
	ret1, _ := ret[1].(error)
	return ret0, ret1
}

// BuildRequest indicates an expected call of BuildRequest.
func (mr *MockbigBURLBuilderMockRecorder) BuildRequest(auth, appInfo, yaCookies, logger interface{}) *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "BuildRequest", reflect.TypeOf((*MockbigBURLBuilder)(nil).BuildRequest), auth, appInfo, yaCookies, logger)
}

// MockbaseComparator is a mock of baseComparator interface.
type MockbaseComparator struct {
	ctrl     *gomock.Controller
	recorder *MockbaseComparatorMockRecorder
}

// MockbaseComparatorMockRecorder is the mock recorder for MockbaseComparator.
type MockbaseComparatorMockRecorder struct {
	mock *MockbaseComparator
}

// NewMockbaseComparator creates a new mock instance.
func NewMockbaseComparator(ctrl *gomock.Controller) *MockbaseComparator {
	mock := &MockbaseComparator{ctrl: ctrl}
	mock.recorder = &MockbaseComparatorMockRecorder{mock}
	return mock
}

// EXPECT returns an object that allows the caller to indicate expected use.
func (m *MockbaseComparator) EXPECT() *MockbaseComparatorMockRecorder {
	return m.recorder
}

// CompareContext mocks base method.
func (m *MockbaseComparator) CompareContext(expected compare.ComparableContextExpected, got compare.ForceableContextGot) []error {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "CompareContext", expected, got)
	ret0, _ := ret[0].([]error)
	return ret0
}

// CompareContext indicates an expected call of CompareContext.
func (mr *MockbaseComparatorMockRecorder) CompareContext(expected, got interface{}) *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "CompareContext", reflect.TypeOf((*MockbaseComparator)(nil).CompareContext), expected, got)
}

// MockforceableContextGot is a mock of forceableContextGot interface.
type MockforceableContextGot struct {
	ctrl     *gomock.Controller
	recorder *MockforceableContextGotMockRecorder
}

// MockforceableContextGotMockRecorder is the mock recorder for MockforceableContextGot.
type MockforceableContextGotMockRecorder struct {
	mock *MockforceableContextGot
}

// NewMockforceableContextGot creates a new mock instance.
func NewMockforceableContextGot(ctrl *gomock.Controller) *MockforceableContextGot {
	mock := &MockforceableContextGot{ctrl: ctrl}
	mock.recorder = &MockforceableContextGotMockRecorder{mock}
	return mock
}

// EXPECT returns an object that allows the caller to indicate expected use.
func (m *MockforceableContextGot) EXPECT() *MockforceableContextGotMockRecorder {
	return m.recorder
}

// ForceABFlags mocks base method.
func (m *MockforceableContextGot) ForceABFlags(arg0 models.ABFlags) {
	m.ctrl.T.Helper()
	m.ctrl.Call(m, "ForceABFlags", arg0)
}

// ForceABFlags indicates an expected call of ForceABFlags.
func (mr *MockforceableContextGotMockRecorder) ForceABFlags(arg0 interface{}) *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "ForceABFlags", reflect.TypeOf((*MockforceableContextGot)(nil).ForceABFlags), arg0)
}

// ForceAuth mocks base method.
func (m *MockforceableContextGot) ForceAuth(arg0 models.Auth) {
	m.ctrl.T.Helper()
	m.ctrl.Call(m, "ForceAuth", arg0)
}

// ForceAuth indicates an expected call of ForceAuth.
func (mr *MockforceableContextGotMockRecorder) ForceAuth(arg0 interface{}) *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "ForceAuth", reflect.TypeOf((*MockforceableContextGot)(nil).ForceAuth), arg0)
}

// ForceBigB mocks base method.
func (m *MockforceableContextGot) ForceBigB(arg0 models.BigB) {
	m.ctrl.T.Helper()
	m.ctrl.Call(m, "ForceBigB", arg0)
}

// ForceBigB indicates an expected call of ForceBigB.
func (mr *MockforceableContextGotMockRecorder) ForceBigB(arg0 interface{}) *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "ForceBigB", reflect.TypeOf((*MockforceableContextGot)(nil).ForceBigB), arg0)
}

// ForceClid mocks base method.
func (m *MockforceableContextGot) ForceClid(arg0 models.Clid) {
	m.ctrl.T.Helper()
	m.ctrl.Call(m, "ForceClid", arg0)
}

// ForceClid indicates an expected call of ForceClid.
func (mr *MockforceableContextGotMockRecorder) ForceClid(arg0 interface{}) *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "ForceClid", reflect.TypeOf((*MockforceableContextGot)(nil).ForceClid), arg0)
}

// ForceDevice mocks base method.
func (m *MockforceableContextGot) ForceDevice(arg0 models.Device) {
	m.ctrl.T.Helper()
	m.ctrl.Call(m, "ForceDevice", arg0)
}

// ForceDevice indicates an expected call of ForceDevice.
func (mr *MockforceableContextGotMockRecorder) ForceDevice(arg0 interface{}) *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "ForceDevice", reflect.TypeOf((*MockforceableContextGot)(nil).ForceDevice), arg0)
}

// ForceGeo mocks base method.
func (m *MockforceableContextGot) ForceGeo(arg0 models.Geo) {
	m.ctrl.T.Helper()
	m.ctrl.Call(m, "ForceGeo", arg0)
}

// ForceGeo indicates an expected call of ForceGeo.
func (mr *MockforceableContextGotMockRecorder) ForceGeo(arg0 interface{}) *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "ForceGeo", reflect.TypeOf((*MockforceableContextGot)(nil).ForceGeo), arg0)
}

// ForceLocale mocks base method.
func (m *MockforceableContextGot) ForceLocale(arg0 models.Locale) {
	m.ctrl.T.Helper()
	m.ctrl.Call(m, "ForceLocale", arg0)
}

// ForceLocale indicates an expected call of ForceLocale.
func (mr *MockforceableContextGotMockRecorder) ForceLocale(arg0 interface{}) *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "ForceLocale", reflect.TypeOf((*MockforceableContextGot)(nil).ForceLocale), arg0)
}

// ForceMordaContent mocks base method.
func (m *MockforceableContextGot) ForceMordaContent(arg0 models.MordaContent) {
	m.ctrl.T.Helper()
	m.ctrl.Call(m, "ForceMordaContent", arg0)
}

// ForceMordaContent indicates an expected call of ForceMordaContent.
func (mr *MockforceableContextGotMockRecorder) ForceMordaContent(arg0 interface{}) *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "ForceMordaContent", reflect.TypeOf((*MockforceableContextGot)(nil).ForceMordaContent), arg0)
}

// ForceMordaZone mocks base method.
func (m *MockforceableContextGot) ForceMordaZone(arg0 models.MordaZone) {
	m.ctrl.T.Helper()
	m.ctrl.Call(m, "ForceMordaZone", arg0)
}

// ForceMordaZone indicates an expected call of ForceMordaZone.
func (mr *MockforceableContextGotMockRecorder) ForceMordaZone(arg0 interface{}) *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "ForceMordaZone", reflect.TypeOf((*MockforceableContextGot)(nil).ForceMordaZone), arg0)
}

// ForceRobot mocks base method.
func (m *MockforceableContextGot) ForceRobot(arg0 models.Robot) {
	m.ctrl.T.Helper()
	m.ctrl.Call(m, "ForceRobot", arg0)
}

// ForceRobot indicates an expected call of ForceRobot.
func (mr *MockforceableContextGotMockRecorder) ForceRobot(arg0 interface{}) *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "ForceRobot", reflect.TypeOf((*MockforceableContextGot)(nil).ForceRobot), arg0)
}

// ForceYabs mocks base method.
func (m *MockforceableContextGot) ForceYabs(arg0 models.Yabs) {
	m.ctrl.T.Helper()
	m.ctrl.Call(m, "ForceYabs", arg0)
}

// ForceYabs indicates an expected call of ForceYabs.
func (mr *MockforceableContextGotMockRecorder) ForceYabs(arg0 interface{}) *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "ForceYabs", reflect.TypeOf((*MockforceableContextGot)(nil).ForceYabs), arg0)
}

// ForceYandexUID mocks base method.
func (m *MockforceableContextGot) ForceYandexUID(arg0 string) {
	m.ctrl.T.Helper()
	m.ctrl.Call(m, "ForceYandexUID", arg0)
}

// ForceYandexUID indicates an expected call of ForceYandexUID.
func (mr *MockforceableContextGotMockRecorder) ForceYandexUID(arg0 interface{}) *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "ForceYandexUID", reflect.TypeOf((*MockforceableContextGot)(nil).ForceYandexUID), arg0)
}

// GetAADB mocks base method.
func (m *MockforceableContextGot) GetAADB() models.AADB {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetAADB")
	ret0, _ := ret[0].(models.AADB)
	return ret0
}

// GetAADB indicates an expected call of GetAADB.
func (mr *MockforceableContextGotMockRecorder) GetAADB() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetAADB", reflect.TypeOf((*MockforceableContextGot)(nil).GetAADB))
}

// GetAppInfo mocks base method.
func (m *MockforceableContextGot) GetAppInfo() models.AppInfo {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetAppInfo")
	ret0, _ := ret[0].(models.AppInfo)
	return ret0
}

// GetAppInfo indicates an expected call of GetAppInfo.
func (mr *MockforceableContextGotMockRecorder) GetAppInfo() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetAppInfo", reflect.TypeOf((*MockforceableContextGot)(nil).GetAppInfo))
}

// GetAuth mocks base method.
func (m *MockforceableContextGot) GetAuth() models.Auth {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetAuth")
	ret0, _ := ret[0].(models.Auth)
	return ret0
}

// GetAuth indicates an expected call of GetAuth.
func (mr *MockforceableContextGotMockRecorder) GetAuth() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetAuth", reflect.TypeOf((*MockforceableContextGot)(nil).GetAuth))
}

// GetAuthOrErr mocks base method.
func (m *MockforceableContextGot) GetAuthOrErr() (models.Auth, error) {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetAuthOrErr")
	ret0, _ := ret[0].(models.Auth)
	ret1, _ := ret[1].(error)
	return ret0, ret1
}

// GetAuthOrErr indicates an expected call of GetAuthOrErr.
func (mr *MockforceableContextGotMockRecorder) GetAuthOrErr() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetAuthOrErr", reflect.TypeOf((*MockforceableContextGot)(nil).GetAuthOrErr))
}

// GetBigB mocks base method.
func (m *MockforceableContextGot) GetBigB() models.BigB {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetBigB")
	ret0, _ := ret[0].(models.BigB)
	return ret0
}

// GetBigB indicates an expected call of GetBigB.
func (mr *MockforceableContextGotMockRecorder) GetBigB() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetBigB", reflect.TypeOf((*MockforceableContextGot)(nil).GetBigB))
}

// GetBigBOrErr mocks base method.
func (m *MockforceableContextGot) GetBigBOrErr() (models.BigB, error) {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetBigBOrErr")
	ret0, _ := ret[0].(models.BigB)
	ret1, _ := ret[1].(error)
	return ret0, ret1
}

// GetBigBOrErr indicates an expected call of GetBigBOrErr.
func (mr *MockforceableContextGotMockRecorder) GetBigBOrErr() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetBigBOrErr", reflect.TypeOf((*MockforceableContextGot)(nil).GetBigBOrErr))
}

// GetBigBURL mocks base method.
func (m *MockforceableContextGot) GetBigBURL() *proto.TQueryParams {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetBigBURL")
	ret0, _ := ret[0].(*proto.TQueryParams)
	return ret0
}

// GetBigBURL indicates an expected call of GetBigBURL.
func (mr *MockforceableContextGotMockRecorder) GetBigBURL() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetBigBURL", reflect.TypeOf((*MockforceableContextGot)(nil).GetBigBURL))
}

// GetCSP mocks base method.
func (m *MockforceableContextGot) GetCSP() models.CSP {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetCSP")
	ret0, _ := ret[0].(models.CSP)
	return ret0
}

// GetCSP indicates an expected call of GetCSP.
func (mr *MockforceableContextGotMockRecorder) GetCSP() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetCSP", reflect.TypeOf((*MockforceableContextGot)(nil).GetCSP))
}

// GetClid mocks base method.
func (m *MockforceableContextGot) GetClid() models.Clid {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetClid")
	ret0, _ := ret[0].(models.Clid)
	return ret0
}

// GetClid indicates an expected call of GetClid.
func (mr *MockforceableContextGotMockRecorder) GetClid() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetClid", reflect.TypeOf((*MockforceableContextGot)(nil).GetClid))
}

// GetCookie mocks base method.
func (m *MockforceableContextGot) GetCookie() models.Cookie {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetCookie")
	ret0, _ := ret[0].(models.Cookie)
	return ret0
}

// GetCookie indicates an expected call of GetCookie.
func (mr *MockforceableContextGotMockRecorder) GetCookie() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetCookie", reflect.TypeOf((*MockforceableContextGot)(nil).GetCookie))
}

// GetDevice mocks base method.
func (m *MockforceableContextGot) GetDevice() models.Device {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetDevice")
	ret0, _ := ret[0].(models.Device)
	return ret0
}

// GetDevice indicates an expected call of GetDevice.
func (mr *MockforceableContextGotMockRecorder) GetDevice() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetDevice", reflect.TypeOf((*MockforceableContextGot)(nil).GetDevice))
}

// GetDeviceOrErr mocks base method.
func (m *MockforceableContextGot) GetDeviceOrErr() (models.Device, error) {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetDeviceOrErr")
	ret0, _ := ret[0].(models.Device)
	ret1, _ := ret[1].(error)
	return ret0, ret1
}

// GetDeviceOrErr indicates an expected call of GetDeviceOrErr.
func (mr *MockforceableContextGotMockRecorder) GetDeviceOrErr() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetDeviceOrErr", reflect.TypeOf((*MockforceableContextGot)(nil).GetDeviceOrErr))
}

// GetDomain mocks base method.
func (m *MockforceableContextGot) GetDomain() models.Domain {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetDomain")
	ret0, _ := ret[0].(models.Domain)
	return ret0
}

// GetDomain indicates an expected call of GetDomain.
func (mr *MockforceableContextGotMockRecorder) GetDomain() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetDomain", reflect.TypeOf((*MockforceableContextGot)(nil).GetDomain))
}

// GetFlags mocks base method.
func (m *MockforceableContextGot) GetFlags() models.ABFlags {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetFlags")
	ret0, _ := ret[0].(models.ABFlags)
	return ret0
}

// GetFlags indicates an expected call of GetFlags.
func (mr *MockforceableContextGotMockRecorder) GetFlags() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetFlags", reflect.TypeOf((*MockforceableContextGot)(nil).GetFlags))
}

// GetFlagsOrErr mocks base method.
func (m *MockforceableContextGot) GetFlagsOrErr() (models.ABFlags, error) {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetFlagsOrErr")
	ret0, _ := ret[0].(models.ABFlags)
	ret1, _ := ret[1].(error)
	return ret0, ret1
}

// GetFlagsOrErr indicates an expected call of GetFlagsOrErr.
func (mr *MockforceableContextGotMockRecorder) GetFlagsOrErr() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetFlagsOrErr", reflect.TypeOf((*MockforceableContextGot)(nil).GetFlagsOrErr))
}

// GetGeo mocks base method.
func (m *MockforceableContextGot) GetGeo() models.Geo {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetGeo")
	ret0, _ := ret[0].(models.Geo)
	return ret0
}

// GetGeo indicates an expected call of GetGeo.
func (mr *MockforceableContextGotMockRecorder) GetGeo() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetGeo", reflect.TypeOf((*MockforceableContextGot)(nil).GetGeo))
}

// GetGeoOrErr mocks base method.
func (m *MockforceableContextGot) GetGeoOrErr() (models.Geo, error) {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetGeoOrErr")
	ret0, _ := ret[0].(models.Geo)
	ret1, _ := ret[1].(error)
	return ret0, ret1
}

// GetGeoOrErr indicates an expected call of GetGeoOrErr.
func (mr *MockforceableContextGotMockRecorder) GetGeoOrErr() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetGeoOrErr", reflect.TypeOf((*MockforceableContextGot)(nil).GetGeoOrErr))
}

// GetLocale mocks base method.
func (m *MockforceableContextGot) GetLocale() models.Locale {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetLocale")
	ret0, _ := ret[0].(models.Locale)
	return ret0
}

// GetLocale indicates an expected call of GetLocale.
func (mr *MockforceableContextGotMockRecorder) GetLocale() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetLocale", reflect.TypeOf((*MockforceableContextGot)(nil).GetLocale))
}

// GetLogger mocks base method.
func (m *MockforceableContextGot) GetLogger() log3.LoggerAlterable {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetLogger")
	ret0, _ := ret[0].(log3.LoggerAlterable)
	return ret0
}

// GetLogger indicates an expected call of GetLogger.
func (mr *MockforceableContextGotMockRecorder) GetLogger() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetLogger", reflect.TypeOf((*MockforceableContextGot)(nil).GetLogger))
}

// GetMadmContent mocks base method.
func (m *MockforceableContextGot) GetMadmContent() models.MadmContent {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetMadmContent")
	ret0, _ := ret[0].(models.MadmContent)
	return ret0
}

// GetMadmContent indicates an expected call of GetMadmContent.
func (mr *MockforceableContextGotMockRecorder) GetMadmContent() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetMadmContent", reflect.TypeOf((*MockforceableContextGot)(nil).GetMadmContent))
}

// GetMadmOptions mocks base method.
func (m *MockforceableContextGot) GetMadmOptions() exports.Options {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetMadmOptions")
	ret0, _ := ret[0].(exports.Options)
	return ret0
}

// GetMadmOptions indicates an expected call of GetMadmOptions.
func (mr *MockforceableContextGotMockRecorder) GetMadmOptions() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetMadmOptions", reflect.TypeOf((*MockforceableContextGot)(nil).GetMadmOptions))
}

// GetMordaContent mocks base method.
func (m *MockforceableContextGot) GetMordaContent() models.MordaContent {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetMordaContent")
	ret0, _ := ret[0].(models.MordaContent)
	return ret0
}

// GetMordaContent indicates an expected call of GetMordaContent.
func (mr *MockforceableContextGotMockRecorder) GetMordaContent() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetMordaContent", reflect.TypeOf((*MockforceableContextGot)(nil).GetMordaContent))
}

// GetMordaZone mocks base method.
func (m *MockforceableContextGot) GetMordaZone() models.MordaZone {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetMordaZone")
	ret0, _ := ret[0].(models.MordaZone)
	return ret0
}

// GetMordaZone indicates an expected call of GetMordaZone.
func (mr *MockforceableContextGotMockRecorder) GetMordaZone() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetMordaZone", reflect.TypeOf((*MockforceableContextGot)(nil).GetMordaZone))
}

// GetOriginRequest mocks base method.
func (m *MockforceableContextGot) GetOriginRequest() (*models.OriginRequest, error) {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetOriginRequest")
	ret0, _ := ret[0].(*models.OriginRequest)
	ret1, _ := ret[1].(error)
	return ret0, ret1
}

// GetOriginRequest indicates an expected call of GetOriginRequest.
func (mr *MockforceableContextGotMockRecorder) GetOriginRequest() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetOriginRequest", reflect.TypeOf((*MockforceableContextGot)(nil).GetOriginRequest))
}

// GetPerlAuthInfo mocks base method.
func (m *MockforceableContextGot) GetPerlAuthInfo() (blackbox.AuthInfo, error) {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetPerlAuthInfo")
	ret0, _ := ret[0].(blackbox.AuthInfo)
	ret1, _ := ret[1].(error)
	return ret0, ret1
}

// GetPerlAuthInfo indicates an expected call of GetPerlAuthInfo.
func (mr *MockforceableContextGotMockRecorder) GetPerlAuthInfo() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetPerlAuthInfo", reflect.TypeOf((*MockforceableContextGot)(nil).GetPerlAuthInfo))
}

// GetPerlScaleFactor mocks base method.
func (m *MockforceableContextGot) GetPerlScaleFactor() float32 {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetPerlScaleFactor")
	ret0, _ := ret[0].(float32)
	return ret0
}

// GetPerlScaleFactor indicates an expected call of GetPerlScaleFactor.
func (mr *MockforceableContextGotMockRecorder) GetPerlScaleFactor() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetPerlScaleFactor", reflect.TypeOf((*MockforceableContextGot)(nil).GetPerlScaleFactor))
}

// GetReqTime mocks base method.
func (m *MockforceableContextGot) GetReqTime() map[string]interface{} {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetReqTime")
	ret0, _ := ret[0].(map[string]interface{})
	return ret0
}

// GetReqTime indicates an expected call of GetReqTime.
func (mr *MockforceableContextGotMockRecorder) GetReqTime() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetReqTime", reflect.TypeOf((*MockforceableContextGot)(nil).GetReqTime))
}

// GetRequest mocks base method.
func (m *MockforceableContextGot) GetRequest() models.Request {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetRequest")
	ret0, _ := ret[0].(models.Request)
	return ret0
}

// GetRequest indicates an expected call of GetRequest.
func (mr *MockforceableContextGotMockRecorder) GetRequest() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetRequest", reflect.TypeOf((*MockforceableContextGot)(nil).GetRequest))
}

// GetRobot mocks base method.
func (m *MockforceableContextGot) GetRobot() models.Robot {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetRobot")
	ret0, _ := ret[0].(models.Robot)
	return ret0
}

// GetRobot indicates an expected call of GetRobot.
func (mr *MockforceableContextGotMockRecorder) GetRobot() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetRobot", reflect.TypeOf((*MockforceableContextGot)(nil).GetRobot))
}

// GetRobotOrErr mocks base method.
func (m *MockforceableContextGot) GetRobotOrErr() (models.Robot, error) {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetRobotOrErr")
	ret0, _ := ret[0].(models.Robot)
	ret1, _ := ret[1].(error)
	return ret0, ret1
}

// GetRobotOrErr indicates an expected call of GetRobotOrErr.
func (mr *MockforceableContextGotMockRecorder) GetRobotOrErr() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetRobotOrErr", reflect.TypeOf((*MockforceableContextGot)(nil).GetRobotOrErr))
}

// GetTime mocks base method.
func (m *MockforceableContextGot) GetTime() *models.TimeData {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetTime")
	ret0, _ := ret[0].(*models.TimeData)
	return ret0
}

// GetTime indicates an expected call of GetTime.
func (mr *MockforceableContextGotMockRecorder) GetTime() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetTime", reflect.TypeOf((*MockforceableContextGot)(nil).GetTime))
}

// GetYaCookies mocks base method.
func (m *MockforceableContextGot) GetYaCookies() models.YaCookies {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetYaCookies")
	ret0, _ := ret[0].(models.YaCookies)
	return ret0
}

// GetYaCookies indicates an expected call of GetYaCookies.
func (mr *MockforceableContextGotMockRecorder) GetYaCookies() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetYaCookies", reflect.TypeOf((*MockforceableContextGot)(nil).GetYaCookies))
}

// GetYaCookiesOrErr mocks base method.
func (m *MockforceableContextGot) GetYaCookiesOrErr() (models.YaCookies, error) {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetYaCookiesOrErr")
	ret0, _ := ret[0].(models.YaCookies)
	ret1, _ := ret[1].(error)
	return ret0, ret1
}

// GetYaCookiesOrErr indicates an expected call of GetYaCookiesOrErr.
func (mr *MockforceableContextGotMockRecorder) GetYaCookiesOrErr() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetYaCookiesOrErr", reflect.TypeOf((*MockforceableContextGot)(nil).GetYaCookiesOrErr))
}

// GetYabs mocks base method.
func (m *MockforceableContextGot) GetYabs() models.Yabs {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetYabs")
	ret0, _ := ret[0].(models.Yabs)
	return ret0
}

// GetYabs indicates an expected call of GetYabs.
func (mr *MockforceableContextGotMockRecorder) GetYabs() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetYabs", reflect.TypeOf((*MockforceableContextGot)(nil).GetYabs))
}

// GetYabsOrErr mocks base method.
func (m *MockforceableContextGot) GetYabsOrErr() (models.Yabs, error) {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetYabsOrErr")
	ret0, _ := ret[0].(models.Yabs)
	ret1, _ := ret[1].(error)
	return ret0, ret1
}

// GetYabsOrErr indicates an expected call of GetYabsOrErr.
func (mr *MockforceableContextGotMockRecorder) GetYabsOrErr() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetYabsOrErr", reflect.TypeOf((*MockforceableContextGot)(nil).GetYabsOrErr))
}

// GetYabsURL mocks base method.
func (m *MockforceableContextGot) GetYabsURL() yabs.Request {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "GetYabsURL")
	ret0, _ := ret[0].(yabs.Request)
	return ret0
}

// GetYabsURL indicates an expected call of GetYabsURL.
func (mr *MockforceableContextGotMockRecorder) GetYabsURL() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetYabsURL", reflect.TypeOf((*MockforceableContextGot)(nil).GetYabsURL))
}

// IsSID669ByAuth mocks base method.
func (m *MockforceableContextGot) IsSID669ByAuth() bool {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "IsSID669ByAuth")
	ret0, _ := ret[0].(bool)
	return ret0
}

// IsSID669ByAuth indicates an expected call of IsSID669ByAuth.
func (mr *MockforceableContextGotMockRecorder) IsSID669ByAuth() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "IsSID669ByAuth", reflect.TypeOf((*MockforceableContextGot)(nil).IsSID669ByAuth))
}

// RefreshABFlags mocks base method.
func (m *MockforceableContextGot) RefreshABFlags() {
	m.ctrl.T.Helper()
	m.ctrl.Call(m, "RefreshABFlags")
}

// RefreshABFlags indicates an expected call of RefreshABFlags.
func (mr *MockforceableContextGotMockRecorder) RefreshABFlags() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "RefreshABFlags", reflect.TypeOf((*MockforceableContextGot)(nil).RefreshABFlags))
}

// RefreshLocale mocks base method.
func (m *MockforceableContextGot) RefreshLocale() {
	m.ctrl.T.Helper()
	m.ctrl.Call(m, "RefreshLocale")
}

// RefreshLocale indicates an expected call of RefreshLocale.
func (mr *MockforceableContextGotMockRecorder) RefreshLocale() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "RefreshLocale", reflect.TypeOf((*MockforceableContextGot)(nil).RefreshLocale))
}

// RefreshMadmContent mocks base method.
func (m *MockforceableContextGot) RefreshMadmContent() {
	m.ctrl.T.Helper()
	m.ctrl.Call(m, "RefreshMadmContent")
}

// RefreshMadmContent indicates an expected call of RefreshMadmContent.
func (mr *MockforceableContextGotMockRecorder) RefreshMadmContent() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "RefreshMadmContent", reflect.TypeOf((*MockforceableContextGot)(nil).RefreshMadmContent))
}

// RefreshMordaZone mocks base method.
func (m *MockforceableContextGot) RefreshMordaZone() {
	m.ctrl.T.Helper()
	m.ctrl.Call(m, "RefreshMordaZone")
}

// RefreshMordaZone indicates an expected call of RefreshMordaZone.
func (mr *MockforceableContextGotMockRecorder) RefreshMordaZone() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "RefreshMordaZone", reflect.TypeOf((*MockforceableContextGot)(nil).RefreshMordaZone))
}

// RefreshTimeLocation mocks base method.
func (m *MockforceableContextGot) RefreshTimeLocation() {
	m.ctrl.T.Helper()
	m.ctrl.Call(m, "RefreshTimeLocation")
}

// RefreshTimeLocation indicates an expected call of RefreshTimeLocation.
func (mr *MockforceableContextGotMockRecorder) RefreshTimeLocation() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "RefreshTimeLocation", reflect.TypeOf((*MockforceableContextGot)(nil).RefreshTimeLocation))
}

// SetIsStaffLogin mocks base method.
func (m *MockforceableContextGot) SetIsStaffLogin() {
	m.ctrl.T.Helper()
	m.ctrl.Call(m, "SetIsStaffLogin")
}

// SetIsStaffLogin indicates an expected call of SetIsStaffLogin.
func (mr *MockforceableContextGotMockRecorder) SetIsStaffLogin() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "SetIsStaffLogin", reflect.TypeOf((*MockforceableContextGot)(nil).SetIsStaffLogin))
}

// SyncTime mocks base method.
func (m *MockforceableContextGot) SyncTime(arg0 int64) {
	m.ctrl.T.Helper()
	m.ctrl.Call(m, "SyncTime", arg0)
}

// SyncTime indicates an expected call of SyncTime.
func (mr *MockforceableContextGotMockRecorder) SyncTime(arg0 interface{}) *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "SyncTime", reflect.TypeOf((*MockforceableContextGot)(nil).SyncTime), arg0)
}

// WarmCache mocks base method.
func (m *MockforceableContextGot) WarmCache() error {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "WarmCache")
	ret0, _ := ret[0].(error)
	return ret0
}

// WarmCache indicates an expected call of WarmCache.
func (mr *MockforceableContextGotMockRecorder) WarmCache() *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "WarmCache", reflect.TypeOf((*MockforceableContextGot)(nil).WarmCache))
}
