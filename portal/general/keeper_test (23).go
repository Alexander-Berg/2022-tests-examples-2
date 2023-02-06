package yacookies

import (
	"errors"
	"net/http"
	"testing"
	"time"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/libs/utils/common"
	"a.yandex-team.ru/portal/avocado/proto/morda_data"
	"a.yandex-team.ru/portal/morda-go/tests/prepared"
)

func Test_keeper_GetYaCookies(t *testing.T) {
	type fields struct {
		cached       *models.YaCookies
		cacheUpdated bool
	}
	tests1 := []struct {
		name             string
		fields           fields
		initMocks        func(*MockoriginRequestKeeper)
		want             models.YaCookies
		wantCacheUpdated bool
		wantErr          error
	}{
		{
			name: "Warm cache",
			fields: fields{
				cached:       &prepared.TestModelYaCookiesVer1,
				cacheUpdated: true,
			},
			initMocks:        func(*MockoriginRequestKeeper) {},
			want:             prepared.TestModelYaCookiesVer1,
			wantCacheUpdated: true,
		},
		{
			name:   "Parse yaCookies and set to cache",
			fields: fields{},
			initMocks: func(originRequestKeeper *MockoriginRequestKeeper) {
				originRequestKeeper.EXPECT().GetOriginRequest().Return(
					&models.OriginRequest{
						Headers: http.Header{
							"Cookie": []string{"yandex_gid=123; yp=100.fruit.apple#300.city.moscow; ys=show_morda.yes#some_flag.1; yandexuid=1234567891234567890; Session_id=SomeRandomString1; sessionid2=SomeRandomString2"},
						},
					},
					nil,
				).MaxTimes(1)
			},
			want: models.YaCookies{
				YandexGID: 123,
				Yp: models.YCookie{
					RawString: "100.fruit.apple#300.city.moscow",
					Subcookies: map[string]models.YSubcookie{
						"fruit": {
							Name:   "fruit",
							Value:  "apple",
							Expire: 100,
						},
						"city": {
							Name:   "city",
							Value:  "moscow",
							Expire: 300,
						},
					},
				},
				Ys: models.YCookie{
					RawString: "show_morda.yes#some_flag.1",
					Subcookies: map[string]models.YSubcookie{
						"show_morda": {
							Name:  "show_morda",
							Value: "yes",
						},
						"some_flag": {
							Name:  "some_flag",
							Value: "1",
						},
					},
				},
				YandexUID:       "1234567891234567890",
				SessionID:       "SomeRandomString1",
				SessionID2:      "SomeRandomString2",
				YandexUIDSalted: 435442591,
			},
			wantCacheUpdated: true,
		},
		{
			name:   "Multiple Cookie headers in request",
			fields: fields{},
			initMocks: func(originRequestKeeper *MockoriginRequestKeeper) {
				originRequestKeeper.EXPECT().GetOriginRequest().Return(
					&models.OriginRequest{
						Headers: http.Header{
							"Cookie": []string{
								"yandex_gid=2; yp=100.fruit.banana#300.city.piter; ys=show_morda.no#some_flag.0; yandexuid=4444444444444444; Session_id=someOtherString",
								"yandex_gid=123; yp=100.fruit.apple#300.city.moscow; ys=show_morda.yes#some_flag.1; yandexuid=1234567891234567890; Session_id=SomeRandomString1; sessionid2=SomeRandomString2",
							},
						},
					},
					nil,
				).MaxTimes(1)
			},
			want: models.YaCookies{
				YandexGID: 123,
				Yp: models.YCookie{
					RawString: "100.fruit.apple#300.city.moscow",
					Subcookies: map[string]models.YSubcookie{
						"fruit": {
							Name:   "fruit",
							Value:  "apple",
							Expire: 100,
						},
						"city": {
							Name:   "city",
							Value:  "moscow",
							Expire: 300,
						},
					},
				},
				Ys: models.YCookie{
					RawString: "show_morda.yes#some_flag.1",
					Subcookies: map[string]models.YSubcookie{
						"show_morda": {
							Name:  "show_morda",
							Value: "yes",
						},
						"some_flag": {
							Name:  "some_flag",
							Value: "1",
						},
					},
				},
				YandexUID:       "1234567891234567890",
				SessionID:       "SomeRandomString1",
				SessionID2:      "SomeRandomString2",
				YandexUIDSalted: 435442591,
			},
			wantCacheUpdated: true,
		},
	}

	for _, tt := range tests1 {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)

			originRequestKeeperMock := NewMockoriginRequestKeeper(ctrl)
			tt.initMocks(originRequestKeeperMock)

			requestGetterMock := NewMockrequestGetter(ctrl)
			requestGetterMock.EXPECT().GetRequest().Return(models.Request{}).AnyTimes()

			timeProviderMock := NewMocktimeProvider(ctrl)
			timeProviderMock.EXPECT().GetCurrentTime().Return(time.Unix(0, 0)).AnyTimes()

			yaCookiesParser := NewParser(originRequestKeeperMock, requestGetterMock, timeProviderMock, common.Production)
			k := &keeper{
				yaCookiesParser: yaCookiesParser,
				cached:          tt.fields.cached,
				cacheUpdated:    tt.fields.cacheUpdated,
			}
			got, err := k.GetYaCookiesOrErr()

			require.Equal(t, tt.wantErr, err)
			require.Equal(t, tt.want, got)
			require.Equal(t, tt.wantCacheUpdated, k.cacheUpdated)
		})
	}

	tests2 := []struct {
		name             string
		fields           fields
		initMocks        func(*MockyaCookiesParser)
		want             models.YaCookies
		wantCacheUpdated bool
		wantErr          assert.ErrorAssertionFunc
	}{
		{
			name:   "Parse returning error",
			fields: fields{},
			initMocks: func(yaCookiesParser *MockyaCookiesParser) {
				yaCookiesParser.EXPECT().Parse().Return(prepared.TestModelYaCookiesVer1, errors.New("error")).Times(1)
			},
			want:             prepared.TestModelYaCookiesVer1,
			wantErr:          assert.Error,
			wantCacheUpdated: true,
		},
	}

	for _, tt := range tests2 {
		t.Run(tt.name, func(t *testing.T) {
			yaCookiesParser := NewMockyaCookiesParser(gomock.NewController(t))
			tt.initMocks(yaCookiesParser)
			k := &keeper{
				yaCookiesParser: yaCookiesParser,
				cached:          tt.fields.cached,
				cacheUpdated:    tt.fields.cacheUpdated,
			}

			got, err := k.GetYaCookiesOrErr()

			tt.wantErr(t, err)
			assert.Equal(t, tt.want, got)
			assert.Equal(t, tt.wantCacheUpdated, k.cacheUpdated)
		})
	}
}

