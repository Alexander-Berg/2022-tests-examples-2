// Code generated by mockery v2.14.0. DO NOT EDIT.

package mocks

import (
	models "a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	mock "github.com/stretchr/testify/mock"
)

// yabsGetter is an autogenerated mock type for the yabsGetter type
type yabsGetter struct {
	mock.Mock
}

// GetYabs provides a mock function with given fields:
func (_m *yabsGetter) GetYabs() models.Yabs {
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
func (_m *yabsGetter) GetYabsOrErr() (models.Yabs, error) {
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

type mockConstructorTestingTnewYabsGetter interface {
	mock.TestingT
	Cleanup(func())
}

// newYabsGetter creates a new instance of yabsGetter. It also registers a testing interface on the mock and a cleanup function to assert the mocks expectations.
func newYabsGetter(t mockConstructorTestingTnewYabsGetter) *yabsGetter {
	mock := &yabsGetter{}
	mock.Mock.Test(t)

	t.Cleanup(func() { mock.AssertExpectations(t) })

	return mock
}