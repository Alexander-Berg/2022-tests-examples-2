// Code generated by mockery 2.9.4. DO NOT EDIT.

package mocks

import (
	context "context"

	apphost "a.yandex-team.ru/apphost/api/service/go/apphost"

	dto "a.yandex-team.ru/portal/morda-go/pkg/dto"

	http "net/http"

	mock "github.com/stretchr/testify/mock"

	models "a.yandex-team.ru/portal/avocado/libs/utils/base/models"

	protoanswers "a.yandex-team.ru/apphost/lib/proto_answers"

	protoreflect "google.golang.org/protobuf/reflect/protoreflect"
)

// GeohelperContext is an autogenerated mock type for the GeohelperContext type
type GeohelperContext struct {
	mock.Mock
}

// AddBalancingHint provides a mock function with given fields: targetSource, hint
func (_m *GeohelperContext) AddBalancingHint(targetSource string, hint uint64) error {
	ret := _m.Called(targetSource, hint)

	var r0 error
	if rf, ok := ret.Get(0).(func(string, uint64) error); ok {
		r0 = rf(targetSource, hint)
	} else {
		r0 = ret.Error(0)
	}

	return r0
}

// AddFlag provides a mock function with given fields: flag
func (_m *GeohelperContext) AddFlag(flag string) error {
	ret := _m.Called(flag)

	var r0 error
	if rf, ok := ret.Get(0).(func(string) error); ok {
		r0 = rf(flag)
	} else {
		r0 = ret.Error(0)
	}

	return r0
}

// AddJSON provides a mock function with given fields: typ, value
func (_m *GeohelperContext) AddJSON(typ string, value interface{}) error {
	ret := _m.Called(typ, value)

	var r0 error
	if rf, ok := ret.Get(0).(func(string, interface{}) error); ok {
		r0 = rf(typ, value)
	} else {
		r0 = ret.Error(0)
	}

	return r0
}

// AddPB provides a mock function with given fields: typ, value
func (_m *GeohelperContext) AddPB(typ string, value protoreflect.ProtoMessage) error {
	ret := _m.Called(typ, value)

	var r0 error
	if rf, ok := ret.Get(0).(func(string, protoreflect.ProtoMessage) error); ok {
		r0 = rf(typ, value)
	} else {
		r0 = ret.Error(0)
	}

	return r0
}

// ApphostParams provides a mock function with given fields:
func (_m *GeohelperContext) ApphostParams() (apphost.ServiceParams, error) {
	ret := _m.Called()

	var r0 apphost.ServiceParams
	if rf, ok := ret.Get(0).(func() apphost.ServiceParams); ok {
		r0 = rf()
	} else {
		r0 = ret.Get(0).(apphost.ServiceParams)
	}

	var r1 error
	if rf, ok := ret.Get(1).(func() error); ok {
		r1 = rf()
	} else {
		r1 = ret.Error(1)
	}

	return r0, r1
}

// Context provides a mock function with given fields:
func (_m *GeohelperContext) Context() context.Context {
	ret := _m.Called()

	var r0 context.Context
	if rf, ok := ret.Get(0).(func() context.Context); ok {
		r0 = rf()
	} else {
		if ret.Get(0) != nil {
			r0 = ret.Get(0).(context.Context)
		}
	}

	return r0
}

// Flush provides a mock function with given fields:
func (_m *GeohelperContext) Flush() error {
	ret := _m.Called()

	var r0 error
	if rf, ok := ret.Get(0).(func() error); ok {
		r0 = rf()
	} else {
		r0 = ret.Error(0)
	}

	return r0
}

// GUID provides a mock function with given fields:
func (_m *GeohelperContext) GUID() string {
	ret := _m.Called()

	var r0 string
	if rf, ok := ret.Get(0).(func() string); ok {
		r0 = rf()
	} else {
		r0 = ret.Get(0).(string)
	}

	return r0
}

