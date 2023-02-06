package cookies

import (
	"errors"
	"net/http"
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/proto/morda_data"
	"a.yandex-team.ru/portal/morda-go/tests/prepared"
)

func Test_keeper_GetCookie(t *testing.T) {
	type fields struct {
		cached *models.Cookie
	}
	tests := []struct {
		name             string
		fields           fields
		initMocks        func(*MockcookieParser, *MockoriginRequestKeeper)
		want             models.Cookie
		wantCacheUpdated bool
	}{
		{
			name: "Warm cache",
			fields: fields{
				cached: models.NewCookie(prepared.TestCookieVer1),
			},

			initMocks: func(*MockcookieParser, *MockoriginRequestKeeper) {
			},
			want: *models.NewCookie(prepared.TestCookieVer1),
		},
		{
			name:   "Parsing cookie and save to cache",
			fields: fields{},
			initMocks: func(parser *MockcookieParser, originRequestKeeper *MockoriginRequestKeeper) {
				headers := http.Header{}
				headers.Add(HeaderName, "test=oo;")
				originRequestKeeper.EXPECT().GetOriginRequest().Return(
					&models.OriginRequest{Headers: headers}, nil,
				).Times(1)
				parser.EXPECT().Parse("test=oo;").Return(models.Cookie{
					Parsed: map[string][]string{
						"test": {"oo"},
					},
				}, nil).Times(1)
			},
			want: models.Cookie{
				Parsed: map[string][]string{
					"test": {"oo"},
				},
			},
			wantCacheUpdated: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			originRequestKeeper := NewMockoriginRequestKeeper(ctrl)
			parser := NewMockcookieParser(ctrl)

			tt.initMocks(parser, originRequestKeeper)

			k := &keeper{
				parser:              parser,
				originRequestKeeper: originRequestKeeper,
				cached:              tt.fields.cached,
			}

			got := k.GetCookie()

			assert.Equal(t, tt.want, got)
			assert.Equal(t, &tt.want, k.cached)
			assert.Equal(t, tt.wantCacheUpdated, k.cacheUpdated)
		})
	}
}

func Test_keeper_GetCookieIfUpdated(t *testing.T) {
	type fields struct {
		cached       *models.Cookie
		cacheUpdated bool
	}
	tests := []struct {
		name   string
		fields fields
		want   *morda_data.Cookie
	}{
		{
			name: "not updated",
			fields: fields{
				cacheUpdated: false,
			},
			want: nil,
		},
		{
			name: "updated",
			fields: fields{
				cacheUpdated: true,
				cached:       &models.Cookie{},
			},
			want: &morda_data.Cookie{
				Parsed: map[string]*morda_data.Cookie_Value{},
				My: &morda_data.Cookie_My{
					Parsed: map[uint32]*morda_data.Cookie_My_MyValue{},
				},
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			k := &keeper{
				cached:       tt.fields.cached,
				cacheUpdated: tt.fields.cacheUpdated,
			}
			got := k.GetCookieIfUpdated()
			assert.Equal(t, tt.want, got)
		})
	}
}

func Test_keeper_parse(t *testing.T) {
	type fields struct {
		cookie           string
		originRequestErr error
		parserAnswer     models.Cookie
		parserErr        error
	}
	tests := []struct {
		name    string
		fields  fields
		want    models.Cookie
		wantErr bool
	}{
		{
			name: "get request error",
			fields: fields{
				originRequestErr: errors.New("error"),
			},
			want:    models.Cookie{},
			wantErr: true,
		},
		{
			name: "parser error",
			fields: fields{
				cookie:       "a=test",
				parserAnswer: models.Cookie{},
				parserErr:    errors.New("error"),
			},
			want:    models.Cookie{},
			wantErr: true,
		},
		{
			name: "valid cookie",
			fields: fields{
				cookie: "a=test",
				parserAnswer: models.Cookie{
					Parsed: map[string][]string{"a": {"test"}},
				},
			},
			want: models.Cookie{
				Parsed: map[string][]string{"a": {"test"}},
			},
			wantErr: false,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			headers := http.Header{}
			headers.Add(HeaderName, tt.fields.cookie)

			ctrl := gomock.NewController(t)
			originRequestKeeper := NewMockoriginRequestKeeper(ctrl)
			originRequestKeeper.EXPECT().GetOriginRequest().Return(
				&models.OriginRequest{Headers: headers},
				tt.fields.originRequestErr,
			).Times(1)

			parser := NewMockcookieParser(ctrl)
			parser.EXPECT().Parse(tt.fields.cookie).Return(tt.fields.parserAnswer, tt.fields.parserErr).MaxTimes(1)

			k := &keeper{
				originRequestKeeper: originRequestKeeper,
				parser:              parser,
			}

			got, err := k.parse()
			assert.Equal(t, tt.wantErr, err != nil)
			assert.Equal(t, tt.want, got)
		})
	}
}
