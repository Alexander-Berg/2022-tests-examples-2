// Code generated by mockery v2.14.0. DO NOT EDIT.

package mocks

import (
	models "a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	mock "github.com/stretchr/testify/mock"
)

// abFlagsGetter is an autogenerated mock type for the abFlagsGetter type
type abFlagsGetter struct {
	mock.Mock
}

// GetFlags provides a mock function with given fields:
func (_m *abFlagsGetter) GetFlags() models.ABFlags {
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
func (_m *abFlagsGetter) GetFlagsOrErr() (models.ABFlags, error) {
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

type mockConstructorTestingTnewAbFlagsGetter interface {
	mock.TestingT
	Cleanup(func())
}

// newAbFlagsGetter creates a new instance of abFlagsGetter. It also registers a testing interface on the mock and a cleanup function to assert the mocks expectations.
func newAbFlagsGetter(t mockConstructorTestingTnewAbFlagsGetter) *abFlagsGetter {
	mock := &abFlagsGetter{}
	mock.Mock.Test(t)

	t.Cleanup(func() { mock.AssertExpectations(t) })

	return mock
}