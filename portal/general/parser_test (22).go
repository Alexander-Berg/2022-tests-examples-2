package yacookies

import (
	"fmt"
	"net/http"
	"net/url"
	"strings"
	"testing"
	"time"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/libs/utils/common"
)

func Test_parser_ParseYSubcookie(t *testing.T) {
	validTestCases := []struct {
		TestName       string
		Item           string
		HasExpireField bool
		Expected       models.YSubcookie
	}{
		{
			TestName:       "String value",
			Item:           "key.value",
			HasExpireField: false,
			Expected: models.YSubcookie{
				Name:   "key",
				Value:  "value",
				Expire: 0,
			},
		},
		{
			TestName:       "Integer value",
			Item:           "key.0",
			HasExpireField: false,
			Expected: models.YSubcookie{
				Name:   "key",
				Value:  "0",
				Expire: 0,
			},
		},
		{
			TestName:       "Key starts with digit",
			Item:           "1key.value",
			HasExpireField: false,
			Expected: models.YSubcookie{
				Name:   "1key",
				Value:  "value",
				Expire: 0,
			},
		},
		{
			TestName:       "Key ends with digit",
			Item:           "key1.value",
			HasExpireField: false,
			Expected: models.YSubcookie{
				Name:   "key1",
				Value:  "value",
				Expire: 0,
			},
		},
		{
			TestName:       "Numeric key",
			Item:           "123.value",
			HasExpireField: false,
			Expected: models.YSubcookie{
				Name:   "123",
				Value:  "value",
				Expire: 0,
			},
		},
		{
			TestName:       "Numeric key and value",
			Item:           "123.456",
			HasExpireField: false,
			Expected: models.YSubcookie{
				Name:   "123",
				Value:  "456",
				Expire: 0,
			},
		},
		{
			TestName:       "URL encoded hash in value",
			Item:           "key.val%23e",
			HasExpireField: false,
			Expected: models.YSubcookie{
				Name:   "key",
				Value:  "val#e",
				Expire: 0,
			},
		},
		{
			TestName:       "URL encoded dot in value",
			Item:           "key.val%2ee",
			HasExpireField: false,
			Expected: models.YSubcookie{
				Name:   "key",
				Value:  "val.e",
				Expire: 0,
			},
		},
		{
			TestName:       "URL encoded space in value",
			Item:           "key.spaced%20value",
			HasExpireField: false,
			Expected: models.YSubcookie{
				Name:   "key",
				Value:  "spaced value",
				Expire: 0,
			},
		},
		{
			TestName:       "More than two parts",
			Item:           "key.dotted.value",
			HasExpireField: false,
			Expected: models.YSubcookie{
				Name:   "key",
				Value:  "dotted.value",
				Expire: 0,
			},
		},

		{
			TestName:       "Timestamp",
			Item:           "721828800.key.value",
			HasExpireField: true,
			Expected: models.YSubcookie{
				Name:   "key",
				Value:  "value",
				Expire: 721828800,
			},
		},
		{
			TestName:       "Zero timestamp",
			Item:           "0.key.value",
			HasExpireField: true,
			Expected: models.YSubcookie{
				Name:   "key",
				Value:  "value",
				Expire: 0,
			},
		},
		{
			TestName:       "More than two parts",
			Item:           "123.key.dotted.value",
			HasExpireField: true,
			Expected: models.YSubcookie{
				Name:   "key",
				Value:  "dotted.value",
				Expire: 123,
			},
		},
		{
			TestName:       "Empty value without timestamp",
			Item:           "key.",
			HasExpireField: false,
			Expected: models.YSubcookie{
				Name:   "key",
				Value:  "",
				Expire: 0,
			},
		},
		{
			TestName:       "Empty value with timestamp",
			Item:           "123.key.",
			HasExpireField: true,
			Expected: models.YSubcookie{
				Name:   "key",
				Value:  "",
				Expire: 123,
			},
		},
	}

	for _, item := range validTestCases {
		t.Run("Valid_"+item.TestName, func(t *testing.T) {
			ctrl := gomock.NewController(t)

			originRequestKeeperMock := NewMockoriginRequestKeeper(ctrl)
			requestKeeperMock := NewMockrequestGetter(ctrl)
			timeProviderMock := NewMocktimeProvider(ctrl)

			actual, err := NewParser(originRequestKeeperMock, requestKeeperMock, timeProviderMock, common.Production).parseYSubcookie(item.Item, item.HasExpireField)
			if assert.NoError(t, err) {
				assert.Equal(t, item.Expected, actual)
			}
		})
	}
	// they must return error
	invalidTestCases := []struct {
		TestName       string
		Item           string
		HasExpireField bool
	}{
		{
			TestName:       "No key",
			Item:           ".value",
			HasExpireField: false,
		},
		{
			TestName:       "No key and value",
			Item:           ".",
			HasExpireField: false,
		},
		{
			TestName:       "Spaces only",
			Item:           " . ",
			HasExpireField: false,
		},
		{
			TestName:       "Space key",
			Item:           " .value",
			HasExpireField: false,
		},
		{
			TestName:       "Nonalphanumeric key",
			Item:           "k?ey.value",
			HasExpireField: false,
		},
		{
			TestName:       "URL encoded key",
			Item:           "k%23y.value",
			HasExpireField: false,
		},
		{
			TestName:       "Negative timestamp",
			Item:           "-1.key.value",
			HasExpireField: true,
		},
	}

	for _, item := range invalidTestCases {
		t.Run("Invalid_"+item.TestName, func(t *testing.T) {
			ctrl := gomock.NewController(t)

			originRequestKeeperMock := NewMockoriginRequestKeeper(ctrl)
			requestKeeperMock := NewMockrequestGetter(ctrl)
			timeProviderMock := NewMocktimeProvider(ctrl)

			_, err := NewParser(originRequestKeeperMock, requestKeeperMock, timeProviderMock, common.Production).parseYSubcookie(item.Item, item.HasExpireField)
			assert.Error(t, err)
		})
	}
}

