// Code generated by mockery v2.14.0. DO NOT EDIT.

package mocks

import (
	log3 "a.yandex-team.ru/portal/avocado/libs/utils/log3"
	exports "a.yandex-team.ru/portal/avocado/morda-go/pkg/exports"

	mock "github.com/stretchr/testify/mock"

	models "a.yandex-team.ru/portal/avocado/libs/utils/base/models"
)

// BaseWithUpdate is an autogenerated mock type for the BaseWithUpdate type
type BaseWithUpdate struct {
	mock.Mock
}

// GetAADB provides a mock function with given fields:
func (_m *BaseWithUpdate) GetAADB() models.AADB {
	ret := _m.Called()

	var r0 models.AADB
	if rf, ok := ret.Get(0).(func() models.AADB); ok {
		r0 = rf()
	} else {
		r0 = ret.Get(0).(models.AADB)
	}

	return r0
}

// GetAppInfo provides a mock function with given fields:
func (_m *BaseWithUpdate) GetAppInfo() models.AppInfo {
	ret := _m.Called()

	var r0 models.AppInfo
	if rf, ok := ret.Get(0).(func() models.AppInfo); ok {
		r0 = rf()
	} else {
		r0 = ret.Get(0).(models.AppInfo)
	}

	return r0
}

// GetAuth provides a mock function with given fields:
func (_m *BaseWithUpdate) GetAuth() models.Auth {
	ret := _m.Called()

	var r0 models.Auth
	if rf, ok := ret.Get(0).(func() models.Auth); ok {
		r0 = rf()
	} else {
		r0 = ret.Get(0).(models.Auth)
	}

	return r0
}

// GetAuthOrErr provides a mock function with given fields:
func (_m *BaseWithUpdate) GetAuthOrErr() (models.Auth, error) {
	ret := _m.Called()

	var r0 models.Auth
	if rf, ok := ret.Get(0).(func() models.Auth); ok {
		r0 = rf()
	} else {
		r0 = ret.Get(0).(models.Auth)
	}

	var r1 error
	if rf, ok := ret.Get(1).(func() error); ok {
		r1 = rf()
	} else {
		r1 = ret.Error(1)
	}

	return r0, r1
}

// GetBigB provides a mock function with given fields:
func (_m *BaseWithUpdate) GetBigB() models.BigB {
	ret := _m.Called()

	var r0 models.BigB
	if rf, ok := ret.Get(0).(func() models.BigB); ok {
		r0 = rf()
	} else {
		r0 = ret.Get(0).(models.BigB)
	}

	return r0
}

// GetBigBOrErr provides a mock function with given fields:
func (_m *BaseWithUpdate) GetBigBOrErr() (models.BigB, error) {
	ret := _m.Called()

	var r0 models.BigB
	if rf, ok := ret.Get(0).(func() models.BigB); ok {
		r0 = rf()
	} else {
		r0 = ret.Get(0).(models.BigB)
	}

	var r1 error
	if rf, ok := ret.Get(1).(func() error); ok {
		r1 = rf()
	} else {
		r1 = ret.Error(1)
	}

	return r0, r1
}

// GetCSP provides a mock function with given fields:
func (_m *BaseWithUpdate) GetCSP() models.CSP {
	ret := _m.Called()

	var r0 models.CSP
	if rf, ok := ret.Get(0).(func() models.CSP); ok {
		r0 = rf()
	} else {
		r0 = ret.Get(0).(models.CSP)
	}

	return r0
}

// GetClid provides a mock function with given fields:
func (_m *BaseWithUpdate) GetClid() models.Clid {
	ret := _m.Called()

	var r0 models.Clid
	if rf, ok := ret.Get(0).(func() models.Clid); ok {
		r0 = rf()
	} else {
		r0 = ret.Get(0).(models.Clid)
	}

	return r0
}

// GetCookie provides a mock function with given fields:
func (_m *BaseWithUpdate) GetCookie() models.Cookie {
	ret := _m.Called()

	var r0 models.Cookie
	if rf, ok := ret.Get(0).(func() models.Cookie); ok {
		r0 = rf()
	} else {
		r0 = ret.Get(0).(models.Cookie)
	}

	return r0
}

// GetDevice provides a mock function with given fields:
func (_m *BaseWithUpdate) GetDevice() models.Device {
	ret := _m.Called()

	var r0 models.Device
	if rf, ok := ret.Get(0).(func() models.Device); ok {
		r0 = rf()
	} else {
		r0 = ret.Get(0).(models.Device)
	}

	return r0
}

// GetDeviceOrErr provides a mock function with given fields:
func (_m *BaseWithUpdate) GetDeviceOrErr() (models.Device, error) {
	ret := _m.Called()

	var r0 models.Device
	if rf, ok := ret.Get(0).(func() models.Device); ok {
		r0 = rf()
	} else {
		r0 = ret.Get(0).(models.Device)
	}

	var r1 error
	if rf, ok := ret.Get(1).(func() error); ok {
		r1 = rf()
	} else {
		r1 = ret.Error(1)
	}

	return r0, r1
}

