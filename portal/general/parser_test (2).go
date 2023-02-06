package aadb

import (
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
)

func Test_parser_Parse(t *testing.T) {
	type fields struct {
		aadbMADMOptions MADMOptions
	}
	type cookieAnswer struct {
		cookie models.Cookie
	}
	type dailyAnswer struct {
		dailyCookie string
	}
	tests := []struct {
		name         string
		fields       fields
		cookieAnswer *cookieAnswer
		dailyAnswer  *dailyAnswer
		want         models.AADB
		wantErr      bool
	}{
		{
			name: "Got nil map answer from cookie getter",
			fields: fields{
				aadbMADMOptions: MADMOptions{
					DisableDayCookie: false,
				},
			},
			cookieAnswer: &cookieAnswer{
				cookie: models.Cookie{},
			},
			dailyAnswer: &dailyAnswer{
				dailyCookie: "test",
			},
			want: models.AADB{
				IsAddBlock: false,
			},
		},
		{
			name: "Got answer from cookie getter but answer is empty",
			fields: fields{
				aadbMADMOptions: MADMOptions{
					DisableDayCookie: false,
				},
			},
			cookieAnswer: &cookieAnswer{
				cookie: models.Cookie{
					Parsed: map[string][]string{},
				},
			},
			dailyAnswer: &dailyAnswer{
				dailyCookie: "test",
			},
			want: models.AADB{
				IsAddBlock: false,
			},
		},
		{
			name:   "Got answer from cookie getter; got cookie from daily",
			fields: fields{},
			cookieAnswer: &cookieAnswer{
				cookie: models.Cookie{
					Parsed: map[string][]string{
						"test": {"test"},
					},
				},
			},
			dailyAnswer: &dailyAnswer{
				dailyCookie: "test",
			},
			want: models.AADB{
				IsAddBlock: true,
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			cookieGetter := NewMockcookieGetter(ctrl)
			dailyGetter := NewMockdailyGetter(ctrl)
			if tt.cookieAnswer != nil {
				cookieGetter.EXPECT().GetCookie().Return(tt.cookieAnswer.cookie).Times(1)
			}
			if tt.dailyAnswer != nil {
				dailyGetter.EXPECT().Get().Return(tt.dailyAnswer.dailyCookie).Times(1)
			}
			p := &parser{
				cookieGetter:    cookieGetter,
				dailyGetter:     dailyGetter,
				aadbMADMOptions: tt.fields.aadbMADMOptions,
			}

			got, err := p.Parse()

			if tt.wantErr {
				require.Error(t, err)
			} else {
				assert.NoError(t, err)
				require.Equal(t, tt.want, got)
			}
		})
	}
}

func Test_parser_parseIsAdblock(t *testing.T) {
	type fields struct {
		aadbMADMOptions MADMOptions
	}
	type args struct {
		cookie      models.Cookie
		dailyCookie string
	}
	tests := []struct {
		name   string
		fields fields
		args   args
		want   bool
	}{
		{
			name: "Cookie is empty; daily cookie is empty",
			args: args{
				cookie:      models.Cookie{},
				dailyCookie: "",
			},
			want: false,
		},
		{
			name: "Got blstr in cookie",
			args: args{
				cookie: models.Cookie{
					Parsed: map[string][]string{
						"test":  {"test"},
						"blstr": {"1"},
					},
				},
				dailyCookie: "",
			},
			want: true,
		},
		{
			name: "Disabled day cookie in madm options is true",
			fields: fields{
				aadbMADMOptions: MADMOptions{
					DisableDayCookie: true,
				},
			},
			args: args{},
			want: false,
		},
		{
			name: "Disabled day cookie in madm options is true; daily cookie in cookie",
			fields: fields{
				aadbMADMOptions: MADMOptions{
					DisableDayCookie: true,
				},
			},
			args: args{
				cookie: models.Cookie{
					Parsed: map[string][]string{
						"test": {"1"},
					},
				},
				dailyCookie: "test",
			},
			want: false,
		},
		{
			name:   "Got daily cookie in cookie",
			fields: fields{},
			args: args{
				cookie: models.Cookie{
					Parsed: map[string][]string{
						"test":         {"1"},
						"daily_cookie": {"smth"},
						"test_2":       {"0"},
					},
				},
				dailyCookie: "daily_cookie",
			},
			want: true,
		},
		{
			name:   "Got 'Sulfur' (on of aadbCookieNames) in cookie",
			fields: fields{},
			args: args{
				cookie: models.Cookie{
					Parsed: map[string][]string{
						"Sulfur": {"q"},
						"test":   {"1"},
					},
				},
				dailyCookie: "daily_cookie",
			},
			want: true,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			p := &parser{
				aadbMADMOptions: tt.fields.aadbMADMOptions,
			}

			got := p.parseIsAdblock(tt.args.cookie, tt.args.dailyCookie)

			require.Equal(t, tt.want, got)
		})
	}
}