func Test_parser_ParseYContainerCookie(t *testing.T) {
	validTestCases := []struct {
		TestName string
		Value    string
		// if current time is 0 then no check for expired cookies
		CurrentTime    int64
		HasExpireField bool
		Expected       models.YCookie
	}{
		{
			TestName:       "Single subcookie",
			Value:          "key.value",
			HasExpireField: false,
			Expected: models.YCookie{
				RawString: "key.value",
				Subcookies: map[string]models.YSubcookie{
					"key": {
						Name:   "key",
						Value:  "value",
						Expire: 0,
					},
				},
			},
		},
		{
			TestName:       "Two subcookies",
			Value:          "apple.42#banana.true",
			HasExpireField: false,
			Expected: models.YCookie{
				RawString: "apple.42#banana.true",
				Subcookies: map[string]models.YSubcookie{
					"apple": {
						Name:   "apple",
						Value:  "42",
						Expire: 0,
					},
					"banana": {
						Name:   "banana",
						Value:  "true",
						Expire: 0,
					},
				},
			},
		},
		{
			TestName:       "Single subcookie with timestamp",
			Value:          "721828800.key.value",
			CurrentTime:    0,
			HasExpireField: true,
			Expected: models.YCookie{
				RawString: "721828800.key.value",
				Subcookies: map[string]models.YSubcookie{
					"key": {
						Name:   "key",
						Value:  "value",
						Expire: 721828800,
					},
				},
			},
		},
		{
			TestName:       "Two subcookies with timestamp",
			Value:          "721828800.apple.42#1602061207.banana.true",
			CurrentTime:    0,
			HasExpireField: true,
			Expected: models.YCookie{
				RawString: "721828800.apple.42#1602061207.banana.true",
				Subcookies: map[string]models.YSubcookie{
					"apple": {
						Name:   "apple",
						Value:  "42",
						Expire: 721828800,
					},
					"banana": {
						Name:   "banana",
						Value:  "true",
						Expire: 1602061207,
					},
				},
			},
		},
		{
			TestName:       "Outdated second cookie",
			Value:          "1600.apple.42#700.banana.true",
			CurrentTime:    800,
			HasExpireField: true,
			Expected: models.YCookie{
				RawString: "1600.apple.42",
				Subcookies: map[string]models.YSubcookie{
					"apple": {
						Name:   "apple",
						Value:  "42",
						Expire: 1600,
					},
				},
			},
		},
		{
			TestName:       "Outdated first cookie",
			Value:          "700.apple.42#1600.banana.true",
			CurrentTime:    800,
			HasExpireField: true,
			Expected: models.YCookie{
				RawString: "1600.banana.true",
				Subcookies: map[string]models.YSubcookie{
					"banana": {
						Name:   "banana",
						Value:  "true",
						Expire: 1600,
					},
				},
			},
		},
		{
			TestName:       "second older then first cookie with same name",
			Value:          "700.banana.42#1600.banana.true",
			CurrentTime:    699,
			HasExpireField: true,
			Expected: models.YCookie{
				RawString: "1600.banana.true",
				Subcookies: map[string]models.YSubcookie{
					"banana": {
						Name:   "banana",
						Value:  "true",
						Expire: 1600,
					},
				},
			},
		},
		{
			TestName:       "first older then second cookie with same name",
			Value:          "1600.banana.42#700.banana.true",
			CurrentTime:    699,
			HasExpireField: true,
			Expected: models.YCookie{
				RawString: "1600.banana.42",
				Subcookies: map[string]models.YSubcookie{
					"banana": {
						Name:   "banana",
						Value:  "42",
						Expire: 1600,
					},
				},
			},
		},
	}

	for _, item := range validTestCases {
		t.Run("Valid_"+item.TestName, func(t *testing.T) {
			ctrl := gomock.NewController(t)

			originRequestKeeperMock := NewMockoriginRequestKeeper(ctrl)
			requestKeeperMock := NewMockrequestGetter(ctrl)
			timeProviderMock := NewMocktimeProvider(ctrl)
			timeProviderMock.EXPECT().GetCurrentTime().Return(time.Unix(item.CurrentTime, 0)).AnyTimes()

			actual, err := NewParser(originRequestKeeperMock, requestKeeperMock, timeProviderMock, common.Production).parseYCookie(item.Value, item.HasExpireField)
			if assert.NoError(t, err) {
				assert.Equal(t, item.Expected, actual)
			}
		})
	}

	invalidTestCases := []struct {
		TestName       string
		Value          string
		HasExpireField bool
	}{
		{"Empty subcookie after hash", "key.value#", false},
		{"Empty subcookie before hash", "#key.value", false},
		{"Only hash symbol", "#", false},
		{"Two hashes", "key1.value1##key2.value2", false},

		{"No timestamp", "key.value", true},
		{"Missing timestamp 2nd subcookie", "721828800.key1.value#key2.value", true},
		{"Missing timestamp 1st subcookie", "key1.value#721828800.key2.value", true},
	}

	for _, item := range invalidTestCases {
		t.Run("Invalid_"+item.TestName, func(t *testing.T) {
			ctrl := gomock.NewController(t)

			originRequestKeeperMock := NewMockoriginRequestKeeper(ctrl)
			requestKeeperMock := NewMockrequestGetter(ctrl)
			timeProviderMock := NewMocktimeProvider(ctrl)
			timeProviderMock.EXPECT().GetCurrentTime().Return(time.Unix(0, 0)).AnyTimes()

			_, err := NewParser(originRequestKeeperMock, requestKeeperMock, timeProviderMock, common.Production).parseYCookie(item.Value, item.HasExpireField)
			assert.Error(t, err)
		})
	}
}