// GetDomain provides a mock function with given fields:
func (_m *BaseWithUpdate) GetDomain() models.Domain {
	ret := _m.Called()

	var r0 models.Domain
	if rf, ok := ret.Get(0).(func() models.Domain); ok {
		r0 = rf()
	} else {
		r0 = ret.Get(0).(models.Domain)
	}

	return r0
}

// GetFlags provides a mock function with given fields:
func (_m *BaseWithUpdate) GetFlags() models.ABFlags {
	ret := _m.Called()

	var r0 models.ABFlags
	if rf, ok := ret.Get(0).(func() models.ABFlags); ok {
		r0 = rf()
	} else {
		r0 = ret.Get(0).(models.ABFlags)
	}

	return r0
}

// GetFlagsOrErr provides a mock function with given fields:
func (_m *BaseWithUpdate) GetFlagsOrErr() (models.ABFlags, error) {
	ret := _m.Called()

	var r0 models.ABFlags
	if rf, ok := ret.Get(0).(func() models.ABFlags); ok {
		r0 = rf()
	} else {
		r0 = ret.Get(0).(models.ABFlags)
	}

	var r1 error
	if rf, ok := ret.Get(1).(func() error); ok {
		r1 = rf()
	} else {
		r1 = ret.Error(1)
	}

	return r0, r1
}

// GetGeo provides a mock function with given fields:
func (_m *BaseWithUpdate) GetGeo() models.Geo {
	ret := _m.Called()

	var r0 models.Geo
	if rf, ok := ret.Get(0).(func() models.Geo); ok {
		r0 = rf()
	} else {
		r0 = ret.Get(0).(models.Geo)
	}

	return r0
}

// GetGeoOrErr provides a mock function with given fields:
func (_m *BaseWithUpdate) GetGeoOrErr() (models.Geo, error) {
	ret := _m.Called()

	var r0 models.Geo
	if rf, ok := ret.Get(0).(func() models.Geo); ok {
		r0 = rf()
	} else {
		r0 = ret.Get(0).(models.Geo)
	}

	var r1 error
	if rf, ok := ret.Get(1).(func() error); ok {
		r1 = rf()
	} else {
		r1 = ret.Error(1)
	}

	return r0, r1
}

// GetLocale provides a mock function with given fields:
func (_m *BaseWithUpdate) GetLocale() models.Locale {
	ret := _m.Called()

	var r0 models.Locale
	if rf, ok := ret.Get(0).(func() models.Locale); ok {
		r0 = rf()
	} else {
		r0 = ret.Get(0).(models.Locale)
	}

	return r0
}

// GetLogger provides a mock function with given fields:
func (_m *BaseWithUpdate) GetLogger() log3.LoggerAlterable {
	ret := _m.Called()

	var r0 log3.LoggerAlterable
	if rf, ok := ret.Get(0).(func() log3.LoggerAlterable); ok {
		r0 = rf()
	} else {
		if ret.Get(0) != nil {
			r0 = ret.Get(0).(log3.LoggerAlterable)
		}
	}

	return r0
}

// GetMadmContent provides a mock function with given fields:
func (_m *BaseWithUpdate) GetMadmContent() models.MadmContent {
	ret := _m.Called()

	var r0 models.MadmContent
	if rf, ok := ret.Get(0).(func() models.MadmContent); ok {
		r0 = rf()
	} else {
		r0 = ret.Get(0).(models.MadmContent)
	}

	return r0
}

// GetMadmOptions provides a mock function with given fields:
func (_m *BaseWithUpdate) GetMadmOptions() exports.Options {
	ret := _m.Called()

	var r0 exports.Options
	if rf, ok := ret.Get(0).(func() exports.Options); ok {
		r0 = rf()
	} else {
		r0 = ret.Get(0).(exports.Options)
	}

	return r0
}

// GetMordaContent provides a mock function with given fields:
func (_m *BaseWithUpdate) GetMordaContent() models.MordaContent {
	ret := _m.Called()

	var r0 models.MordaContent
	if rf, ok := ret.Get(0).(func() models.MordaContent); ok {
		r0 = rf()
	} else {
		r0 = ret.Get(0).(models.MordaContent)
	}

	return r0
}

// GetMordaZone provides a mock function with given fields:
func (_m *BaseWithUpdate) GetMordaZone() models.MordaZone {
	ret := _m.Called()

	var r0 models.MordaZone
	if rf, ok := ret.Get(0).(func() models.MordaZone); ok {
		r0 = rf()
	} else {
		r0 = ret.Get(0).(models.MordaZone)
	}

	return r0
}

// GetOriginRequest provides a mock function with given fields:
func (_m *BaseWithUpdate) GetOriginRequest() (*models.OriginRequest, error) {
	ret := _m.Called()

	var r0 *models.OriginRequest
	if rf, ok := ret.Get(0).(func() *models.OriginRequest); ok {
		r0 = rf()
	} else {
		if ret.Get(0) != nil {
			r0 = ret.Get(0).(*models.OriginRequest)
		}
	}

	var r1 error
	if rf, ok := ret.Get(1).(func() error); ok {
		r1 = rf()
	} else {
		r1 = ret.Error(1)
	}

	return r0, r1
}