func Test_keeper_GetYaCookiesIfUpdated(t *testing.T) {
	type fields struct {
		cached       *models.YaCookies
		cacheUpdated bool
	}
	tests := []struct {
		name   string
		fields fields
		want   *morda_data.YaCookies
	}{
		{
			name: "Empty cache",
			want: nil,
		},
		{
			name: "Warm cache",
			fields: fields{
				cached:       &prepared.TestModelYaCookiesVer1,
				cacheUpdated: true,
			},
			want: prepared.TestDTOYaCookiesVer1,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			k := &keeper{
				cached:       tt.fields.cached,
				cacheUpdated: tt.fields.cacheUpdated,
			}

			got := k.GetYaCookiesIfUpdated()
			require.Equal(t, tt.want, got)
		})
	}
}

func Test_keeper_ForceYandexUID(t *testing.T) {
	type fields struct {
		cached       *models.YaCookies
		cacheUpdated bool
	}
	type args struct {
		yandexUID string
	}
	tests := []struct {
		name        string
		fields      fields
		args        args
		wantCache   *models.YaCookies
		wantUpdated bool
	}{
		{
			name: "update cache",
			fields: fields{
				cached: &models.YaCookies{
					Yp: models.YCookie{
						Subcookies: map[string]models.YSubcookie{
							"qwe": {
								Name:  "qwe",
								Value: "qwe",
							},
						},
					},
					YandexUID:       "1234567891234567890",
					YandexUIDSalted: 435442591,
				},
				cacheUpdated: false,
			},
			args: args{
				yandexUID: "11111111111111",
			},
			wantCache: &models.YaCookies{
				Yp: models.YCookie{
					Subcookies: map[string]models.YSubcookie{
						"qwe": {
							Name:  "qwe",
							Value: "qwe",
						},
					},
				},
				YandexUID:       "11111111111111",
				YandexUIDSalted: 42,
			},
			wantUpdated: true,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			parserMock := NewMockyaCookiesParser(gomock.NewController(t))
			parserMock.EXPECT().GetYandexUIDSalted(tt.args.yandexUID).Return(uint32(42)).Times(1)
			k := &keeper{
				yaCookiesParser: parserMock,
				cached:          tt.fields.cached,
				cacheUpdated:    tt.fields.cacheUpdated,
			}
			k.ForceYandexUID(tt.args.yandexUID)
			assert.Equal(t, tt.wantCache, k.cached)
			assert.Equal(t, tt.wantUpdated, k.cacheUpdated)
		})
	}
}