func Test_parser_parse(t *testing.T) {
	type testCase struct {
		name    string
		headers http.Header
		// if current time is 0 then no check for expired cookies
		CurrentTime int64
		want        models.YaCookies
		wantErrFunc assert.ErrorAssertionFunc
	}

	cases := []testCase{
		{
			name:    "no cookie header",
			headers: make(http.Header),
			want: models.YaCookies{
				IsYandexUIDGenerated: true,
			},
			wantErrFunc: assert.NoError,
		},
		{
			name: "single cookie header",
			headers: http.Header{
				"Cookie": []string{
					"yandex_gid=213; " +
						"yp=100.fruit.apple#300.city.moscow; " +
						"ys=show_morda.yes#some_flag.1; " +
						"yandexuid=1234567891234567890; " +
						"Session_id=someRand0mStr1ng; " +
						"sessionid2=someRand0mStr1ng2",
				},
			},
			want: models.YaCookies{YandexGID: 213,
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
				YandexUIDSalted: 435442591,
				SessionID:       "someRand0mStr1ng",
				SessionID2:      "someRand0mStr1ng2",
			},
			wantErrFunc: assert.NoError,
		},
		{
			name: "single cookie header with multiple values",
			headers: http.Header{
				"Cookie": []string{
					"yandex_gid=213; " +
						"yp=100.fruit.apple#300.city.moscow; " +
						"ys=show_morda.yes#some_flag.1; " +
						"yandexuid=1234567891234567890; " +
						"Session_id=someRand0mStr1ng; " +
						"sessionid2=someRand0mStr1ng2; " +
						"yandex_gid=2; " +
						"yp=100.fruit.banana#300.city.piter; " +
						"ys=show_morda.no#some_flag.0; " +
						"yandexuid=4444444444444444; " +
						"Session_id=someOtherString",
				},
			},
			want: models.YaCookies{YandexGID: 213,
				Yp: models.YCookie{
					RawString: "100.fruit.banana#300.city.piter",
					Subcookies: map[string]models.YSubcookie{
						"fruit": {
							Name:   "fruit",
							Value:  "banana",
							Expire: 100,
						},
						"city": {
							Name:   "city",
							Value:  "piter",
							Expire: 300,
						},
					},
				},
				Ys: models.YCookie{
					RawString: "show_morda.no#some_flag.0",
					Subcookies: map[string]models.YSubcookie{
						"show_morda": {
							Name:  "show_morda",
							Value: "no",
						},
						"some_flag": {
							Name:  "some_flag",
							Value: "0",
						},
					},
				},
				YandexUID:       "1234567891234567890",
				YandexUIDSalted: 435442591,
				SessionID:       "someRand0mStr1ng",
				SessionID2:      "someRand0mStr1ng2",
			},
			wantErrFunc: assert.NoError,
		},
		{
			name: "several cookie headers",
			headers: http.Header{
				"Cookie": []string{
					"yandexuid=3333333331234567890; yandexuid=4444444441234567890",
					"yandexuid=1234567891234567890",
				},
			},
			want: models.YaCookies{
				YandexUID:       "1234567891234567890",
				YandexUIDSalted: 435442591,
			},
			wantErrFunc: assert.NoError,
		},

		{
			name: "expired yp cookie",
			headers: map[string][]string{
				"Cookie": {"yp=10.cow.milk#19.foo.bar#30.goat.grass"},
			},
			CurrentTime: 20,
			want: models.YaCookies{
				IsYandexUIDGenerated: true,
				Yp: models.YCookie{
					RawString: "30.goat.grass",
					Subcookies: map[string]models.YSubcookie{
						"goat": {
							Name:   "goat",
							Value:  "grass",
							Expire: 30,
						},
					},
				},
			},
			wantErrFunc: assert.NoError,
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			timeProviderMock := NewMocktimeProvider(ctrl)
			timeProviderMock.EXPECT().GetCurrentTime().Return(time.Unix(tt.CurrentTime, 0)).AnyTimes()
			p := &parser{
				timeProvider: timeProviderMock,
			}
			got, err := p.parse(tt.headers)
			tt.wantErrFunc(t, err)
			assert.Equal(t, tt.want, got)
		})
	}
}