// GetRequest provides a mock function with given fields:
func (_m *BaseWithUpdate) GetRequest() models.Request {
	ret := _m.Called()

	var r0 models.Request
	if rf, ok := ret.Get(0).(func() models.Request); ok {
		r0 = rf()
	} else {
		r0 = ret.Get(0).(models.Request)
	}

	return r0
}

// GetRobot provides a mock function with given fields:
func (_m *BaseWithUpdate) GetRobot() models.Robot {
	ret := _m.Called()

	var r0 models.Robot
	if rf, ok := ret.Get(0).(func() models.Robot); ok {
		r0 = rf()
	} else {
		r0 = ret.Get(0).(models.Robot)
	}

	return r0
}

// GetRobotOrErr provides a mock function with given fields:
func (_m *BaseWithUpdate) GetRobotOrErr() (models.Robot, error) {
	ret := _m.Called()

	var r0 models.Robot
	if rf, ok := ret.Get(0).(func() models.Robot); ok {
		r0 = rf()
	} else {
		r0 = ret.Get(0).(models.Robot)
	}

	var r1 error
	if rf, ok := ret.Get(1).(func() error); ok {
		r1 = rf()
	} else {
		r1 = ret.Error(1)
	}

	return r0, r1
}

// GetTime provides a mock function with given fields:
func (_m *BaseWithUpdate) GetTime() *models.TimeData {
	ret := _m.Called()

	var r0 *models.TimeData
	if rf, ok := ret.Get(0).(func() *models.TimeData); ok {
		r0 = rf()
	} else {
		if ret.Get(0) != nil {
			r0 = ret.Get(0).(*models.TimeData)
		}
	}

	return r0
}

// GetYaCookies provides a mock function with given fields:
func (_m *BaseWithUpdate) GetYaCookies() models.YaCookies {
	ret := _m.Called()

	var r0 models.YaCookies
	if rf, ok := ret.Get(0).(func() models.YaCookies); ok {
		r0 = rf()
	} else {
		r0 = ret.Get(0).(models.YaCookies)
	}

	return r0
}

// GetYaCookiesOrErr provides a mock function with given fields:
func (_m *BaseWithUpdate) GetYaCookiesOrErr() (models.YaCookies, error) {
	ret := _m.Called()

	var r0 models.YaCookies
	if rf, ok := ret.Get(0).(func() models.YaCookies); ok {
		r0 = rf()
	} else {
		r0 = ret.Get(0).(models.YaCookies)
	}

	var r1 error
	if rf, ok := ret.Get(1).(func() error); ok {
		r1 = rf()
	} else {
		r1 = ret.Error(1)
	}

	return r0, r1
}

// GetYabs provides a mock function with given fields:
func (_m *BaseWithUpdate) GetYabs() models.Yabs {
	ret := _m.Called()

	var r0 models.Yabs
	if rf, ok := ret.Get(0).(func() models.Yabs); ok {
		r0 = rf()
	} else {
		r0 = ret.Get(0).(models.Yabs)
	}

	return r0
}

// GetYabsOrErr provides a mock function with given fields:
func (_m *BaseWithUpdate) GetYabsOrErr() (models.Yabs, error) {
	ret := _m.Called()

	var r0 models.Yabs
	if rf, ok := ret.Get(0).(func() models.Yabs); ok {
		r0 = rf()
	} else {
		r0 = ret.Get(0).(models.Yabs)
	}

	var r1 error
	if rf, ok := ret.Get(1).(func() error); ok {
		r1 = rf()
	} else {
		r1 = ret.Error(1)
	}

	return r0, r1
}

// IsSID669ByAuth provides a mock function with given fields:
func (_m *BaseWithUpdate) IsSID669ByAuth() bool {
	ret := _m.Called()

	var r0 bool
	if rf, ok := ret.Get(0).(func() bool); ok {
		r0 = rf()
	} else {
		r0 = ret.Get(0).(bool)
	}

	return r0
}

// UpdateCache provides a mock function with given fields:
func (_m *BaseWithUpdate) UpdateCache() error {
	ret := _m.Called()

	var r0 error
	if rf, ok := ret.Get(0).(func() error); ok {
		r0 = rf()
	} else {
		r0 = ret.Error(0)
	}

	return r0
}

// WarmCache provides a mock function with given fields:
func (_m *BaseWithUpdate) WarmCache() error {
	ret := _m.Called()

	var r0 error
	if rf, ok := ret.Get(0).(func() error); ok {
		r0 = rf()
	} else {
		r0 = ret.Error(0)
	}

	return r0
}

type mockConstructorTestingTNewBaseWithUpdate interface {
	mock.TestingT
	Cleanup(func())
}

// NewBaseWithUpdate creates a new instance of BaseWithUpdate. It also registers a testing interface on the mock and a cleanup function to assert the mocks expectations.
func NewBaseWithUpdate(t mockConstructorTestingTNewBaseWithUpdate) *BaseWithUpdate {
	mock := &BaseWithUpdate{}
	mock.Mock.Test(t)

	t.Cleanup(func() { mock.AssertExpectations(t) })

	return mock
}
