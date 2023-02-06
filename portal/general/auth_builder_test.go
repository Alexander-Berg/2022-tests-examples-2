package blackbox

import (
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
)

func stringPtr(s string) *string {
	return &s
}

func TestAuthContextBuilder_Build(t *testing.T) {
	type fields struct {
		authInfo AuthInfo
	}
	tests := []struct {
		name   string
		fields fields
		want   models.Auth
	}{
		{
			name: "empty auth info",
			fields: fields{
				authInfo: AuthInfo{},
			},
			want: models.Auth{
				UID:              "",
				Sids:             map[string]string{},
				PlusSubscription: models.PlusSubscription{},
				Logged:           false,
				SocialUser:       "",
			},
		},
		{
			name: "auth info with UID",
			fields: fields{
				authInfo: AuthInfo{
					AuthUser: AuthUser{
						UID: "test",
					},
					Logged: 1,
				},
			},
			want: models.Auth{
				UID:              "test",
				Sids:             map[string]string{},
				PlusSubscription: models.PlusSubscription{},
				Logged:           true,
			},
		},
		{
			name: "simple auth info",
			fields: fields{
				authInfo: AuthInfo{
					AuthUser: AuthUser{
						UID: "test",
						Sids: map[string]Suid{
							"sid1": {"1"},
							"sid2": {"2"},
						},
					},
					Logged: 1,
				},
			},
			want: models.Auth{
				UID: "test",
				Sids: map[string]string{
					"sid1": "1",
					"sid2": "2",
				},
				PlusSubscription: models.PlusSubscription{},
				Logged:           true,
			},
		},
		{
			name: "auth info without UID",
			fields: fields{
				authInfo: AuthInfo{
					AuthUser: AuthUser{
						Sids: map[string]Suid{
							"sid1": {"1"},
							"sid2": {"2"},
						},
					},
					Logged: 0,
				},
			},
			want: models.Auth{
				UID: "",
				Sids: map[string]string{
					"sid1": "1",
					"sid2": "2",
				},
				PlusSubscription: models.PlusSubscription{},
				Logged:           false,
			},
		},
		{
			name: "auth with Plus subscription",
			fields: fields{
				authInfo: AuthInfo{
					AuthUser: AuthUser{
						Sids: map[string]Suid{
							"sid1": {"1"},
							"sid2": {"2"},
						},
						PlusStatus:               stringPtr("1"),
						PlusStatusType:           stringPtr("KINOPOISK"),
						PlusSubscriptionExpireTS: stringPtr("1999888777"),
						PlusNextChargeTS:         stringPtr("1777888999"),
					},
					Logged: 1,
				},
			},
			want: models.Auth{
				UID: "",
				Sids: map[string]string{
					"sid1": "1",
					"sid2": "2",
				},
				PlusSubscription: models.PlusSubscription{
					Status:              true,
					NextChargeTimestamp: 1777888999,
					StatusType:          "KINOPOISK",
					ExpireTimestamp:     1999888777,
				},
				Logged: true,
			},
		},
		{
			name: "auth info with social",
			fields: fields{
				authInfo: AuthInfo{
					AuthUser: AuthUser{
						UID:    "test",
						Social: "some_social_account",
					},
					Logged: 1,
				},
			},
			want: models.Auth{
				UID:              "test",
				Sids:             map[string]string{},
				PlusSubscription: models.PlusSubscription{},
				Logged:           true,
				SocialUser:       "some_social_account",
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			b := &authBuilder{
				authInfo: tt.fields.authInfo,
			}

			assert.Equal(t, tt.want, b.Build())
		})
	}
}

func TestAuthContextBuilder_buildPlusSubscription(t *testing.T) {
	type testCase struct {
		name     string
		authInfo AuthInfo
		want     models.PlusSubscription
	}

	cases := []testCase{
		{
			name: "nil",
			authInfo: AuthInfo{
				AuthUser: AuthUser{
					PlusNextChargeTS:         nil,
					PlusStatus:               nil,
					PlusStatusType:           nil,
					PlusSubscriptionExpireTS: nil,
				},
			},
			want: models.PlusSubscription{
				Status:              false,
				NextChargeTimestamp: 0,
				StatusType:          "",
				ExpireTimestamp:     0,
			},
		},
		{
			name: "not activated with not nil value",
			authInfo: AuthInfo{
				AuthUser: AuthUser{
					PlusNextChargeTS:         nil,
					PlusStatus:               nil,
					PlusStatusType:           nil,
					PlusSubscriptionExpireTS: nil,
				},
			},
			want: models.PlusSubscription{
				Status:              false,
				NextChargeTimestamp: 0,
				StatusType:          "",
				ExpireTimestamp:     0,
			},
		},
		{
			name: "not activated with not nil value",
			authInfo: AuthInfo{
				AuthUser: AuthUser{
					PlusNextChargeTS:         nil,
					PlusStatus:               stringPtr("0"),
					PlusStatusType:           nil,
					PlusSubscriptionExpireTS: nil,
				},
			},
			want: models.PlusSubscription{
				Status:              false,
				NextChargeTimestamp: 0,
				StatusType:          "",
				ExpireTimestamp:     0,
			},
		},
		{
			name: "activated",
			authInfo: AuthInfo{
				AuthUser: AuthUser{
					PlusNextChargeTS:         stringPtr("1888888888"),
					PlusStatus:               stringPtr("1"),
					PlusStatusType:           stringPtr("YA_PREMIUM"),
					PlusSubscriptionExpireTS: stringPtr("1999999999"),
				},
			},
			want: models.PlusSubscription{
				Status:              true,
				NextChargeTimestamp: 1888888888,
				StatusType:          "YA_PREMIUM",
				ExpireTimestamp:     1999999999,
			},
		},
		{
			name: "activated without timestamps",
			authInfo: AuthInfo{
				AuthUser: AuthUser{
					PlusNextChargeTS:         stringPtr(""),
					PlusStatus:               stringPtr("1"),
					PlusStatusType:           stringPtr("YA_PREMIUM"),
					PlusSubscriptionExpireTS: stringPtr(""),
				},
			},
			want: models.PlusSubscription{
				Status:              true,
				NextChargeTimestamp: 0,
				StatusType:          "YA_PREMIUM",
				ExpireTimestamp:     0,
			},
		},
		{
			name: "activated without status type",
			authInfo: AuthInfo{
				AuthUser: AuthUser{
					PlusNextChargeTS:         stringPtr("123"),
					PlusStatus:               stringPtr("1"),
					PlusStatusType:           nil,
					PlusSubscriptionExpireTS: stringPtr("456"),
				},
			},
			want: models.PlusSubscription{
				Status:              true,
				NextChargeTimestamp: 123,
				StatusType:          "",
				ExpireTimestamp:     456,
			},
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			b := &authBuilder{
				authInfo: tt.authInfo,
			}
			actual := b.buildPlusSubscription()
			assert.Equal(t, tt.want, actual, "compare plus subscription")
		})
	}
}

func Test_authBuilde_parseStringPtrAsTimestamp(t *testing.T) {
	type testCase struct {
		name string
		arg  *string
		want int32
	}

	cases := []testCase{
		{
			name: "nil",
			arg:  nil,
			want: 0,
		},
		{
			name: "empty string",
			arg:  stringPtr(""),
			want: 0,
		},
		{
			name: "non-integer value",
			arg:  stringPtr("test"),
			want: 0,
		},
		{
			name: "integer value",
			arg:  stringPtr("123"),
			want: 123,
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			var b authBuilder
			actual := b.parseStringPtrAsTimestamp(tt.arg)
			assert.Equal(t, tt.want, actual)
		})
	}
}