func Test_parser_Parse(t *testing.T) {
	type testCase struct {
		name        string
		headers     map[string][]string
		request     models.Request
		CurrentTime int64
		environment common.Environment
		want        models.YaCookies
		wantErrFunc assert.ErrorAssertionFunc
	}

	cases := []testCase{
		{
			name: "regular case",
			headers: map[string][]string{
				"Cookie": {"yandex_gid=213; yp=100.fruit.apple#300.city.moscow; ys=show_morda.yes#some_flag.1; yandexuid=1234567891234567890; Session_id=someRand0mStr1ng; sessionid2=someRand0mStr1ng2"},
			},
			want: models.YaCookies{
				YandexGID: 213,
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
				YandexUIDSalted: 435442591,
				SessionID:       "someRand0mStr1ng",
				SessionID2:      "someRand0mStr1ng2",
			},
			wantErrFunc: assert.NoError,
		},
		{
			name: "duplicated values",
			headers: map[string][]string{
				"Cookie": {
					"yandex_gid=2; yp=100.fruit.banana#300.city.piter; ys=show_morda.no#some_flag.0; yandexuid=4444444441234567890; Session_id=someOtherString",
					"yandex_gid=213; yp=100.fruit.apple#300.city.moscow; ys=show_morda.yes#some_flag.1; yandexuid=1234567891234567890; Session_id=someRand0mStr1ng; sessionid2=someRand0mStr1ng2",
				},
			},
			want: models.YaCookies{
				YandexGID: 213,
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
				YandexUIDSalted: 435442591,
				SessionID:       "someRand0mStr1ng",
				SessionID2:      "someRand0mStr1ng2",
			},
			wantErrFunc: assert.NoError,
		},
		{
			name: "first yandexuid is empty",
			headers: map[string][]string{
				"Cookie": {"yandexuid=; yandexuid=1234567891234567890"},
			},
			want: models.YaCookies{
				YandexUID:       "1234567891234567890",
				YandexUIDSalted: 435442591,
			},
			wantErrFunc: assert.NoError,
		},
		{
			name: "no yandexuid in cookies",
			headers: map[string][]string{
				"Cookie":        {"yandex_gid=213"},
				randomUIDHeader: {"1234567891234567890"},
			},
			want: models.YaCookies{
				YandexGID:            213,
				YandexUID:            "1234567891234567890",
				YandexUIDSalted:      435442591,
				IsYandexUIDGenerated: true,
			},
			wantErrFunc: assert.NoError,
		},
		{
			name: "invalid yandexuid",
			headers: map[string][]string{
				"Cookie":        {"yandex_gid=213; yandexuid=1234567890"},
				randomUIDHeader: {"1234567891234567890"},
			},
			want: models.YaCookies{
				YandexGID:            213,
				YandexUID:            "1234567891234567890",
				YandexUIDSalted:      435442591,
				IsYandexUIDGenerated: true,
			},
			wantErrFunc: assert.Error,
		},
		{
			name: "overriding from CGI-arg in testing env",
			headers: map[string][]string{
				"Cookie":        {"yandexuid=6666666661234567890"},
				randomUIDHeader: {"4444444441234567890"},
			},
			request: models.Request{
				CGI: map[string][]string{
					"yandexuid": {"1234567891234567890"},
				},
				IsInternal: true,
			},
			environment: common.Testing,
			want: models.YaCookies{
				YandexUID:       "1234567891234567890",
				YandexUIDSalted: 435442591,
			},
			wantErrFunc: assert.NoError,
		},
		{
			name: "expired yp cookie",
			headers: map[string][]string{
				"Cookie": {"yp=10.cow.milk#30.goat.grass"},
			},
			CurrentTime: 20,
			want: models.YaCookies{
				IsYandexUIDGenerated: true,
				Yp: models.YCookie{
					RawString: "30.goat.grass",
					Subcookies: map[string]models.YSubcookie{
						"goat": {
							Name:   "goat",
							Value:  "grass",
							Expire: 30,
						},
					},
				},
			},
			wantErrFunc: assert.NoError,
		},
		{
			name: "yp contains yb subcookie",
			headers: map[string][]string{
				"Cookie": {"yp=1666777888.cow.milk#1777666888.goat.grass#1888999444.yb.16_9_1_1192:0:1476540563:1544959729:1057:0"},
			},
			CurrentTime: 1658401218,
			want: models.YaCookies{
				IsYandexUIDGenerated: true,
				Yp: models.YCookie{
					RawString: "1666777888.cow.milk#1777666888.goat.grass#1888999444.yb.16_9_1_1192:0:1476540563:1544959729:1057:0",
					Subcookies: map[string]models.YSubcookie{
						"cow": {
							Name:   "cow",
							Value:  "milk",
							Expire: 1666777888,
						},
						"goat": {
							Name:   "goat",
							Value:  "grass",
							Expire: 1777666888,
						},
						"yb": {
							Name:   "yb",
							Value:  "16_9_1_1192:0:1476540563:1544959729:1057:0",
							Expire: 1888999444,
						},
					},
				},
				YaBroswerInfo: common.NewOptional(models.YbSubcookieYaBroswerInfo{
					MajorVersion:       "16_9",
					BroswerAgeInDays:   1312,
					LastVisitAgeInDays: 792,
					MordaVisitCount:    1057,
				}),
			},
			wantErrFunc: assert.NoError,
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			preparedHeaders := http.Header{}
			for key, values := range tt.headers {
				headerKey := http.CanonicalHeaderKey(key)
				for _, value := range values {
					preparedHeaders.Add(headerKey, value)
				}
			}
			ctrl := gomock.NewController(t)
			originRequestKeeperMock := NewMockoriginRequestKeeper(ctrl)
			originRequestKeeperMock.EXPECT().GetOriginRequest().Return(&models.OriginRequest{
				Headers: preparedHeaders,
			}, nil).MaxTimes(1)

			requestKeeperMock := NewMockrequestGetter(ctrl)
			requestKeeperMock.EXPECT().GetRequest().Return(tt.request).AnyTimes()

			timeProviderMock := NewMocktimeProvider(ctrl)
			timeProviderMock.EXPECT().GetCurrentTime().Return(time.Unix(tt.CurrentTime, 0)).AnyTimes()

			got, err := NewParser(originRequestKeeperMock, requestKeeperMock, timeProviderMock, tt.environment).Parse()
			tt.wantErrFunc(t, err)
			assert.Equal(t, tt.want, got)
		})
	}
}

