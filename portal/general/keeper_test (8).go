package devices

import (
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/library/go/yandex/uatraits"
	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/libs/utils/errors/v3"
	"a.yandex-team.ru/portal/avocado/libs/utils/log3"
)

func Test_keeper_GetDevice(t *testing.T) {
	type fields struct {
		createParser func(t *testing.T) *MockdeviceParser
		logger       log3.LoggerAlterable
		cached       *models.Device
		cacheUpdated bool
	}

	tests := []struct {
		name   string
		fields fields
		want   models.Device
	}{
		{
			name: "nil cache",
			fields: fields{
				createParser: func(t *testing.T) *MockdeviceParser {
					parser := NewMockdeviceParser(gomock.NewController(t))
					parser.EXPECT().Parse().Return(models.Device{
						BrowserDesc: &models.BrowserDesc{
							Traits: uatraits.Traits{
								"IsMobile": "true",
							},
							IsGramps:  true,
							UserAgent: "user-agent",
						},
					}, nil)
					return parser
				},
				logger:       log3.NewLoggerStub(),
				cached:       nil,
				cacheUpdated: false,
			},
			want: models.Device{
				BrowserDesc: &models.BrowserDesc{
					Traits: uatraits.Traits{
						"IsMobile": "true",
					},
					IsGramps:  true,
					UserAgent: "user-agent",
				},
			},
		},
		{
			name: "parse error",
			fields: fields{
				createParser: func(t *testing.T) *MockdeviceParser {
					parser := NewMockdeviceParser(gomock.NewController(t))
					parser.EXPECT().Parse().Return(models.Device{}, errors.Error("error"))
					return parser
				},
				logger:       log3.NewLoggerStub(),
				cached:       nil,
				cacheUpdated: false,
			},
			want: models.Device{},
		},
		{
			name: "not nil cache",
			fields: fields{
				createParser: func(t *testing.T) *MockdeviceParser {
					return nil
				},
				logger: log3.NewLoggerStub(),
				cached: &models.Device{
					BrowserDesc: &models.BrowserDesc{
						Traits: uatraits.Traits{
							"IsMobile": "true",
						},
						IsGramps:  true,
						UserAgent: "user-agent",
					},
				},
				cacheUpdated: false,
			},
			want: models.Device{
				BrowserDesc: &models.BrowserDesc{
					Traits: uatraits.Traits{
						"IsMobile": "true",
					},
					IsGramps:  true,
					UserAgent: "user-agent",
				},
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			k := &keeper{
				parser:       tt.fields.createParser(t),
				logger:       tt.fields.logger,
				cached:       tt.fields.cached,
				cacheUpdated: tt.fields.cacheUpdated,
			}

			got := k.GetDevice()
			assert.Equal(t, tt.want, got)
		})
	}
}

func Test_keeper_ForceDevice(t *testing.T) {
	type fields struct {
		cached       *models.Device
		cacheUpdated bool
	}
	type args struct {
		device models.Device
	}
	tests := []struct {
		name        string
		fields      fields
		args        args
		wantCache   *models.Device
		wantUpdated bool
	}{
		{
			name: "update cache",
			fields: fields{
				cached: &models.Device{
					BrowserDesc: &models.BrowserDesc{
						Traits: map[string]string{"os": "ios"},
					},
				},
				cacheUpdated: false,
			},
			args: args{
				device: models.Device{
					BrowserDesc: &models.BrowserDesc{
						Traits: map[string]string{"os": "android"},
					},
				},
			},
			wantCache: &models.Device{
				BrowserDesc: &models.BrowserDesc{
					Traits: map[string]string{"os": "android"},
				},
			},
			wantUpdated: true,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			k := &keeper{
				cached:       tt.fields.cached,
				cacheUpdated: tt.fields.cacheUpdated,
			}
			k.ForceDevice(tt.args.device)
			assert.Equal(t, tt.wantCache, k.cached)
			assert.Equal(t, tt.wantUpdated, k.cacheUpdated)
		})
	}
}

func Test_keeper_SetIsTouchGramps(t *testing.T) {
	tests := []struct {
		name             string
		cached           *models.Device
		cacheUpdated     bool
		parserAnswer     models.Device
		wantCached       *models.Device
		wantCacheUpdated bool
	}{
		{
			name: "set new IsTouchGramps",
			cached: &models.Device{
				BrowserDesc: &models.BrowserDesc{
					Traits: uatraits.Traits{
						"IsMobile": "true",
					},
					IsGramps:  true,
					UserAgent: "user-agent",
				},
			},
			cacheUpdated: false,
			parserAnswer: models.Device{
				BrowserDesc: &models.BrowserDesc{
					Traits: uatraits.Traits{
						"IsMobile": "true",
					},
					IsGramps:      true,
					IsTouchGramps: true,
					UserAgent:     "user-agent",
				},
			},
			wantCached: &models.Device{
				BrowserDesc: &models.BrowserDesc{
					Traits: uatraits.Traits{
						"IsMobile": "true",
					},
					IsGramps:      true,
					IsTouchGramps: true,
					UserAgent:     "user-agent",
				},
			},
			wantCacheUpdated: true,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			parserMock := NewMockdeviceParser(gomock.NewController(t))
			parserMock.EXPECT().SetIsTouchGramps(*tt.cached, "com").Return(tt.parserAnswer).Times(1)

			k := &keeper{
				parser:       parserMock,
				cached:       tt.cached,
				cacheUpdated: tt.cacheUpdated,
			}

			k.SetIsTouchGramps("com")

			assert.Equal(t, tt.wantCached, k.cached)
			assert.Equal(t, tt.wantCacheUpdated, k.cacheUpdated)
		})
	}
}
