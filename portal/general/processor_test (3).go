package plus

import (
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"

	protoanswers "a.yandex-team.ru/apphost/lib/proto_answers"
	"a.yandex-team.ru/library/go/test/assertpb"
	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/morda-go/pkg/exports"
	"a.yandex-team.ru/portal/avocado/morda-go/tests/mocks"
	plusproto "a.yandex-team.ru/portal/avocado/proto/plus"
)

func TestProcessor_getCurrentBalance(t *testing.T) {
	type args struct {
		balances []*plusproto.TPlusBlockBalance
		currency string
	}
	type testCase struct {
		name string
		args
		want *plusproto.TPlusBlockBalance
	}

	cases := []testCase{
		{
			name: "empty balances",
			args: args{
				balances: nil,
				currency: "RUB",
			},
			want: nil,
		},
		{
			name: "no balance with specified currency",
			args: args{
				balances: []*plusproto.TPlusBlockBalance{
					{
						Amount:   "15000",
						Currency: "USD",
						WalletId: "w/87ec365d-973f-4fb1-bf70-758f99c56168",
					},
					{
						Amount:   "4000",
						Currency: "EUR",
						WalletId: "w/8433eb5d-994d-434a-9518-64fe10bfb459",
					},
				},
				currency: "RUB",
			},
			want: nil,
		},
		{
			name: "several balance with specified currency",
			args: args{
				balances: []*plusproto.TPlusBlockBalance{
					{
						Amount:   "15000",
						Currency: "RUB",
						WalletId: "w/87ec365d-973f-4fb1-bf70-758f99c56168",
					},
					{
						Amount:   "4000",
						Currency: "EUR",
						WalletId: "w/8433eb5d-994d-434a-9518-64fe10bfb459",
					},
					{
						Amount:   "25000",
						Currency: "RUB",
						WalletId: "w/ff2a574c-fbe1-46d3-bb1d-348127ec5cef",
					},
				},
				currency: "RUB",
			},
			want: &plusproto.TPlusBlockBalance{
				Amount:   "15000",
				Currency: "RUB",
				WalletId: "w/87ec365d-973f-4fb1-bf70-758f99c56168",
			},
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			p := Processor{}
			actual := p.getCurrentBalance(tt.balances, tt.currency)
			assertpb.Equal(t, tt.want, actual)
		})
	}
}

func TestProcess_parseTrustAPIResponse(t *testing.T) {
	type testCase struct {
		name        string
		resp        *protoanswers.THttpResponse
		want        *trustAPIResponse
		wantErrFunc assert.ErrorAssertionFunc
	}

	cases := []testCase{
		{
			name:        "nil pointer",
			resp:        nil,
			want:        nil,
			wantErrFunc: assert.Error,
		},
		{
			name: "nil content",
			resp: &protoanswers.THttpResponse{
				Content: nil,
			},
			want:        nil,
			wantErrFunc: assert.Error,
		},
		{
			name: "success response",
			resp: &protoanswers.THttpResponse{
				Content: []byte(`{
					"balances": [
						{
							"amount": "15555.1234",
							"currency": "RUB",
							"wallet_id": "w/de24548f-0991-4c9c-b46b-6357d4012027"
						},
						{
							"amount": "888.234567",
							"currency": "BYN",
							"wallet_id": "w/d23dd000-3d15-4b18-be08-84f46bc31416"
						}
					]
				}`),
				StatusCode: 200,
			},
			want: &trustAPIResponse{
				Balances: []trustAPIBalance{
					{
						WalletID: "w/de24548f-0991-4c9c-b46b-6357d4012027",
						Amount:   "15555.1234",
						Currency: "RUB",
					},
					{
						WalletID: "w/d23dd000-3d15-4b18-be08-84f46bc31416",
						Amount:   "888.234567",
						Currency: "BYN",
					},
				},
			},
			wantErrFunc: assert.NoError,
		},
		{
			name: "trust reports error",
			resp: &protoanswers.THttpResponse{
				Content: []byte(`{
					"status": "error",
					"code": 504,
					"data": {
						"error": "invalid response from billing-wallet"
					}
				}`),
				StatusCode: 504,
			},
			want:        nil,
			wantErrFunc: assert.Error,
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			p := Processor{}
			actual, err := p.parseTrustAPIResponse(tt.resp)
			assert.Equal(t, tt.want, actual)
			tt.wantErrFunc(t, err)
		})
	}
}