func Test_parser_processYandexUIDSalted(t *testing.T) {
	type args struct {
		yandexUID string
	}
	tests := []struct {
		name string
		args args
		want uint32
	}{
		{
			name: "yandexuid - test",
			args: args{
				yandexUID: "test",
			},
			want: 2291272135,
		},
		{
			name: "yandexuid - 1 only",
			args: args{
				yandexUID: "11111111111111",
			},
			want: 2926973284,
		},
		{
			name: "yandexuid - rnd",
			args: args{
				yandexUID: "128049812831278",
			},
			want: 3688134480,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			p := &parser{}

			got := p.GetYandexUIDSalted(tt.args.yandexUID)

			require.Equal(t, tt.want, got)
		})
	}
}

func Test_parser_updateYandexUID(t *testing.T) {
	type args struct {
		cookieUID string
		headerUID string
		request   models.Request
		env       common.Environment
	}
	tests := []struct {
		name            string
		args            args
		wantUID         string
		wantIsGenerated bool
	}{
		{
			name: "empty yandexuid overridden by header",
			args: args{
				cookieUID: "",
				headerUID: "128049812831278",
			},
			wantUID:         "128049812831278",
			wantIsGenerated: true,
		},
		{
			name: "non-empty yandexuid",
			args: args{
				cookieUID: "11111111111111",
				headerUID: "128049812831278",
			},
			wantUID:         "11111111111111",
			wantIsGenerated: false,
		},
		{
			name: "is API",
			args: args{
				cookieUID: "11111111111111",
				headerUID: "22222222222222",
				request: models.Request{
					APIInfo: models.APIInfo{
						Name: "search",
					},
					CGI: url.Values{"yuid": {"33333333333333"}},
				},
			},
			wantUID:         "33333333333333",
			wantIsGenerated: false,
		},
		{
			name: "is API, empty CGI",
			args: args{
				cookieUID: "11111111111111",
				headerUID: "22222222222222",
				request: models.Request{
					APIInfo: models.APIInfo{
						Name: "search",
					},
					CGI: url.Values{},
				},
			},
			wantUID:         "",
			wantIsGenerated: false,
		},
		{
			name: "testing from CGI",
			args: args{
				cookieUID: "11111111111111",
				headerUID: "22222222222222",
				request: models.Request{
					CGI:        url.Values{"yandexuid": {"4444444441234567890"}},
					IsInternal: true,
				},
				env: common.Testing,
			},
			wantUID:         "4444444441234567890",
			wantIsGenerated: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			requestGetterMock := NewMockrequestGetter(ctrl)
			requestGetterMock.EXPECT().GetRequest().Return(tt.args.request)

			p := &parser{
				requestGetter: requestGetterMock,
				environment:   tt.args.env,
			}

			headers := http.Header{}
			headers.Add(randomUIDHeader, tt.args.headerUID)
			gotUID, gotIsGenerated := p.updateYandexUID(tt.args.cookieUID, headers)
			assert.Equal(t, tt.wantUID, gotUID)
			assert.Equal(t, tt.wantIsGenerated, gotIsGenerated)
		})
	}
}

