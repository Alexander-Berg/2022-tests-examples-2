package geo

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"

	"a.yandex-team.ru/apphost/api/service/go/apphost"
	"a.yandex-team.ru/portal/avocado/libs/utils/errors/v3"
	"a.yandex-team.ru/portal/avocado/libs/utils/geo/laas"
	"a.yandex-team.ru/portal/avocado/libs/utils/geo/lbs"
	"a.yandex-team.ru/portal/morda-go/tests/mocks"
)

func Test_geoContext_GetLBSLocation(t *testing.T) {
	type fields struct {
		apphostCtx apphost.Context
	}

	tests := []struct {
		name    string
		fields  fields
		wantErr assert.ErrorAssertionFunc
	}{
		{
			name: "success",
			fields: fields{
				apphostCtx: func() *mocks.ApphostContext {
					ctx := &mocks.ApphostContext{}
					ctx.On("GetJSONs", lbsLocationType, mock.Anything).Return(nil)
					return ctx
				}(),
			},
			wantErr: assert.NoError,
		},
		{
			name: "failed",
			fields: fields{
				apphostCtx: func() *mocks.ApphostContext {
					ctx := &mocks.ApphostContext{}
					ctx.On("GetJSONs", lbsLocationType, mock.Anything).Return(errors.Error("error"))
					return ctx
				}(),
			},
			wantErr: assert.Error,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			g := &geoContext{
				apphostCtx: tt.fields.apphostCtx,
			}

			_, err := g.GetLBSLocation()
			tt.wantErr(t, err)
		})
	}
}

func Test_geoContext_AddLAASByGPAutoRequest(t *testing.T) {
	type fields struct {
		apphostCtx apphost.Context
	}

	type args struct {
		request *laas.Request
	}

	tests := []struct {
		name    string
		fields  fields
		args    args
		wantErr assert.ErrorAssertionFunc
	}{
		{
			name: "success",
			fields: fields{
				apphostCtx: func() *mocks.ApphostContext {
					ctx := &mocks.ApphostContext{}
					ctx.On("AddJSON", laasGpAutoRequestType, mock.Anything).Return(nil)
					return ctx
				}(),
			},
			args: args{
				request: &laas.Request{
					Headers: [][]string{
						{"X-Real-Ip", "192.168.0.1"},
						{"Cookie", "ys=gpauto.1:2:85:0:1643302515"},
					},
					Method:   "GET",
					URI:      "/region",
					RemoteIP: "127.0.0.1",
				},
			},
			wantErr: assert.NoError,
		},
		{
			name: "failed",
			fields: fields{
				apphostCtx: func() *mocks.ApphostContext {
					ctx := &mocks.ApphostContext{}
					ctx.On("AddJSON", laasGpAutoRequestType, mock.Anything).Return(errors.Error("error"))
					return ctx
				}(),
			},
			args: args{
				request: &laas.Request{
					Headers: [][]string{
						{"X-Real-Ip", "192.168.0.1"},
						{"Cookie", "ys=gpauto.1:2:85:0:1643302515"},
					},
					Method:   "GET",
					URI:      "/region",
					RemoteIP: "127.0.0.1",
				},
			},
			wantErr: assert.Error,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			g := &geoContext{
				apphostCtx: tt.fields.apphostCtx,
			}

			tt.wantErr(t, g.AddLAASByGPAutoRequest(tt.args.request))
		})
	}
}

func Test_geoContext_AddLBSRequest(t *testing.T) {
	type fields struct {
		apphostCtx apphost.Context
	}

	type args struct {
		request *lbs.Request
	}

	tests := []struct {
		name    string
		fields  fields
		args    args
		wantErr assert.ErrorAssertionFunc
	}{
		{
			name: "success",
			fields: fields{
				apphostCtx: func() *mocks.ApphostContext {
					ctx := &mocks.ApphostContext{}
					ctx.On("AddJSON", lbsRequestType, mock.Anything).Return(nil)
					return ctx
				}(),
			},
			args: args{
				request: &lbs.Request{
					Params: lbs.Params{
						Wifi:   []string{"1:2:3:4"},
						CellID: []string{"5:6:7:8"},
					},
					Headers: make(map[string]string),
					URI:     "GET",
					Method:  "/geolocation",
				},
			},
			wantErr: assert.NoError,
		},
		{
			name: "failed",
			fields: fields{
				apphostCtx: func() *mocks.ApphostContext {
					ctx := &mocks.ApphostContext{}
					ctx.On("AddJSON", lbsRequestType, mock.Anything).Return(errors.Error("error"))
					return ctx
				}(),
			},
			args: args{
				request: &lbs.Request{
					Params: lbs.Params{
						Wifi:   []string{"1:2:3:4"},
						CellID: []string{"5:6:7:8"},
					},
					Headers: make(map[string]string),
					URI:     "GET",
					Method:  "/geolocation",
				},
			},
			wantErr: assert.Error,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			g := &geoContext{
				apphostCtx: tt.fields.apphostCtx,
			}
			tt.wantErr(t, g.AddLBSRequest(tt.args.request))
		})
	}
}

func Test_geoContext_GetLAASResponse(t *testing.T) {
	type fields struct {
		apphostCtx apphost.Context
	}

	tests := []struct {
		name    string
		fields  fields
		want    *laas.Response
		wantErr assert.ErrorAssertionFunc
	}{
		{
			name: "success",
			fields: fields{
				apphostCtx: func() *mocks.ApphostContext {
					ctx := &mocks.ApphostContext{}
					ctx.On("GetJSONs", laasRegionType, mock.Anything).Return(nil)
					return ctx
				}(),
			},
			wantErr: assert.NoError,
		},
		{
			name: "failed",
			fields: fields{
				apphostCtx: func() *mocks.ApphostContext {
					ctx := &mocks.ApphostContext{}
					ctx.On("GetJSONs", laasRegionType, mock.Anything).Return(errors.Error("error"))
					return ctx
				}(),
			},
			wantErr: assert.Error,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			g := &geoContext{
				apphostCtx: tt.fields.apphostCtx,
			}

			_, err := g.GetLAASResponse()
			tt.wantErr(t, err)
		})
	}
}

func Test_geoContext_AddLAASByGPAutoBalancingHint(t *testing.T) {
	type fields struct {
		apphostCtx apphost.Context
	}

	type args struct {
		hint uint64
	}

	tests := []struct {
		name    string
		fields  fields
		args    args
		wantErr assert.ErrorAssertionFunc
	}{
		{
			name: "success",
			fields: fields{
				apphostCtx: func() *mocks.ApphostContext {
					ctx := &mocks.ApphostContext{}
					ctx.On("AddBalancingHint", "LAAS_GPAUTO", mock.Anything).Return(nil)
					return ctx
				}(),
			},
			args: args{
				hint: 123,
			},
			wantErr: assert.NoError,
		},
		{
			name: "failed",
			fields: fields{
				apphostCtx: func() *mocks.ApphostContext {
					ctx := &mocks.ApphostContext{}
					ctx.On("AddBalancingHint", "LAAS_GPAUTO", mock.Anything).Return(nil)
					return ctx
				}(),
			},
			args: args{
				hint: 123,
			},
			wantErr: assert.NoError,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			g := &geoContext{
				apphostCtx: tt.fields.apphostCtx,
			}

			err := g.AddLAASByGPAutoBalancingHint(tt.args.hint)
			tt.wantErr(t, err)
		})
	}
}
