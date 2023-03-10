// Code generated by mockery v2.14.0. DO NOT EDIT.

package mocks

import (
	blackbox "a.yandex-team.ru/portal/avocado/libs/utils/blackbox"
	contexts "a.yandex-team.ru/portal/avocado/morda-go/pkg/contexts"

	mock "github.com/stretchr/testify/mock"

	protoanswers "a.yandex-team.ru/apphost/lib/proto_answers"

	query_params "a.yandex-team.ru/ads/bsyeti/eagle/collect/proto"
)

// Init is an autogenerated mock type for the Init type
type Init struct {
	mock.Mock
}

// Base provides a mock function with given fields:
func (_m *Init) Base() contexts.Base {
	ret := _m.Called()

	var r0 contexts.Base
	if rf, ok := ret.Get(0).(func() contexts.Base); ok {
		r0 = rf()
	} else {
		if ret.Get(0) != nil {
			r0 = ret.Get(0).(contexts.Base)
		}
	}

	return r0
}

// GetBlackboxResponse provides a mock function with given fields:
func (_m *Init) GetBlackboxResponse() (*protoanswers.THttpResponse, error) {
	ret := _m.Called()

	var r0 *protoanswers.THttpResponse
	if rf, ok := ret.Get(0).(func() *protoanswers.THttpResponse); ok {
		r0 = rf()
	} else {
		if ret.Get(0) != nil {
			r0 = ret.Get(0).(*protoanswers.THttpResponse)
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

// GetYabsResponse provides a mock function with given fields:
func (_m *Init) GetYabsResponse() (*protoanswers.THttpResponse, error) {
	ret := _m.Called()

	var r0 *protoanswers.THttpResponse
	if rf, ok := ret.Get(0).(func() *protoanswers.THttpResponse); ok {
		r0 = rf()
	} else {
		if ret.Get(0) != nil {
			r0 = ret.Get(0).(*protoanswers.THttpResponse)
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

// PutAuthInfo provides a mock function with given fields: authInfo
func (_m *Init) PutAuthInfo(authInfo blackbox.AuthInfo) error {
	ret := _m.Called(authInfo)

	var r0 error
	if rf, ok := ret.Get(0).(func(blackbox.AuthInfo) error); ok {
		r0 = rf(authInfo)
	} else {
		r0 = ret.Error(0)
	}

	return r0
}

// PutBigBRequest provides a mock function with given fields: request
func (_m *Init) PutBigBRequest(request *query_params.TQueryParams) error {
	ret := _m.Called(request)

	var r0 error
	if rf, ok := ret.Get(0).(func(*query_params.TQueryParams) error); ok {
		r0 = rf(request)
	} else {
		r0 = ret.Error(0)
	}

	return r0
}

// PutBlackboxRequest provides a mock function with given fields: request
func (_m *Init) PutBlackboxRequest(request *protoanswers.THttpRequest) error {
	ret := _m.Called(request)

	var r0 error
	if rf, ok := ret.Get(0).(func(*protoanswers.THttpRequest) error); ok {
		r0 = rf(request)
	} else {
		r0 = ret.Error(0)
	}

	return r0
}

// PutFinalResponse provides a mock function with given fields: response
func (_m *Init) PutFinalResponse(response *protoanswers.THttpResponse) error {
	ret := _m.Called(response)

	var r0 error
	if rf, ok := ret.Get(0).(func(*protoanswers.THttpResponse) error); ok {
		r0 = rf(response)
	} else {
		r0 = ret.Error(0)
	}

	return r0
}

// PutYabsRequest provides a mock function with given fields: request
func (_m *Init) PutYabsRequest(request *protoanswers.THttpRequest) error {
	ret := _m.Called(request)

	var r0 error
	if rf, ok := ret.Get(0).(func(*protoanswers.THttpRequest) error); ok {
		r0 = rf(request)
	} else {
		r0 = ret.Error(0)
	}

	return r0
}

type mockConstructorTestingTNewInit interface {
	mock.TestingT
	Cleanup(func())
}

// NewInit creates a new instance of Init. It also registers a testing interface on the mock and a cleanup function to assert the mocks expectations.
func NewInit(t mockConstructorTestingTNewInit) *Init {
	mock := &Init{}
	mock.Mock.Test(t)

	t.Cleanup(func() { mock.AssertExpectations(t) })

	return mock
}