func Test_parser_parseHTTPCookies(t *testing.T) {
	type testCase struct {
		name         string
		cookieHeader string
		want         map[string]string
	}

	cases := []testCase{
		{
			name:         "empty string",
			cookieHeader: "",
			want:         make(map[string]string),
		},
		{
			name:         "regular case",
			cookieHeader: "town=korolyov",
			want: map[string]string{
				"town": "korolyov",
			},
		},
		{
			name:         "single header value with several cookies",
			cookieHeader: "town=korolyov; fruit=apple",
			want: map[string]string{
				"town":  "korolyov",
				"fruit": "apple",
			},
		},
		{
			name:         "duplicated cookie key",
			cookieHeader: "country=italy; country=russia",
			want: map[string]string{
				"country": "italy",
			},
		},
		{
			name:         "duplicated cookie with first empty value",
			cookieHeader: "country=; country=italy",
			want: map[string]string{
				"country": "italy",
			},
		},
		{
			name:         "duplicated cookie with first empty value in single header and several not-empty cookieHeader",
			cookieHeader: "country=; country=italy; country=russia",
			want: map[string]string{
				"country": "italy",
			},
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			items := make([]string, 0, len(tt.want))
			for k, v := range tt.want {
				items = append(items, fmt.Sprintf("%s=%s", k, v))
			}
			r := http.Request{
				Header: map[string][]string{
					"Cookie": {strings.Join(items, "; ")},
				},
			}
			expectedCookies := r.Cookies()

			p := &parser{}
			actualCookies := p.parseHTTPCookies(tt.cookieHeader)

			assert.ElementsMatch(t, expectedCookies, actualCookies)
		})
	}
}

func Test_parser_isValidYandexUID(t *testing.T) {
	type testCase struct {
		name      string
		yandexuid string
		wantFunc  assert.BoolAssertionFunc
	}

	cases := []testCase{
		{
			name:      "empty string",
			yandexuid: "",
			wantFunc:  assert.False,
		},
		{
			name:      "not a yandexuid",
			yandexuid: "yandexuid",
			wantFunc:  assert.False,
		},
		{
			name:      "too short value",
			yandexuid: "15111992",
			wantFunc:  assert.False,
		},
		{
			name:      "too long value",
			yandexuid: "314159265358979323846264338327950288",
			wantFunc:  assert.False,
		},
		{
			name:      "old timestamp",
			yandexuid: "444444440777777777",
			wantFunc:  assert.False,
		},
		{
			name:      "leading zero in generated number",
			yandexuid: "0123456781234567890",
			wantFunc:  assert.False,
		},
		{
			name:      "minimal timestamp",
			yandexuid: "3333333331000000000",
			wantFunc:  assert.True,
		},
		{
			name:      "maximal timestamp",
			yandexuid: "3333333339999999999",
			wantFunc:  assert.True,
		},
		{
			name:      "seven digits in generated number",
			yandexuid: "12345671234567890",
			wantFunc:  assert.True,
		},
		{
			name:      "eight digits in generated number",
			yandexuid: "123456781234567890",
			wantFunc:  assert.True,
		},
		{
			name:      "regular value",
			yandexuid: "1234567891234567890",
			wantFunc:  assert.True,
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			p := &parser{}
			actual := p.isValidYandexUID(tt.yandexuid)
			tt.wantFunc(t, actual)
		})
	}
}

