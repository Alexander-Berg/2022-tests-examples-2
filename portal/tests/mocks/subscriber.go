// Code generated by mockery v2.12.2. DO NOT EDIT.

package mocks

import (
	madm "a.yandex-team.ru/portal/avocado/libs/utils/madm/v2"
	mock "github.com/stretchr/testify/mock"

	testing "testing"
)

// Subscriber is an autogenerated mock type for the Subscriber type
type Subscriber struct {
	mock.Mock
}

// SubscribeForUpdates provides a mock function with given fields: export, callback
func (_m *Subscriber) SubscribeForUpdates(export madm.ExportName, callback func()) error {
	ret := _m.Called(export, callback)

	var r0 error
	if rf, ok := ret.Get(0).(func(madm.ExportName, func()) error); ok {
		r0 = rf(export, callback)
	} else {
		r0 = ret.Error(0)
	}

	return r0
}

// NewSubscriber creates a new instance of Subscriber. It also registers the testing.TB interface on the mock and a cleanup function to assert the mocks expectations.
func NewSubscriber(t testing.TB) *Subscriber {
	mock := &Subscriber{}
	mock.Mock.Test(t)

	t.Cleanup(func() { mock.AssertExpectations(t) })

	return mock
}
