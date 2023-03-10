// Code generated by mockery v2.12.2. DO NOT EDIT.

package mocks

import (
	testing "testing"

	mock "github.com/stretchr/testify/mock"
)

// SpokSettings is an autogenerated mock type for the SpokSettings type
type SpokSettings struct {
	mock.Mock
}

// GetSpokDomains provides a mock function with given fields:
func (_m *SpokSettings) GetSpokDomains() []string {
	ret := _m.Called()

	var r0 []string
	if rf, ok := ret.Get(0).(func() []string); ok {
		r0 = rf()
	} else {
		if ret.Get(0) != nil {
			r0 = ret.Get(0).([]string)
		}
	}

	return r0
}

// IsSpokDomain provides a mock function with given fields: domain
func (_m *SpokSettings) IsSpokDomain(domain string) bool {
	ret := _m.Called(domain)

	var r0 bool
	if rf, ok := ret.Get(0).(func(string) bool); ok {
		r0 = rf(domain)
	} else {
		r0 = ret.Get(0).(bool)
	}

	return r0
}

// NewSpokSettings creates a new instance of SpokSettings. It also registers the testing.TB interface on the mock and a cleanup function to assert the mocks expectations.
func NewSpokSettings(t testing.TB) *SpokSettings {
	mock := &SpokSettings{}
	mock.Mock.Test(t)

	t.Cleanup(func() { mock.AssertExpectations(t) })

	return mock
}
