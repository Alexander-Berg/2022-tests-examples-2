// Code generated by mockery v2.12.2. DO NOT EDIT.

package mocks

import (
	filters "a.yandex-team.ru/portal/avocado/libs/utils/madm/filters"
	mock "github.com/stretchr/testify/mock"

	testing "testing"
)

// Filter is an autogenerated mock type for the Filter type
type Filter struct {
	mock.Mock
}

// Evaluate provides a mock function with given fields: ctx
func (_m *Filter) Evaluate(ctx filters.Context) bool {
	ret := _m.Called(ctx)

	var r0 bool
	if rf, ok := ret.Get(0).(func(filters.Context) bool); ok {
		r0 = rf(ctx)
	} else {
		r0 = ret.Get(0).(bool)
	}

	return r0
}

// NewFilter creates a new instance of Filter. It also registers the testing.TB interface on the mock and a cleanup function to assert the mocks expectations.
func NewFilter(t testing.TB) *Filter {
	mock := &Filter{}
	mock.Mock.Test(t)

	t.Cleanup(func() { mock.AssertExpectations(t) })

	return mock
}