func Test_parser_getTestingYandexUID(t *testing.T) {
	type testCase struct {
		name string
		env  common.Environment
		req  models.Request
		want string
	}

	cases := []testCase{
		{
			name: "production",
			env:  common.Production,
			req: models.Request{
				IsInternal: false,
				CGI: url.Values{
					"yandexuid": {"4444444441234567890"},
				},
			},
			want: "",
		},
		{
			name: "not internal request",
			env:  common.Testing,
			req: models.Request{
				IsInternal: false,
				CGI: url.Values{
					"yandexuid": {"4444444441234567890"},
				},
			},
			want: "",
		},
		{
			name: "no CGI argument",
			env:  common.Testing,
			req: models.Request{
				IsInternal: true,
				CGI: url.Values{
					"some_arg": {"some_value"},
				},
			},
			want: "",
		},
		{
			name: "invalid yandexuid",
			env:  common.Testing,
			req: models.Request{
				IsInternal: true,
				CGI: url.Values{
					"yandexuid": {"123"},
				},
			},
			want: "",
		},
		{
			name: "regular case",
			env:  common.Testing,
			req: models.Request{
				IsInternal: true,
				CGI: url.Values{
					"yandexuid": {"4444444441234567890"},
				},
			},
			want: "4444444441234567890",
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			p := &parser{
				environment: tt.env,
			}
			actual := p.getTestingYandexUID(tt.req)
			assert.Equal(t, tt.want, actual)
		})
	}
}

func Test_parser_stringYSubcookie(t *testing.T) {
	type args struct {
		subcookie      models.YSubcookie
		hasExpireField bool
	}
	tests := []struct {
		name string
		args args
		want string
	}{
		{
			name: "ordinary yp cookie",
			args: args{
				subcookie: models.YSubcookie{
					Name:   "city",
					Value:  "moscow",
					Expire: 1234567890,
				},
				hasExpireField: true,
			},
			want: "1234567890.city.moscow",
		},
		{
			name: "ordinary ys cookie",
			args: args{
				subcookie: models.YSubcookie{
					Name:   "city",
					Value:  "moscow",
					Expire: 1234567890,
				},
				hasExpireField: false,
			},
			want: "city.moscow",
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			pa := &parser{}
			assert.Equalf(t, tt.want, pa.stringYSubcookie(tt.args.subcookie, tt.args.hasExpireField), "stringYSubcookie(%v, %v)", tt.args.subcookie, tt.args.hasExpireField)
		})
	}
}

func Test_parser_parseYBSubcookie(t *testing.T) {
	type testCase struct {
		name        string
		arg         string
		want        *parsedYBSubcookie
		wantErrFunc assert.ErrorAssertionFunc
	}

	cases := []testCase{
		{
			name:        "empty string",
			arg:         "",
			want:        nil,
			wantErrFunc: assert.Error,
		},
		{
			name:        "corrupted escaping",
			arg:         "16_4_0_7916%_3A0%3A1462343065%%%%3A1545224765%3A1502%3A0",
			want:        nil,
			wantErrFunc: assert.Error,
		},
		{
			name: "regular case",
			arg:  "16_9_1_1192:0:1476540563:1544959729:1057:0",
			want: &parsedYBSubcookie{
				BrowserVersion:           "16_9_1_1192",
				ChannelNumber:            "0",
				BroswerInstallTimestamp:  1476540563,
				LastMordaVisitTimestamp:  1544959729,
				MordaVisitCount:          1057,
				BrowserDeletionTimestamp: 0,
			},
			wantErrFunc: assert.NoError,
		},
		{
			name: "missing channel and deletion timestamp",
			arg:  "17_7_1_791::1506307718:1506307718:1",
			want: &parsedYBSubcookie{
				BrowserVersion:           "17_7_1_791",
				ChannelNumber:            "",
				BroswerInstallTimestamp:  1506307718,
				LastMordaVisitTimestamp:  1506307718,
				MordaVisitCount:          1,
				BrowserDeletionTimestamp: 0,
			},
			wantErrFunc: assert.NoError,
		},
		{
			name: "without deletion timestamp",
			arg:  "15_6_2311_4046:1955450:1434476958:1499591193:11:",
			want: &parsedYBSubcookie{
				BrowserVersion:           "15_6_2311_4046",
				ChannelNumber:            "1955450",
				BroswerInstallTimestamp:  1434476958,
				LastMordaVisitTimestamp:  1499591193,
				MordaVisitCount:          11,
				BrowserDeletionTimestamp: 0,
			},
			wantErrFunc: assert.NoError,
		},
		{
			name: "escaped colon",
			arg:  "16_4_0_7916%3A0%3A1462343065%3A1545224765%3A1502%3A0",
			want: &parsedYBSubcookie{
				BrowserVersion:           "16_4_0_7916",
				ChannelNumber:            "0",
				BroswerInstallTimestamp:  1462343065,
				LastMordaVisitTimestamp:  1545224765,
				MordaVisitCount:          1502,
				BrowserDeletionTimestamp: 0,
			},
			wantErrFunc: assert.NoError,
		},
		{
			name: "non-zero channel",
			arg:  "14_5_1847_18825:2139531:1407773256:1541348116:15:0",
			want: &parsedYBSubcookie{
				BrowserVersion:           "14_5_1847_18825",
				ChannelNumber:            "2139531",
				BroswerInstallTimestamp:  1407773256,
				LastMordaVisitTimestamp:  1541348116,
				MordaVisitCount:          15,
				BrowserDeletionTimestamp: 0,
			},
			wantErrFunc: assert.NoError,
		},
		{
			name: "strange channel number",
			arg:  "15_7_2357_2877:2153751-211:1449392323:1542044832:5:0",
			want: &parsedYBSubcookie{
				BrowserVersion:           "15_7_2357_2877",
				ChannelNumber:            "2153751-211",
				BroswerInstallTimestamp:  1449392323,
				LastMordaVisitTimestamp:  1542044832,
				MordaVisitCount:          5,
				BrowserDeletionTimestamp: 0,
			},
			wantErrFunc: assert.NoError,
		},
		{
			name: "only install timestamp, without Morda visits",
			arg:  "16_2_0_3539:0:1462967375",
			want: &parsedYBSubcookie{
				BrowserVersion:           "16_2_0_3539",
				ChannelNumber:            "0",
				BroswerInstallTimestamp:  1462967375,
				LastMordaVisitTimestamp:  0,
				MordaVisitCount:          0,
				BrowserDeletionTimestamp: 0,
			},
			wantErrFunc: assert.NoError,
		},
		{
			name: "without Morda visits, but with browser deletion",
			arg:  "15_10_2454_3658:2121012:1448268738:::1448268850",
			want: &parsedYBSubcookie{
				BrowserVersion:           "15_10_2454_3658",
				ChannelNumber:            "2121012",
				BroswerInstallTimestamp:  1448268738,
				LastMordaVisitTimestamp:  0,
				MordaVisitCount:          0,
				BrowserDeletionTimestamp: 1448268850,
			},
			wantErrFunc: assert.NoError,
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			var p parser
			actual, err := p.parseYbSubcookie(tt.arg)
			tt.wantErrFunc(t, err)
			assert.Equal(t, tt.want, actual)
		})
	}
}

