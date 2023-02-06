package madmprocessor

import (
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
)

func Test_madmProcessor_checkYandexOnly(t *testing.T) {
	type fields struct {
		request models.Request
	}
	type args struct {
		params ABFlagsParameters
	}
	tests := []struct {
		name   string
		fields fields
		args   args
		want   bool
	}{
		{
			name: "yandexonly is zero",
			fields: fields{
				request: models.Request{
					IsInternal:   false,
					IsStaffLogin: false,
				},
			},
			args: args{
				params: ABFlagsParameters{
					YandexOnly: false,
				},
			},
			want: true,
		},
		{
			name: "yandexonly is 1, but got external request",
			fields: fields{
				request: models.Request{
					IsInternal:   false,
					IsStaffLogin: false,
				},
			},
			args: args{
				params: ABFlagsParameters{
					YandexOnly: true,
				},
			},
			want: false,
		},
		{
			name: "yandexonly is 1, got stafflogin",
			fields: fields{
				request: models.Request{
					IsInternal:   false,
					IsStaffLogin: true,
				},
			},
			args: args{
				params: ABFlagsParameters{
					YandexOnly: true,
				},
			},
			want: true,
		},
		{
			name: "yandexonly is 1, got internal request",
			fields: fields{
				request: models.Request{
					IsInternal:   true,
					IsStaffLogin: false,
				},
			},
			args: args{
				params: ABFlagsParameters{
					YandexOnly: true,
				},
			},
			want: true,
		},
		{
			name: "yandexonly is 1, got stafflogin and it's internal request",
			fields: fields{
				request: models.Request{
					IsInternal:   true,
					IsStaffLogin: true,
				},
			},
			args: args{
				params: ABFlagsParameters{
					YandexOnly: true,
				},
			},
			want: true,
		},
		{
			name: "yandexonly is 0, got stafflogin and it's internal request",
			fields: fields{
				request: models.Request{
					IsInternal:   true,
					IsStaffLogin: true,
				},
			},
			args: args{
				params: ABFlagsParameters{
					YandexOnly: false,
				},
			},
			want: true,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			requestGetter := NewMockrequestGetter(ctrl)
			requestGetter.EXPECT().GetRequest().Return(tt.fields.request).MaxTimes(1)
			p := &processor{
				requestGetter: requestGetter,
			}

			got := p.checkYandexOnly(tt.args.params)

			assert.Equal(t, tt.want, got)
		})
	}
}

func Test_madmProcessor_checkExpSlotAndPercentage(t *testing.T) {
	type fields struct {
		request   models.Request
		yaCookies models.YaCookies
	}
	type args struct {
		params  ABFlagsParameters
		appInfo models.AppInfo
	}
	tests := []struct {
		name   string
		fields fields
		args   args
		want   bool
	}{
		{
			name: "yandex100 is true, and it is internal request",
			fields: fields{
				request: models.Request{
					IsInternal: true,
				},
			},
			args: args{
				params: ABFlagsParameters{
					Yandex100: true,
				},
			},
			want: true,
		},
		{
			name: "percent is 100",
			fields: fields{
				request: models.Request{},
			},
			args: args{
				params: ABFlagsParameters{
					Yandex100: false,
					Percent:   100,
				},
			},
			want: true,
		},
		{
			name: "expSlot in range yandexuid_salted",
			fields: fields{
				request: models.Request{},
				yaCookies: models.YaCookies{
					YandexUIDSalted: 9112,
				},
			},
			args: args{
				params: ABFlagsParameters{
					Yandex100: false,
					Percent:   10,
					Selector:  "yandexuid_salted",
					ExpSlot:   100,
				},
			},
			want: true,
		},
		{
			name: "expSlot not in range yandexuid_salted",
			fields: fields{
				request: models.Request{},
				yaCookies: models.YaCookies{
					YandexUIDSalted: 9200,
				},
			},
			args: args{
				params: ABFlagsParameters{
					Yandex100: false,
					Percent:   10,
					Selector:  "yandexuid_salted",
					ExpSlot:   100,
				},
			},
			want: false,
		},
		{
			name: "yandexuid==0 and ExpSlot==0",
			fields: fields{
				request: models.Request{},
				yaCookies: models.YaCookies{
					YandexUIDSalted: 0,
				},
			},
			args: args{
				params: ABFlagsParameters{
					Yandex100: false,
					Percent:   10,
					Selector:  "yandexuid_salted",
					ExpSlot:   0,
				},
			},
			want: false,
		},
		{
			name: "expSlot in range uuid",
			fields: fields{
				request: models.Request{},
			},
			args: args{
				params: ABFlagsParameters{
					Yandex100: false,
					Percent:   10,
					Selector:  "uuid",
					ExpSlot:   100,
				},
				appInfo: models.AppInfo{
					UUIDHashed: 9112,
				},
			},
			want: true,
		},
		{
			name: "expSlot not in range uuid",
			fields: fields{
				request: models.Request{},
			},
			args: args{
				params: ABFlagsParameters{
					Yandex100: false,
					Percent:   10,
					Selector:  "uuid",
					ExpSlot:   100,
				},
				appInfo: models.AppInfo{
					UUIDHashed: 9200,
				},
			},
			want: false,
		},
		{
			name: "uuid==0 and ExpSlot==0",
			fields: fields{
				request: models.Request{},
			},
			args: args{
				params: ABFlagsParameters{
					Yandex100: false,
					Percent:   10,
					Selector:  "uuid",
					ExpSlot:   0,
				},
				appInfo: models.AppInfo{
					UUIDHashed: 0,
				},
			},
			want: false,
		},
		{
			name: "expSlot in range did",
			fields: fields{
				request: models.Request{},
			},
			args: args{
				params: ABFlagsParameters{
					Yandex100: false,
					Percent:   10,
					Selector:  "did",
					ExpSlot:   100,
				},
				appInfo: models.AppInfo{
					DIDHashed: 9112,
				},
			},
			want: true,
		},
		{
			name: "expSlot not in range did",
			fields: fields{
				request: models.Request{},
			},
			args: args{
				params: ABFlagsParameters{
					Yandex100: false,
					Percent:   10,
					Selector:  "did",
					ExpSlot:   100,
				},
				appInfo: models.AppInfo{
					DIDHashed: 9200,
				},
			},
			want: false,
		},
		{
			name: "did==0 and ExpSlot==0",
			fields: fields{
				request: models.Request{},
			},
			args: args{
				params: ABFlagsParameters{
					Yandex100: false,
					Percent:   10,
					Selector:  "did",
					ExpSlot:   0,
				},
				appInfo: models.AppInfo{
					DIDHashed: 0,
				},
			},
			want: false,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			requestGetter := NewMockrequestGetter(ctrl)
			requestGetter.EXPECT().GetRequest().Return(tt.fields.request).MaxTimes(1)
			yaCookiesGetter := NewMockyaCookieGetter(ctrl)
			yaCookiesGetter.EXPECT().GetYaCookies().Return(tt.fields.yaCookies).MaxTimes(1)
			p := &processor{
				requestGetter:  requestGetter,
				yaCookieGetter: yaCookiesGetter,
			}

			got := p.checkExpSlotAndPercentage(tt.args.params, tt.args.appInfo)

			require.Equal(t, tt.want, got)
		})
	}
}
