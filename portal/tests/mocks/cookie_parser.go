// Code generated by mockery 2.9.4. DO NOT EDIT.

package mocks

import (
	http "net/http"

	morda_data "a.yandex-team.ru/portal/avocado/proto/morda_data"
	mock "github.com/stretchr/testify/mock"
)

// CookieParser is an autogenerated mock type for the CookieParser type
type CookieParser struct {
	mock.Mock
}

// JoinHTTP provides a mock function with given fields: _a0
func (_m *CookieParser) JoinHTTP(_a0 []*http.Cookie) string {
	ret := _m.Called(_a0)

	var r0 string
	if rf, ok := ret.Get(0).(func([]*http.Cookie) string); ok {
		r0 = rf(_a0)
	} else {
		r0 = ret.Get(0).(string)
	}

	return r0
}

// Parse provides a mock function with given fields: raw
func (_m *CookieParser) Parse(raw string) *morda_data.Cookie {
	ret := _m.Called(raw)

	var r0 *morda_data.Cookie
	if rf, ok := ret.Get(0).(func(string) *morda_data.Cookie); ok {
		r0 = rf(raw)
	} else {
		if ret.Get(0) != nil {
			r0 = ret.Get(0).(*morda_data.Cookie)
		}
	}

	return r0
}

// ParseInHTTP provides a mock function with given fields: raw
func (_m *CookieParser) ParseInHTTP(raw string) []*http.Cookie {
	ret := _m.Called(raw)

	var r0 []*http.Cookie
	if rf, ok := ret.Get(0).(func(string) []*http.Cookie); ok {
		r0 = rf(raw)
	} else {
		if ret.Get(0) != nil {
			r0 = ret.Get(0).([]*http.Cookie)
		}
	}

	return r0
}