func Test_parser_extractMajorVersion(t *testing.T) {
	type testCase struct {
		name string
		arg  string
		want string
	}

	cases := []testCase{
		{
			name: "empty string",
			arg:  "",
			want: "",
		},
		{
			name: "regular case",
			arg:  "17_10_0_2017",
			want: "17_10",
		},
		{
			name: "without build version",
			arg:  "17_10_0",
			want: "17_10",
		},
		{
			name: "extra underscore after first number",
			arg:  "17__10_0_2017",
			want: "17",
		},
		{
			name: "extra underscore after second number",
			arg:  "17_10__0_2017",
			want: "17_10",
		},
		{
			name: "starts with underscore",
			arg:  "_17_10_0_2017",
			want: "",
		},
		{
			name: "single number",
			arg:  "17",
			want: "17",
		},
		{
			name: "single number with underscores",
			arg:  "17___",
			want: "17",
		},
		{
			name: "not a version",
			arg:  "__not_a_version__",
			want: "",
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			var p parser
			actual := p.extractMajorVersion(tt.arg)
			assert.Equal(t, tt.want, actual)
		})
	}
}

func Test_parser_parseYaBroswerInfoFromCookie(t *testing.T) {
	type testCase struct {
		name string
		yb   *parsedYBSubcookie
		time int
		want common.Optional[models.YbSubcookieYaBroswerInfo]
	}

	cases := []testCase{
		{
			name: "nil pointer",
			yb:   nil,
			want: common.NewOptionalNil[models.YbSubcookieYaBroswerInfo](),
		},
		{
			name: "common case",
			yb: &parsedYBSubcookie{
				BrowserVersion:           "16_9_1_1192",
				ChannelNumber:            "0",
				BroswerInstallTimestamp:  1476540563,
				LastMordaVisitTimestamp:  1544959729,
				MordaVisitCount:          1057,
				BrowserDeletionTimestamp: 0,
			},
			time: 1658401218,
			want: common.NewOptional(models.YbSubcookieYaBroswerInfo{
				MajorVersion:       "16_9",
				BroswerAgeInDays:   1312,
				LastVisitAgeInDays: 792,
				MordaVisitCount:    1057,
			}),
		},
		{
			name: "install and visit once",
			yb: &parsedYBSubcookie{
				BrowserVersion:           "16_9_1_1192",
				ChannelNumber:            "",
				BroswerInstallTimestamp:  1468837827,
				LastMordaVisitTimestamp:  1468837827,
				MordaVisitCount:          1,
				BrowserDeletionTimestamp: 0,
			},
			time: 1658401218,
			want: common.NewOptional(models.YbSubcookieYaBroswerInfo{
				MajorVersion:       "16_9",
				BroswerAgeInDays:   2194,
				LastVisitAgeInDays: 0,
				MordaVisitCount:    1,
			}),
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			var p parser
			actual := p.parseYaBroswerInfoFromCookie(tt.yb, tt.time)
			assert.Equal(t, tt.want, actual)
		})
	}
}
