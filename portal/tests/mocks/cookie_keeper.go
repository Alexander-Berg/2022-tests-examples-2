// Code generated by mockery v2.9.4. DO NOT EDIT.

package mocks

import (
	morda_data "a.yandex-team.ru/portal/avocado/proto/morda_data"
	mock "github.com/stretchr/testify/mock"
)

// CookieKeeper is an autogenerated mock type for the CookieKeeper type
type CookieKeeper struct {
	mock.Mock
}

// GetCookie provides a mock function with given fields:
func (_m *CookieKeeper) GetCookie() (*morda_data.Cookie, error) {
	ret := _m.Called()

	var r0 *morda_data.Cookie
	if rf, ok := ret.Get(0).(func() *morda_data.Cookie); ok {
		r0 = rf()
	} else {
		if ret.Get(0) != nil {
			r0 = ret.Get(0).(*morda_data.Cookie)
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

// GetCookieIfUpdated provides a mock function with given fields:
func (_m *CookieKeeper) GetCookieIfUpdated() *morda_data.Cookie {
	ret := _m.Called()

	var r0 *morda_data.Cookie
	if rf, ok := ret.Get(0).(func() *morda_data.Cookie); ok {
		r0 = rf()
	} else {
		if ret.Get(0) != nil {
			r0 = ret.Get(0).(*morda_data.Cookie)
		}
	}

	return r0
}

// GetRawCookie provides a mock function with given fields:
func (_m *CookieKeeper) GetRawCookie() (string, error) {
	ret := _m.Called()

	var r0 string
	if rf, ok := ret.Get(0).(func() string); ok {
		r0 = rf()
	} else {
		r0 = ret.Get(0).(string)
	}

	var r1 error
	if rf, ok := ret.Get(1).(func() error); ok {
		r1 = rf()
	} else {
		r1 = ret.Error(1)
	}

	return r0, r1
}