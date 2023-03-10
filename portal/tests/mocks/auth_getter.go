// Code generated by mockery v2.14.0. DO NOT EDIT.

package mocks

import (
	models "a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	mock "github.com/stretchr/testify/mock"
)

// authGetter is an autogenerated mock type for the authGetter type
type authGetter struct {
	mock.Mock
}

// GetAuth provides a mock function with given fields:
func (_m *authGetter) GetAuth() models.Auth {
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
func (_m *authGetter) GetAuthOrErr() (models.Auth, error) {
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

type mockConstructorTestingTnewAuthGetter interface {
	mock.TestingT
	Cleanup(func())
}

// newAuthGetter creates a new instance of authGetter. It also registers a testing interface on the mock and a cleanup function to assert the mocks expectations.
func newAuthGetter(t mockConstructorTestingTnewAuthGetter) *authGetter {
	mock := &authGetter{}
	mock.Mock.Test(t)

	t.Cleanup(func() { mock.AssertExpectations(t) })

	return mock
}
