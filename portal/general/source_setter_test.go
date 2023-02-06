package plus

import (
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/morda-go/pkg/exports"
	"a.yandex-team.ru/portal/avocado/morda-go/pkg/its"
	basemocks "a.yandex-team.ru/portal/avocado/morda-go/tests/mocks"
	"a.yandex-team.ru/portal/morda-go/tests/mocks"
)

func Test_SourceSetter_isTrustAPIEnabled(t *testing.T) {
	type testCase struct {
		name       string
		initMock   func(base *basemocks.Base)
		itsOptions its.Options
		wantFunc   assert.BoolAssertionFunc
	}

	cases := []testCase{
		{
			name: "disabled by ITS option",
			initMock: func(base *basemocks.Base) {
				base.On("GetMadmOptions").Return(exports.Options{
					Plus: exports.PlusOptions{
						DisableTrustAPI: true,
					},
				}).Maybe()
				base.On("GetAuth").Return(models.Auth{
					UID: "123",
				}).Maybe()
				base.On("GetFlags").Return(models.ABFlags{
					Flags: map[string]string{
						"plus_cashback": "1",
					},
				}).Maybe()
				base.On("GetMordaContent").Return(models.MordaContent{
					Value: "touch",
				}).Maybe()
				base.On("GetRequest").Return(models.Request{}).Maybe()
			},
			itsOptions: its.Options{
				MordaBackendOptions: its.MordaBackendOptions{
					TrustAPIRequestPercentage: 0,
				},
			},
			wantFunc: assert.False,
		},
		{
			name: "disabled by MADM option",
			initMock: func(base *basemocks.Base) {
				base.On("GetMadmOptions").Return(exports.Options{
					Plus: exports.PlusOptions{
						DisableTrustAPI: true,
					},
				}).Maybe()
				base.On("GetAuth").Return(models.Auth{
					UID: "123",
				}).Maybe()
				base.On("GetFlags").Return(models.ABFlags{
					Flags: map[string]string{
						"plus_cashback": "1",
					},
				}).Maybe()
				base.On("GetMordaContent").Return(models.MordaContent{
					Value: "touch",
				}).Maybe()
				base.On("GetRequest").Return(models.Request{}).Maybe()
			},
			itsOptions: its.Options{
				MordaBackendOptions: its.MordaBackendOptions{
					TrustAPIRequestPercentage: 100,
				},
			},
			wantFunc: assert.False,
		},
		{
			name: "no UID",
			initMock: func(base *basemocks.Base) {
				base.On("GetMadmOptions").Return(exports.Options{
					Plus: exports.PlusOptions{
						DisableTrustAPI: false,
					},
				}).Maybe()
				base.On("GetAuth").Return(models.Auth{
					UID: "",
				}).Maybe()
				base.On("GetFlags").Return(models.ABFlags{
					Flags: map[string]string{
						"plus_cashback": "1",
					},
				}).Maybe()
				base.On("GetMordaContent").Return(models.MordaContent{
					Value: "touch",
				}).Maybe()
				base.On("GetRequest").Return(models.Request{}).Maybe()
			},
			itsOptions: its.Options{
				MordaBackendOptions: its.MordaBackendOptions{
					TrustAPIRequestPercentage: 100,
				},
			},
			wantFunc: assert.False,
		},
		{
			name: "no plus_cashback AB-flag",
			initMock: func(base *basemocks.Base) {
				base.On("GetMadmOptions").Return(exports.Options{
					Plus: exports.PlusOptions{
						DisableTrustAPI: false,
					},
				}).Maybe()
				base.On("GetAuth").Return(models.Auth{
					UID: "123",
				}).Maybe()
				base.On("GetFlags").Return(models.ABFlags{
					Flags: map[string]string{
						"plus_cashback": "0",
					},
				}).Maybe()
				base.On("GetMordaContent").Return(models.MordaContent{
					Value: "touch",
				}).Maybe()
				base.On("GetRequest").Return(models.Request{}).Maybe()
			},
			itsOptions: its.Options{
				MordaBackendOptions: its.MordaBackendOptions{
					TrustAPIRequestPercentage: 100,
				},
			},
			wantFunc: assert.False,
		},
		{
			name: "unsupported content",
			initMock: func(base *basemocks.Base) {
				base.On("GetMadmOptions").Return(exports.Options{
					Plus: exports.PlusOptions{
						DisableTrustAPI: false,
					},
				}).Maybe()
				base.On("GetAuth").Return(models.Auth{
					UID: "123",
				}).Maybe()
				base.On("GetFlags").Return(models.ABFlags{
					Flags: map[string]string{
						"plus_cashback": "1",
					},
				}).Maybe()
				base.On("GetMordaContent").Return(models.MordaContent{
					Value: "com",
				}).Maybe()
				base.On("GetRequest").Return(models.Request{}).Maybe()
			},
			itsOptions: its.Options{
				MordaBackendOptions: its.MordaBackendOptions{
					TrustAPIRequestPercentage: 100,
				},
			},
			wantFunc: assert.False,
		},
		{
			name: "regular case from touch",
			initMock: func(base *basemocks.Base) {
				base.On("GetMadmOptions").Return(exports.Options{
					Plus: exports.PlusOptions{
						DisableTrustAPI: false,
					},
				}).Maybe()
				base.On("GetAuth").Return(models.Auth{
					UID: "123",
				}).Maybe()
				base.On("GetFlags").Return(models.ABFlags{
					Flags: map[string]string{
						"plus_cashback": "1",
					},
				}).Maybe()
				base.On("GetMordaContent").Return(models.MordaContent{
					Value: "touch",
				}).Maybe()
				base.On("GetRequest").Return(models.Request{}).Maybe()
			},
			itsOptions: its.Options{
				MordaBackendOptions: its.MordaBackendOptions{
					TrustAPIRequestPercentage: 100,
				},
			},
			wantFunc: assert.True,
		},
		{
			name: "regular case from SearchApp",
			initMock: func(base *basemocks.Base) {
				base.On("GetMadmOptions").Return(exports.Options{
					Plus: exports.PlusOptions{
						DisableTrustAPI: false,
					},
				}).Maybe()
				base.On("GetAuth").Return(models.Auth{
					UID: "123",
				}).Maybe()
				base.On("GetFlags").Return(models.ABFlags{
					Flags: map[string]string{
						"plus_cashback": "1",
					},
				}).Maybe()
				base.On("GetMordaContent").Return(models.MordaContent{
					Value: "api_search",
				}).Maybe()
				base.On("GetRequest").Return(models.Request{
					APIInfo: models.APIInfo{
						Name:    "search",
						Version: 2,
					},
				})
			},
			itsOptions: its.Options{
				MordaBackendOptions: its.MordaBackendOptions{
					TrustAPIRequestPercentage: 100,
				},
			},
			wantFunc: assert.True,
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			optionsGetterMock := &mocks.OptionsGetter{}
			optionsGetterMock.On("Get").Return(tt.itsOptions).Maybe()
			setter := NewSourceSetter(optionsGetterMock)
			baseMock := basemocks.NewBase(t)
			tt.initMock(baseMock)
			tt.wantFunc(t, setter.isTrustAPIEnabled(baseMock))
		})
	}
}