// GetBlackboxResponse provides a mock function with given fields:
func (_m *GeohelperContext) GetBlackboxResponse() (*protoanswers.THttpResponse, error) {
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

// GetBody provides a mock function with given fields:
func (_m *GeohelperContext) GetBody() []byte {
	ret := _m.Called()

	var r0 []byte
	if rf, ok := ret.Get(0).(func() []byte); ok {
		r0 = rf()
	} else {
		if ret.Get(0) != nil {
			r0 = ret.Get(0).([]byte)
		}
	}

	return r0
}

// GetCookies provides a mock function with given fields:
func (_m *GeohelperContext) GetCookies() models.YaCookies {
	ret := _m.Called()

	var r0 models.YaCookies
	if rf, ok := ret.Get(0).(func() models.YaCookies); ok {
		r0 = rf()
	} else {
		r0 = ret.Get(0).(models.YaCookies)
	}

	return r0
}

// GetDivRendererResponse provides a mock function with given fields:
func (_m *GeohelperContext) GetDivRendererResponse() (*dto.GeohelperResponse, error) {
	ret := _m.Called()

	var r0 *dto.GeohelperResponse
	if rf, ok := ret.Get(0).(func() *dto.GeohelperResponse); ok {
		r0 = rf()
	} else {
		if ret.Get(0) != nil {
			r0 = ret.Get(0).(*dto.GeohelperResponse)
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

// GetFailedBlocks provides a mock function with given fields:
func (_m *GeohelperContext) GetFailedBlocks() ([]string, error) {
	ret := _m.Called()

	var r0 []string
	if rf, ok := ret.Get(0).(func() []string); ok {
		r0 = rf()
	} else {
		if ret.Get(0) != nil {
			r0 = ret.Get(0).([]string)
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

// GetGeohelperRawResponse provides a mock function with given fields:
func (_m *GeohelperContext) GetGeohelperRawResponse() (*protoanswers.THttpResponse, error) {
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

// GetGeohelperResponse provides a mock function with given fields:
func (_m *GeohelperContext) GetGeohelperResponse() (*dto.GeohelperResponse, error) {
	ret := _m.Called()

	var r0 *dto.GeohelperResponse
	if rf, ok := ret.Get(0).(func() *dto.GeohelperResponse); ok {
		r0 = rf()
	} else {
		if ret.Get(0) != nil {
			r0 = ret.Get(0).(*dto.GeohelperResponse)
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

// GetHTTPAdapterInputRequest provides a mock function with given fields:
func (_m *GeohelperContext) GetHTTPAdapterInputRequest() (*protoanswers.THttpRequest, error) {
	ret := _m.Called()

	var r0 *protoanswers.THttpRequest
	if rf, ok := ret.Get(0).(func() *protoanswers.THttpRequest); ok {
		r0 = rf()
	} else {
		if ret.Get(0) != nil {
			r0 = ret.Get(0).(*protoanswers.THttpRequest)
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

// GetHeaders provides a mock function with given fields:
func (_m *GeohelperContext) GetHeaders() http.Header {
	ret := _m.Called()

	var r0 http.Header
	if rf, ok := ret.Get(0).(func() http.Header); ok {
		r0 = rf()
	} else {
		if ret.Get(0) != nil {
			r0 = ret.Get(0).(http.Header)
		}
	}

	return r0
}

// GetIP provides a mock function with given fields:
func (_m *GeohelperContext) GetIP() string {
	ret := _m.Called()

	var r0 string
	if rf, ok := ret.Get(0).(func() string); ok {
		r0 = rf()
	} else {
		r0 = ret.Get(0).(string)
	}

	return r0
}

// GetJSONs provides a mock function with given fields: typ, slice
func (_m *GeohelperContext) GetJSONs(typ string, slice interface{}) error {
	ret := _m.Called(typ, slice)

	var r0 error
	if rf, ok := ret.Get(0).(func(string, interface{}) error); ok {
		r0 = rf(typ, slice)
	} else {
		r0 = ret.Error(0)
	}

	return r0
}

// GetOneJSON provides a mock function with given fields: typ, value
func (_m *GeohelperContext) GetOneJSON(typ string, value interface{}) error {
	ret := _m.Called(typ, value)

	var r0 error
	if rf, ok := ret.Get(0).(func(string, interface{}) error); ok {
		r0 = rf(typ, value)
	} else {
		r0 = ret.Error(0)
	}

	return r0
}

// GetOnePB provides a mock function with given fields: typ, value
func (_m *GeohelperContext) GetOnePB(typ string, value protoreflect.ProtoMessage) error {
	ret := _m.Called(typ, value)

	var r0 error
	if rf, ok := ret.Get(0).(func(string, protoreflect.ProtoMessage) error); ok {
		r0 = rf(typ, value)
	} else {
		r0 = ret.Error(0)
	}

	return r0
}

// GetPBs provides a mock function with given fields: typ, slice
func (_m *GeohelperContext) GetPBs(typ string, slice interface{}) error {
	ret := _m.Called(typ, slice)

	var r0 error
	if rf, ok := ret.Get(0).(func(string, interface{}) error); ok {
		r0 = rf(typ, slice)
	} else {
		r0 = ret.Error(0)
	}

	return r0
}

// GetSkippedBlocks provides a mock function with given fields:
func (_m *GeohelperContext) GetSkippedBlocks() ([]string, error) {
	ret := _m.Called()

	var r0 []string
	if rf, ok := ret.Get(0).(func() []string); ok {
		r0 = rf()
	} else {
		if ret.Get(0) != nil {
			r0 = ret.Get(0).([]string)
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

// GetURL provides a mock function with given fields:
func (_m *GeohelperContext) GetURL() string {
	ret := _m.Called()

	var r0 string
	if rf, ok := ret.Get(0).(func() string); ok {
		r0 = rf()
	} else {
		r0 = ret.Get(0).(string)
	}

	return r0
}

// LogWarn provides a mock function with given fields: format, args
func (_m *GeohelperContext) LogWarn(format string, args ...interface{}) {
	var _ca []interface{}
	_ca = append(_ca, format)
	_ca = append(_ca, args...)
	_m.Called(_ca...)
}

// Next provides a mock function with given fields:
func (_m *GeohelperContext) Next() (bool, error) {
	ret := _m.Called()

	var r0 bool
	if rf, ok := ret.Get(0).(func() bool); ok {
		r0 = rf()
	} else {
		r0 = ret.Get(0).(bool)
	}

	var r1 error
	if rf, ok := ret.Get(1).(func() error); ok {
		r1 = rf()
	} else {
		r1 = ret.Error(1)
	}

	return r0, r1
}

// Path provides a mock function with given fields:
func (_m *GeohelperContext) Path() string {
	ret := _m.Called()

	var r0 string
	if rf, ok := ret.Get(0).(func() string); ok {
		r0 = rf()
	} else {
		r0 = ret.Get(0).(string)
	}

	return r0
}

// PutAuth provides a mock function with given fields: auth
func (_m *GeohelperContext) PutAuth(auth dto.Auth) error {
	ret := _m.Called(auth)

	var r0 error
	if rf, ok := ret.Get(0).(func(dto.Auth) error); ok {
		r0 = rf(auth)
	} else {
		r0 = ret.Error(0)
	}

	return r0
}

// PutFailedBlocks provides a mock function with given fields: value
func (_m *GeohelperContext) PutFailedBlocks(value []string) error {
	ret := _m.Called(value)

	var r0 error
	if rf, ok := ret.Get(0).(func([]string) error); ok {
		r0 = rf(value)
	} else {
		r0 = ret.Error(0)
	}

	return r0
}

// PutSkippedBlocks provides a mock function with given fields: value
func (_m *GeohelperContext) PutSkippedBlocks(value []string) error {
	ret := _m.Called(value)

	var r0 error
	if rf, ok := ret.Get(0).(func([]string) error); ok {
		r0 = rf(value)
	} else {
		r0 = ret.Error(0)
	}

	return r0
}

// RUID provides a mock function with given fields:
func (_m *GeohelperContext) RUID() uint64 {
	ret := _m.Called()

	var r0 uint64
	if rf, ok := ret.Get(0).(func() uint64); ok {
		r0 = rf()
	} else {
		r0 = ret.Get(0).(uint64)
	}

	return r0
}

// ReadAll provides a mock function with given fields:
func (_m *GeohelperContext) ReadAll() error {
	ret := _m.Called()

	var r0 error
	if rf, ok := ret.Get(0).(func() error); ok {
		r0 = rf()
	} else {
		r0 = ret.Error(0)
	}

	return r0
}

// ServiceTicket provides a mock function with given fields:
func (_m *GeohelperContext) ServiceTicket() string {
	ret := _m.Called()

	var r0 string
	if rf, ok := ret.Get(0).(func() string); ok {
		r0 = rf()
	} else {
		r0 = ret.Get(0).(string)
	}

	return r0
}

// UserTicket provides a mock function with given fields:
func (_m *GeohelperContext) UserTicket() (string, error) {
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

// WithContext provides a mock function with given fields: ctx
func (_m *GeohelperContext) WithContext(ctx context.Context) apphost.Context {
	ret := _m.Called(ctx)

	var r0 apphost.Context
	if rf, ok := ret.Get(0).(func(context.Context) apphost.Context); ok {
		r0 = rf(ctx)
	} else {
		if ret.Get(0) != nil {
			r0 = ret.Get(0).(apphost.Context)
		}
	}

	return r0
}