func TestProcessor_roundBalance(t *testing.T) {
	type testCase struct {
		name      string
		value     string
		precision int
		want      string
	}

	cases := []testCase{
		{
			name:      "integer value",
			value:     "1511",
			precision: 0,
			want:      "1511",
		},
		{
			name:      "integer value with specified precision",
			value:     "1511",
			precision: 3,
			want:      "1511",
		},
		{
			name:      "trunked decimal value",
			value:     "1511.1992",
			precision: 0,
			want:      "1511",
		},
		{
			name:      "decimal value with one digit precision",
			value:     "1511.1992",
			precision: 1,
			want:      "1511.1",
		},
		{
			name:      "decimal value with two digit precision",
			value:     "1511.1992",
			precision: 2,
			want:      "1511.19",
		},
		{
			name:      "decimal value with high precision",
			value:     "1511.1992",
			precision: 99,
			want:      "1511.1992",
		},
		{
			name:      "decimal value with leading zeros",
			value:     "1511.0092",
			precision: 0,
			want:      "1511",
		},
		{
			name:      "decimal value with leading zeros and one digit precision",
			value:     "1511.0092",
			precision: 1,
			want:      "1511",
		},
		{
			name:      "decimal value with leading zeros and two digit precision",
			value:     "1511.0092",
			precision: 2,
			want:      "1511",
		},
		{
			name:      "decimal value with leading zeros and three digits precision",
			value:     "1511.0092",
			precision: 3,
			want:      "1511.009",
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			p := Processor{}
			actual := p.roundBalance(tt.value, tt.precision)
			assert.Equal(t, tt.want, actual)
		})
	}
}

func TestProcessor_getTrustBalances(t *testing.T) {
	type testCase struct {
		name      string
		arg       []trustAPIBalance
		precision int
		want      []*plusproto.TPlusBlockBalance
	}

	cases := []testCase{
		{
			name:      "empty slice",
			arg:       nil,
			precision: 0,
			want:      make([]*plusproto.TPlusBlockBalance, 0),
		},
		{
			name: "zero precision",
			arg: []trustAPIBalance{
				{
					WalletID: "w/17391523-8a16-4d6d-80a6-2b0029443474",
					Amount:   "1511.1992",
					Currency: "RUB",
				},
				{
					WalletID: "w/cf78808d-e802-416c-b071-d5d0143d6b52",
					Amount:   "21.28506",
					Currency: "BYN",
				},
				{
					WalletID: "w/5a6158f0-3637-417a-82d4-1de5855ff805",
					Amount:   "144778.34",
					Currency: "KZT",
				},
			},
			precision: 0,
			want: []*plusproto.TPlusBlockBalance{
				{
					WalletId: "w/17391523-8a16-4d6d-80a6-2b0029443474",
					Amount:   "1511",
					Currency: "RUB",
				},
				{
					WalletId: "w/cf78808d-e802-416c-b071-d5d0143d6b52",
					Amount:   "21",
					Currency: "BYN",
				},
				{
					WalletId: "w/5a6158f0-3637-417a-82d4-1de5855ff805",
					Amount:   "144778",
					Currency: "KZT",
				},
			},
		},
		{
			name: "nonzero precision",
			arg: []trustAPIBalance{
				{
					WalletID: "w/17391523-8a16-4d6d-80a6-2b0029443474",
					Amount:   "1511.1992",
					Currency: "RUB",
				},
				{
					WalletID: "w/cf78808d-e802-416c-b071-d5d0143d6b52",
					Amount:   "21.28506",
					Currency: "BYN",
				},
				{
					WalletID: "w/5a6158f0-3637-417a-82d4-1de5855ff805",
					Amount:   "144778.34",
					Currency: "KZT",
				},
			},
			precision: 1,
			want: []*plusproto.TPlusBlockBalance{
				{
					WalletId: "w/17391523-8a16-4d6d-80a6-2b0029443474",
					Amount:   "1511.1",
					Currency: "RUB",
				},
				{
					WalletId: "w/cf78808d-e802-416c-b071-d5d0143d6b52",
					Amount:   "21.2",
					Currency: "BYN",
				},
				{
					WalletId: "w/5a6158f0-3637-417a-82d4-1de5855ff805",
					Amount:   "144778.3",
					Currency: "KZT",
				},
			},
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			p := Processor{}
			actual := p.getTrustBalances(tt.arg, tt.precision)
			assert.Equal(t, tt.want, actual)
		})
	}
}

