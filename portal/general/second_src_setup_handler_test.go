package geo

import (
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/libs/utils/errors/v3"
	"a.yandex-team.ru/portal/avocado/libs/utils/geo/lbs"
	"a.yandex-team.ru/portal/avocado/morda-go/tests/mocks"
)

func Test_secondSrcSetupHandler_handle(t *testing.T) {
	type fields struct {
		createHandler func(t *testing.T) *Mockhandler
	}

	type args struct {
		createContext func(t *testing.T) *Mockcontext
		baseCtx       *mocks.Base
	}

	tests := []struct {
		name    string
		fields  fields
		args    args
		wantErr assert.ErrorAssertionFunc
	}{
		{
			name: "get lbs location failed",
			fields: fields{
				createHandler: func(t *testing.T) *Mockhandler {
					return nil
				},
			},
			args: args{
				createContext: func(t *testing.T) *Mockcontext {
					ctx := NewMockcontext(gomock.NewController(t))
					ctx.EXPECT().GetLBSLocation().Return(&lbs.Location{}, errors.Error("error"))
					return ctx
				},
			},
			wantErr: assert.Error,
		},
		{
			name: "lbs location not found",
			fields: fields{
				createHandler: func(t *testing.T) *Mockhandler {
					return nil
				},
			},
			args: args{
				createContext: func(t *testing.T) *Mockcontext {
					ctx := NewMockcontext(gomock.NewController(t))
					ctx.EXPECT().GetLBSLocation().Return(&lbs.Location{
						Found: false,
					}, nil)
					return ctx
				},
			},
			wantErr: assert.NoError,
		},
		{
			name: "get origin request failed",
			fields: fields{
				createHandler: func(t *testing.T) *Mockhandler {
					return nil
				},
			},
			args: args{
				baseCtx: func() *mocks.Base {
					ctx := &mocks.Base{}
					ctx.On("GetOriginRequest").Return(nil, errors.Error("error"))
					return ctx
				}(),
				createContext: func(t *testing.T) *Mockcontext {
					ctx := NewMockcontext(gomock.NewController(t))
					ctx.EXPECT().GetLBSLocation().Return(&lbs.Location{
						Found:     true,
						Latitude:  1,
						Longitude: 2,
					}, nil)
					return ctx
				},
			},
			wantErr: assert.Error,
		},
		{
			name: "setup laas by gpauto failed failed",
			fields: fields{
				createHandler: func(t *testing.T) *Mockhandler {
					handler := NewMockhandler(gomock.NewController(t))
					handler.EXPECT().SetupLAASByGpAuto(gomock.Any(), gomock.Any(), gomock.Any(), gomock.Any(), gomock.Any()).
						Return(errors.Error("error"))
					return handler
				},
			},
			args: args{
				baseCtx: func() *mocks.Base {
					ctx := &mocks.Base{}
					ctx.On("GetOriginRequest").Return(&models.OriginRequest{}, nil)
					ctx.On("GetRequest").Return(models.Request{})
					ctx.On("GetAppInfo").Return(models.AppInfo{})
					return ctx
				}(),
				createContext: func(t *testing.T) *Mockcontext {
					ctx := NewMockcontext(gomock.NewController(t))
					ctx.EXPECT().GetLBSLocation().Return(&lbs.Location{
						Found:     true,
						Latitude:  1,
						Longitude: 2,
					}, nil)
					return ctx
				},
			},
			wantErr: assert.Error,
		},
		{
			name: "setup laas by gpauto failed sucess",
			fields: fields{
				createHandler: func(t *testing.T) *Mockhandler {
					handler := NewMockhandler(gomock.NewController(t))
					handler.EXPECT().SetupLAASByGpAuto(gomock.Any(), gomock.Any(), gomock.Any(), gomock.Any(), gomock.Any()).
						Return(nil)
					return handler
				},
			},
			args: args{
				baseCtx: func() *mocks.Base {
					ctx := &mocks.Base{}
					ctx.On("GetOriginRequest").Return(&models.OriginRequest{}, nil)
					ctx.On("GetRequest").Return(models.Request{})
					ctx.On("GetAppInfo").Return(models.AppInfo{})
					return ctx
				}(),
				createContext: func(t *testing.T) *Mockcontext {
					ctx := NewMockcontext(gomock.NewController(t))
					ctx.EXPECT().GetLBSLocation().Return(&lbs.Location{
						Found:     true,
						Latitude:  1,
						Longitude: 2,
					}, nil)
					return ctx
				},
			},
			wantErr: assert.NoError,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			s := &secondSrcSetupHandler{
				handler: tt.fields.createHandler(t),
			}

			ctx := tt.args.createContext(t)
			tt.wantErr(t, s.handle(ctx, tt.args.baseCtx))
		})
	}
}
