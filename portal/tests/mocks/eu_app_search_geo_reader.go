// Code generated by mockery v2.12.2. DO NOT EDIT.

package mocks

import (
	testing "testing"

	models "a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	mock "github.com/stretchr/testify/mock"
)

// EUAppSearchGeoReader is an autogenerated mock type for the EUAppSearchGeoReader type
type EUAppSearchGeoReader struct {
	mock.Mock
}

// IsAppSearchShort provides a mock function with given fields: appInfo, apiInfo, geos
func (_m *EUAppSearchGeoReader) IsAppSearchShort(appInfo models.AppInfo, apiInfo models.APIInfo, geos []uint32) bool {
	ret := _m.Called(appInfo, apiInfo, geos)

	var r0 bool
	if rf, ok := ret.Get(0).(func(models.AppInfo, models.APIInfo, []uint32) bool); ok {
		r0 = rf(appInfo, apiInfo, geos)
	} else {
		r0 = ret.Get(0).(bool)
	}

	return r0
}

// NewEUAppSearchGeoReader creates a new instance of EUAppSearchGeoReader. It also registers the testing.TB interface on the mock and a cleanup function to assert the mocks expectations.
func NewEUAppSearchGeoReader(t testing.TB) *EUAppSearchGeoReader {
	mock := &EUAppSearchGeoReader{}
	mock.Mock.Test(t)

	t.Cleanup(func() { mock.AssertExpectations(t) })

	return mock
}