func TestProcessor_getBaseURLPlus(t *testing.T) {
	type testCase struct {
		name   string
		domain string
		want   string
	}

	cases := []testCase{
		{
			name:   "empty string",
			domain: "",
			want:   "https://plus.yandex.ru",
		},
		{
			name:   "not a domain",
			domain: "???",
			want:   "https://plus.yandex.ru",
		},
		{
			name:   "RU",
			domain: "ru",
			want:   "https://plus.yandex.ru",
		},
		{
			name:   "BY",
			domain: "by",
			want:   "https://plus.yandex.by",
		},
		{
			name:   "IT",
			domain: "it",
			want:   "https://plus.yandex.ru",
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			p := Processor{}
			actual := p.getBaseURLPlus(tt.domain)
			assert.Equal(t, tt.want, actual)
		})
	}
}

func TestProcessor_process(t *testing.T) {
	type args struct {
		resp                       *trustAPIResponse
		baseCtxMockFuncInit        func(mock *mocks.Base)
		geoSettingsGetterMockInit  func(mock *MockgeoSettingsGetter)
		localizationGetterMockinit func(mock *MocklocalizationGetter)
	}
	type testCase struct {
		name string
		args
		expected        *plusproto.TPlusBlock
		expectedErrFunc assert.ErrorAssertionFunc
	}

	cases := []testCase{
		{
			name: "disable plus data AB-flag",
			args: args{
				resp: nil,
				baseCtxMockFuncInit: func(mock *mocks.Base) {
					mock.On("GetFlags").Return(models.ABFlags{
						Flags: map[string]string{
							"disable_plus_data": "1",
						},
					})
				},
			},
			expected:        nil,
			expectedErrFunc: assert.NoError,
		},
		{
			name: "no subscription",
			args: args{
				resp: nil,
				baseCtxMockFuncInit: func(mock *mocks.Base) {
					mock.On("GetFlags").Return(models.ABFlags{
						Flags: map[string]string{
							"disable_plus_data": "0",
						},
					})
					mock.On("GetAuth").Return(models.Auth{
						PlusSubscription: models.PlusSubscription{
							Status:     false,
							StatusType: "",
						},
					})
					mock.On("GetMadmOptions").Return(exports.Options{
						Plus: exports.PlusOptions{
							NoPlusAll: false,
						},
					})
					mock.On("GetMordaZone").Return(models.MordaZone{
						Value: "ru",
					})
				},
				geoSettingsGetterMockInit: func(mock *MockgeoSettingsGetter) {
					mock.EXPECT().Get(gomock.Any()).Return(&geoSettings{
						ShowWallet: true,
						Currency:   "RUB",
						Precision:  0,
					}, nil)
				},
				localizationGetterMockinit: func(mock *MocklocalizationGetter) {
					mock.EXPECT().Get(gomock.Any(), gomock.Any()).Return("Оформите подписку")
				},
			},
			expected: &plusproto.TPlusBlock{
				Hint:          "Оформите подписку",
				IsActive:      false,
				LocalAmount:   "",
				LocalCurrency: "RUB",
				Processed:     true,
				Show:          true,
				Type:          "",
				Url:           "https://plus.yandex.ru",
				Balances:      nil,
			},
			expectedErrFunc: assert.NoError,
		},
		{
			name: "disable by option",
			args: args{
				resp: nil,
				baseCtxMockFuncInit: func(mock *mocks.Base) {
					mock.On("GetFlags").Return(models.ABFlags{
						Flags: map[string]string{
							"disable_plus_data": "0",
						},
					})
					mock.On("GetMadmOptions").Return(exports.Options{
						Plus: exports.PlusOptions{
							NoPlusAll: true,
						},
					})
				},
			},
			expected:        nil,
			expectedErrFunc: assert.NoError,
		},
		{
			name: "no geo settings",
			args: args{
				resp: &trustAPIResponse{
					Balances: []trustAPIBalance{
						{
							WalletID: "w/82846E17-CD7F-4CD2-B181-C9214E0ACA4A",
							Amount:   "1234.5678",
							Currency: "RUB",
						},
					},
				},
				baseCtxMockFuncInit: func(mock *mocks.Base) {
					mock.On("GetFlags").Return(models.ABFlags{
						Flags: map[string]string{
							"disable_plus_data": "0",
						},
					})
					mock.On("GetMadmOptions").Return(exports.Options{
						Plus: exports.PlusOptions{
							NoPlusAll: false,
						},
					})
				},
				geoSettingsGetterMockInit: func(mock *MockgeoSettingsGetter) {
					mock.EXPECT().Get(gomock.Any()).Return(nil, nil)
				},
			},
			expected:        nil,
			expectedErrFunc: assert.NoError,
		},
		{
			name: "auth user from Russia",
			args: args{
				resp: &trustAPIResponse{
					Balances: []trustAPIBalance{
						{
							WalletID: "w/82846E17-CD7F-4CD2-B181-C9214E0ACA4A",
							Amount:   "1234.5678",
							Currency: "RUB",
						},
					},
				},
				baseCtxMockFuncInit: func(mock *mocks.Base) {
					mock.On("GetFlags").Return(models.ABFlags{
						Flags: map[string]string{
							"disable_plus_data": "0",
						},
					})
					mock.On("GetAuth").Return(models.Auth{
						PlusSubscription: models.PlusSubscription{
							Status:     true,
							StatusType: "YA_PREMIUM",
						},
					})
					mock.On("GetMadmOptions").Return(exports.Options{
						Plus: exports.PlusOptions{
							NoPlusAll: false,
						},
					})
					mock.On("GetMordaZone").Return(models.MordaZone{
						Value: "ru",
					})
				},
				geoSettingsGetterMockInit: func(mock *MockgeoSettingsGetter) {
					mock.EXPECT().Get(gomock.Any()).Return(&geoSettings{
						ShowWallet: true,
						Currency:   "RUB",
						Precision:  0,
					}, nil)
				},
				localizationGetterMockinit: func(mock *MocklocalizationGetter) {
					mock.EXPECT().Get(gomock.Any(), gomock.Any()).Return("Подписка оформлена")
				},
			},
			expected: &plusproto.TPlusBlock{
				Hint:          "Подписка оформлена",
				IsActive:      true,
				LocalAmount:   "1234",
				LocalCurrency: "RUB",
				Processed:     true,
				Show:          true,
				Type:          "YA_PREMIUM",
				Url:           "https://plus.yandex.ru",
				Balances: []*plusproto.TPlusBlockBalance{
					{
						Amount:   "1234",
						Currency: "RUB",
						WalletId: "w/82846E17-CD7F-4CD2-B181-C9214E0ACA4A",
					},
				},
			},
			expectedErrFunc: assert.NoError,
		},
		{
			name: "auth user from Russia",
			args: args{
				resp: &trustAPIResponse{
					Balances: []trustAPIBalance{
						{
							WalletID: "w/82846E17-CD7F-4CD2-B181-C9214E0ACA4A",
							Amount:   "1234.5678",
							Currency: "RUB",
						},
					},
				},
				baseCtxMockFuncInit: func(mock *mocks.Base) {
					mock.On("GetFlags").Return(models.ABFlags{
						Flags: map[string]string{
							"disable_plus_data": "0",
						},
					})
					mock.On("GetAuth").Return(models.Auth{
						PlusSubscription: models.PlusSubscription{
							Status:     true,
							StatusType: "YA_PREMIUM",
						},
					})
					mock.On("GetMadmOptions").Return(exports.Options{
						Plus: exports.PlusOptions{
							NoPlusAll: false,
						},
					})
					mock.On("GetMordaZone").Return(models.MordaZone{
						Value: "ru",
					})
				},
				geoSettingsGetterMockInit: func(mock *MockgeoSettingsGetter) {
					mock.EXPECT().Get(gomock.Any()).Return(&geoSettings{
						ShowWallet: true,
						Currency:   "RUB",
						Precision:  0,
					}, nil)
				},
				localizationGetterMockinit: func(mock *MocklocalizationGetter) {
					mock.EXPECT().Get(gomock.Any(), gomock.Any()).Return("Подписка оформлена")
				},
			},
			expected: &plusproto.TPlusBlock{
				Hint:          "Подписка оформлена",
				IsActive:      true,
				LocalAmount:   "1234",
				LocalCurrency: "RUB",
				Processed:     true,
				Show:          true,
				Type:          "YA_PREMIUM",
				Url:           "https://plus.yandex.ru",
				Balances: []*plusproto.TPlusBlockBalance{
					{
						Amount:   "1234",
						Currency: "RUB",
						WalletId: "w/82846E17-CD7F-4CD2-B181-C9214E0ACA4A",
					},
				},
			},
			expectedErrFunc: assert.NoError,
		},
		{
			name: "auth but no response from trustAPI",
			args: args{
				resp: nil,
				baseCtxMockFuncInit: func(mock *mocks.Base) {
					mock.On("GetFlags").Return(models.ABFlags{
						Flags: map[string]string{
							"disable_plus_data": "0",
						},
					})
					mock.On("GetAuth").Return(models.Auth{
						PlusSubscription: models.PlusSubscription{
							Status:     true,
							StatusType: "YA_PREMIUM",
						},
					})
					mock.On("GetMadmOptions").Return(exports.Options{
						Plus: exports.PlusOptions{
							NoPlusAll: false,
						},
					})
					mock.On("GetMordaZone").Return(models.MordaZone{
						Value: "ru",
					})
				},
				geoSettingsGetterMockInit: func(mock *MockgeoSettingsGetter) {
					mock.EXPECT().Get(gomock.Any()).Return(&geoSettings{
						ShowWallet: true,
						Currency:   "RUB",
						Precision:  0,
					}, nil)
				},
				localizationGetterMockinit: func(mock *MocklocalizationGetter) {
					mock.EXPECT().Get(gomock.Any(), gomock.Any()).Return("Подписка оформлена")
				},
			},
			expected: &plusproto.TPlusBlock{
				Hint:          "Подписка оформлена",
				IsActive:      true,
				LocalAmount:   "",
				LocalCurrency: "RUB",
				Processed:     true,
				Show:          true,
				Type:          "YA_PREMIUM",
				Url:           "https://plus.yandex.ru",
				Balances:      nil,
			},
			expectedErrFunc: assert.NoError,
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)

			geoSettingsGetterMock := NewMockgeoSettingsGetter(ctrl)
			if tt.geoSettingsGetterMockInit != nil {
				tt.geoSettingsGetterMockInit(geoSettingsGetterMock)
			}

			localizationGetterMock := NewMocklocalizationGetter(ctrl)
			if tt.localizationGetterMockinit != nil {
				tt.localizationGetterMockinit(localizationGetterMock)
			}

			p := NewProcessor(geoSettingsGetterMock, localizationGetterMock)
			baseCtxMock := mocks.NewBase(t)

			if tt.baseCtxMockFuncInit != nil {
				tt.baseCtxMockFuncInit(baseCtxMock)
			}

			actual, err := p.process(baseCtxMock, tt.args.resp)
			assertpb.Equal(t, tt.expected, actual, "check TProtoPlus")
			tt.expectedErrFunc(t, err, "check error")
		})
	}
}
