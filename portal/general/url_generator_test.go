package urlgenerator

import (
	"fmt"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestViewport(t *testing.T) {
	cases := []struct {
		url      string
		expected string
	}{
		{
			url:      "",
			expected: "",
		},
		{
			url:      "http://mail.ru?fffff=333#333",
			expected: "http://mail.ru?fffff=333#333",
		},
		{
			url:      "http://yandex.ru",
			expected: "http://yandex.ru",
		},
		{
			url:      "http://yandex.ru/search?text=123#trolololo",
			expected: "viewport://?text=123#trolololo",
		},
		{
			url:      "http://yandex.ua/search?text=123#trolololo",
			expected: "viewport://?text=123#trolololo",
		},
		{
			url:      "http://yandex.by/search?text=123#trolololo",
			expected: "viewport://?text=123#trolololo",
		},
		{
			url:      "http://yandex.kz/search?text=123#trolololo",
			expected: "viewport://?text=123#trolololo",
		},
		{
			url:      "http://www.yandex.ru/search?text=123#trolololo",
			expected: "viewport://?text=123#trolololo",
		},
		{
			url:      "https://www.yandex.ua/search?text=123#trolololo",
			expected: "viewport://?text=123#trolololo",
		},
		{
			url:      "https://www.yandex.by/search?text=123#trolololo",
			expected: "viewport://?text=123#trolololo",
		},
		{
			url:      "http://www.yandex.kz/search?text=123#trolololo",
			expected: "viewport://?text=123#trolololo",
		},
		{
			url:      "http://www.yandex.com/search?text=123#trolololo",
			expected: "viewport://?text=123#trolololo",
		},
		{
			url:      "http://yandex.com.tr/search?text=123#trolololo",
			expected: "viewport://?text=123#trolololo",
		},
		{
			url:      "http://yandex.ru/yandsearch?text=123#trolololo",
			expected: "viewport://?text=123#trolololo",
		},
		{
			url:      "http://yandex.ua/yandsearch?text=123#trolololo",
			expected: "viewport://?text=123#trolololo",
		},
		{
			url:      "http://yandex.by/yandsearch?text=123#trolololo",
			expected: "viewport://?text=123#trolololo",
		},
		{
			url:      "http://yandex.kz////yandsearch//s/df//df//?text=123#trolololo",
			expected: "viewport://?text=123#trolololo",
		},
		{
			url:      "http://yandex.com/yandsearch/d/d/d/d/dfa/r?text=123#trolololo",
			expected: "viewport://?text=123#trolololo",
		},
		{
			url:      "http://yandex.com.tr/yandsearch?text=123#trolololo",
			expected: "viewport://?text=123#trolololo",
		},
		{
			url:      "http://yandex.ru/touchsearch?text=123#trolololo",
			expected: "viewport://?text=123#trolololo",
		},
		{
			url:      "http://yandex.ua////touchsearch?text=123#trolololo",
			expected: "viewport://?text=123#trolololo",
		},
		{
			url:      "http://yandex.by/touchsearch?text=123#trolololo",
			expected: "viewport://?text=123#trolololo",
		},
		{
			url:      "http://yandex.kz/touchsearch?text=123#trolololo",
			expected: "viewport://?text=123#trolololo",
		},
		{
			url:      "http://yandex.com/touchsearch?text=123#trolololo",
			expected: "viewport://?text=123#trolololo",
		},
		{
			url:      "http://yandex.com.tr/touchsearch?text=123#trolololo",
			expected: "viewport://?text=123#trolololo",
		},
		{
			url:      "http://yandex.ru/search",
			expected: "http://yandex.ru/search",
		},
		{
			url:      "http://yandex.ua/search#trolololo",
			expected: "http://yandex.ua/search#trolololo",
		},
		{
			url:      "http://yandex.by/search?",
			expected: "http://yandex.by/search?",
		},
	}

	for _, testCase := range cases {
		generator := generatorBase{}
		got, err := generator.MakeViewportURL(testCase.url)
		assert.NoError(t, err)
		assert.Equal(t, testCase.expected, got)
	}
}

func TestBrowser(t *testing.T) {
	cases := []struct {
		url                     string
		noredir                 bool
		addAppsearchHeaderParam bool
		expected                string
	}{
		{
			url:      "https://yandex.ru?portal=1",
			noredir:  true,
			expected: "browser://?noredir=1&url=https%3A%2F%2Fyandex.ru%3Fportal%3D1",
		},
		{
			url:      "https://yandex.ru?portal=1",
			expected: "browser://?noredir=0&url=https%3A%2F%2Fyandex.ru%3Fportal%3D1",
		},
		{
			url:                     "https://yandex.ru?portal=1",
			addAppsearchHeaderParam: true,
			expected:                "browser://?noredir=0&url=https%3A%2F%2Fyandex.ru%3Fappsearch_header%3D1%26portal%3D1",
		},
		{
			url:                     "https://yandex.ru?portal=1",
			noredir:                 true,
			addAppsearchHeaderParam: true,
			expected:                "browser://?noredir=1&url=https%3A%2F%2Fyandex.ru%3Fappsearch_header%3D1%26portal%3D1",
		},
		{
			url:                     "https://yandex.ru?appsearch_header=1",
			noredir:                 true,
			addAppsearchHeaderParam: true,
			expected:                "browser://?noredir=1&url=https%3A%2F%2Fyandex.ru%3Fappsearch_header%3D1",
		},
	}

	for _, testCase := range cases {
		generator := generatorBase{}
		got, err := generator.MakeBrowserURL(testCase.url, testCase.addAppsearchHeaderParam, testCase.noredir)
		assert.NoError(t, err)
		assert.Equal(t, testCase.expected, got)
	}
}

func TestMordanavigate(t *testing.T) {
	cases := []struct {
		url                     string
		fallback                string
		card                    string
		page                    string
		addAppsearchHeaderParam bool
		expected                string
	}{
		{
			url:      "https://yandex.ru?portal=1",
			card:     "weather/weather",
			expected: "mordanavigate://?card=weather%2Fweather&fallback=https%3A%2F%2Fyandex.ru%3Fportal%3D1",
		},
		{
			url:                     "https://yandex.ru?portal=1",
			card:                    "weather/weather",
			addAppsearchHeaderParam: true,
			expected:                "mordanavigate://?card=weather%2Fweather&fallback=https%3A%2F%2Fyandex.ru%3Fappsearch_header%3D1%26portal%3D1",
		},
		{
			url:                     "https://yandex.ru?appsearch_header=1",
			card:                    "weather/weather",
			addAppsearchHeaderParam: true,
			expected:                "mordanavigate://?card=weather%2Fweather&fallback=https%3A%2F%2Fyandex.ru%3Fappsearch_header%3D1",
		},
		{
			url:      "https://local.yandex.ru/?event_id=333",
			fallback: "yellowskin://?url=https%3A%2F%2Flocal.yandex.ru%2F%3Fevent_id%3D333",
			page:     "local",
			expected: "mordanavigate://?fallback=yellowskin%3A%2F%2F%3Furl%3Dhttps%253A%252F%252Flocal.yandex.ru%252F%253Fevent_id%253D333&page=local&url=https%3A%2F%2Flocal.yandex.ru%2F%3Fevent_id%3D333",
		},
	}

	for _, testCase := range cases {
		generator := generatorBase{}
		got, err := generator.MakeMordanavigateURL(testCase.url, testCase.addAppsearchHeaderParam, testCase.page, testCase.card, testCase.fallback)
		assert.NoError(t, err)
		assert.Equal(t, testCase.expected, got)
	}
}

func TestTranslate(t *testing.T) {
	cases := []struct {
		url                   string
		isNewTranslateEnabled bool
		noredir               bool
		fallbackBrowser       bool
		expected              string
	}{
		{
			url:                   "https://translate.yandex.ru/",
			isNewTranslateEnabled: true,
			expected:              "translate://?url=https%3A%2F%2Ftranslate.yandex.ru%2F",
		},
		{
			url:      "https://translate.yandex.ru/",
			expected: "https://translate.yandex.ru/",
		},
		{
			url:             "https://translate.yandex.ru/",
			noredir:         true,
			fallbackBrowser: true,
			expected:        "browser://?noredir=1&url=https%3A%2F%2Ftranslate.yandex.ru%2F",
		},
	}

	for _, testCase := range cases {
		generator := generatorBase{
			isNewTranslateEnabled: testCase.isNewTranslateEnabled,
		}
		got, err := generator.MakeTranslateURL(testCase.url, testCase.fallbackBrowser, testCase.noredir)
		assert.NoError(t, err)
		assert.Equal(t, testCase.expected, got)
	}
}

func TestAppsearchHeader(t *testing.T) {
	url := "http://yandex.ru"
	expected := "http://yandex.ru?appsearch_header=1"
	generator := generatorBase{}

	got, err := generator.AddAppsearchHeaderParam(url, false)
	assert.NoError(t, err)
	assert.Equal(t, expected, got)

	got, err = generator.AddAppsearchHeaderParam(got, false)
	assert.NoError(t, err)
	assert.Equal(t, expected, got)
}

var ysAndroid600Test = YellowskinPrefix{
	PrimaryColor:   "#f3f1ed",
	SecondaryColor: "#000000",
}

var ysAndroid645Test = YellowskinPrefix{
	ButtonsColor:    "#91989b",
	OmniboxColor:    "#f0f0f0",
	StatusBarTheme:  "light",
	BackgroundColor: "#fefefe",
	TextColor:       "#000000",
}

var ysTVDefault = YellowskinPrefix{
	PrimaryColor:   "#42435e",
	SecondaryColor: "#ffffff",
}

var ysStocksDefault = YellowskinPrefix{
	PrimaryColor:   "#000000",
	SecondaryColor: "#ffffff",
}

var ysEdadealDefault = YellowskinPrefix{
	PrimaryColor:   "#2e9a3e",
	SecondaryColor: "#ffffff",
}

var ysEdadealAndroid645 = YellowskinPrefix{
	ButtonsColor:    "#ffffff",
	OmniboxColor:    "#288736",
	StatusBarTheme:  "dark",
	BackgroundColor: "#4b9645",
	TextColor:       "#ffffff",
}

func TestYellowskin(t *testing.T) {
	cases := []struct {
		platform   string
		version    int
		ysPrefixes YellowskinPrefixes
		expected   map[string]string
	}{
		{
			platform: "android",
			version:  5_000_000,
			ysPrefixes: YellowskinPrefixes{
				"default": ysAndroid600Test,
				"tv":      ysTVDefault,
				"stocks":  ysStocksDefault,
				"edadeal": ysEdadealDefault,
			},
			expected: map[string]string{
				"default": "yellowskin://?primary_color=%23f3f1ed&secondary_color=%23000000&url=https%3A%2F%2Fya.ru",
				"tv":      "yellowskin://?primary_color=%2342435e&secondary_color=%23ffffff&url=https%3A%2F%2Fya.ru",
				"stocks":  "yellowskin://?primary_color=%23000000&secondary_color=%23ffffff&url=https%3A%2F%2Fya.ru",
				"edadeal": "yellowskin://?primary_color=%232e9a3e&secondary_color=%23ffffff&url=https%3A%2F%2Fya.ru",
			},
		},
		{
			platform: "android",
			version:  6_000_000,
			ysPrefixes: YellowskinPrefixes{
				"default": ysAndroid600Test,
				"tv":      ysAndroid600Test,
				"stocks":  ysAndroid600Test,
				"edadeal": ysEdadealDefault,
			},
			expected: map[string]string{
				"default": "yellowskin://?primary_color=%23f3f1ed&secondary_color=%23000000&url=https%3A%2F%2Fya.ru",
				"tv":      "yellowskin://?primary_color=%23f3f1ed&secondary_color=%23000000&url=https%3A%2F%2Fya.ru",
				"stocks":  "yellowskin://?primary_color=%23f3f1ed&secondary_color=%23000000&url=https%3A%2F%2Fya.ru",
				"edadeal": "yellowskin://?primary_color=%232e9a3e&secondary_color=%23ffffff&url=https%3A%2F%2Fya.ru",
			},
		},
		{
			platform: "android",
			version:  6_040_500,
			ysPrefixes: YellowskinPrefixes{
				"default": ysAndroid645Test,
				"tv":      ysAndroid645Test,
				"stocks":  ysAndroid645Test,
				"edadeal": ysEdadealAndroid645,
			},
			expected: map[string]string{
				"default": "yellowskin://?background_color=%23fefefe&buttons_color=%2391989b&omnibox_color=%23f0f0f0&status_bar_theme=light&text_color=%23000000&url=https%3A%2F%2Fya.ru",
				"tv":      "yellowskin://?background_color=%23fefefe&buttons_color=%2391989b&omnibox_color=%23f0f0f0&status_bar_theme=light&text_color=%23000000&url=https%3A%2F%2Fya.ru",
				"stocks":  "yellowskin://?background_color=%23fefefe&buttons_color=%2391989b&omnibox_color=%23f0f0f0&status_bar_theme=light&text_color=%23000000&url=https%3A%2F%2Fya.ru",
				"edadeal": "yellowskin://?background_color=%234b9645&buttons_color=%23ffffff&omnibox_color=%23288736&status_bar_theme=dark&text_color=%23ffffff&url=https%3A%2F%2Fya.ru",
			},
		},
		{
			platform: "android",
			version:  6_050_000,
			ysPrefixes: YellowskinPrefixes{
				"default": ysAndroid645Test,
				"tv":      ysAndroid645Test,
				"stocks":  ysAndroid645Test,
				"edadeal": ysEdadealAndroid645,
			},
			expected: map[string]string{
				"default": "yellowskin://?background_color=%23fefefe&buttons_color=%2391989b&omnibox_color=%23f0f0f0&status_bar_theme=light&text_color=%23000000&url=https%3A%2F%2Fya.ru",
				"tv":      "yellowskin://?background_color=%23fefefe&buttons_color=%2391989b&omnibox_color=%23f0f0f0&status_bar_theme=light&text_color=%23000000&url=https%3A%2F%2Fya.ru",
				"stocks":  "yellowskin://?background_color=%23fefefe&buttons_color=%2391989b&omnibox_color=%23f0f0f0&status_bar_theme=light&text_color=%23000000&url=https%3A%2F%2Fya.ru",
				"edadeal": "yellowskin://?background_color=%234b9645&buttons_color=%23ffffff&omnibox_color=%23288736&status_bar_theme=dark&text_color=%23ffffff&url=https%3A%2F%2Fya.ru",
			},
		},
		{
			platform: "iphone",
			version:  2_050_000,
			ysPrefixes: YellowskinPrefixes{
				"default": ysAndroid600Test,
				"tv":      ysTVDefault,
				"stocks":  ysStocksDefault,
				"edadeal": ysEdadealDefault,
			},
			expected: map[string]string{
				"default": "yellowskin://?primary_color=%23f3f1ed&secondary_color=%23000000&url=https%3A%2F%2Fya.ru",
				"tv":      "yellowskin://?primary_color=%2342435e&secondary_color=%23ffffff&url=https%3A%2F%2Fya.ru",
				"stocks":  "yellowskin://?primary_color=%23000000&secondary_color=%23ffffff&url=https%3A%2F%2Fya.ru",
				"edadeal": "yellowskin://?primary_color=%232e9a3e&secondary_color=%23ffffff&url=https%3A%2F%2Fya.ru",
			},
		},
		{
			platform: "iphone",
			version:  3_050_000,
			ysPrefixes: YellowskinPrefixes{
				"default": ysAndroid600Test,
				"tv":      ysAndroid600Test,
				"stocks":  ysAndroid600Test,
				"edadeal": ysEdadealDefault,
			},
			expected: map[string]string{
				"default": "yellowskin://?primary_color=%23f3f1ed&secondary_color=%23000000&url=https%3A%2F%2Fya.ru",
				"tv":      "yellowskin://?primary_color=%23f3f1ed&secondary_color=%23000000&url=https%3A%2F%2Fya.ru",
				"stocks":  "yellowskin://?primary_color=%23f3f1ed&secondary_color=%23000000&url=https%3A%2F%2Fya.ru",
				"edadeal": "yellowskin://?primary_color=%232e9a3e&secondary_color=%23ffffff&url=https%3A%2F%2Fya.ru",
			},
		},
	}

	ids := []string{"default", "tv", "stocks", "edadeal"}

	for _, testCase := range cases {
		generator := generatorBase{
			appPlatform:        testCase.platform,
			yellowskinPrefixes: testCase.ysPrefixes,
		}

		for _, id := range ids {
			t.Run(fmt.Sprintf("%s-%d-%s", testCase.platform, testCase.version, id),
				func(t *testing.T) {
					url := "https://ya.ru"
					got, err := generator.MakeYellowskinURL(url, id, false, false, None)
					assert.NoError(t, err)
					assert.Equal(t, testCase.expected[id], got)

					url = "//ya.ru"
					got, err = generator.MakeYellowskinURL(url, id, false, false, None)
					assert.NoError(t, err)
					assert.Equal(t, testCase.expected[id], got)

					got, err = generator.MakeYellowskinURL(url, id, false, false, None)
					assert.NoError(t, err)
					assert.Equal(t, testCase.expected[id], got)

					url = "http://yandex.ru/search?text=123#trolololo"
					expected := "viewport://?text=123#trolololo"
					got, err = generator.MakeYellowskinURL(url, id, false, false, None)
					assert.NoError(t, err)
					assert.Equal(t, expected, got)

					got, err = generator.MakeYellowskinURL(url, id, false, false, None)
					assert.NoError(t, err)
					assert.Equal(t, expected, got)
				})
		}

	}
}

func TestYellowskinTurbo(t *testing.T) {
	cases := []struct {
		platform   string
		version    int
		ysPrefixes YellowskinPrefixes
		expected   map[string]string
	}{
		{
			platform: "android",
			version:  5_000_000,
			ysPrefixes: YellowskinPrefixes{
				"default": ysAndroid600Test,
				"tv":      ysTVDefault,
				"stocks":  ysStocksDefault,
				"edadeal": ysEdadealDefault,
			},
			expected: map[string]string{
				"default": "yellowskin://?primary_color=%23f3f1ed&secondary_color=%23000000&url=https%3A%2F%2Fyandex.ru%2Fturbo%3Ftext%3Dhttps%253A%252F%252Fya.ru",
				"tv":      "yellowskin://?primary_color=%2342435e&secondary_color=%23ffffff&url=https%3A%2F%2Fyandex.ru%2Fturbo%3Ftext%3Dhttps%253A%252F%252Fya.ru",
				"stocks":  "yellowskin://?primary_color=%23000000&secondary_color=%23ffffff&url=https%3A%2F%2Fyandex.ru%2Fturbo%3Ftext%3Dhttps%253A%252F%252Fya.ru",
				"edadeal": "yellowskin://?primary_color=%232e9a3e&secondary_color=%23ffffff&url=https%3A%2F%2Fyandex.ru%2Fturbo%3Ftext%3Dhttps%253A%252F%252Fya.ru",
			},
		},
	}

	ids := []string{"default", "tv", "stocks", "edadeal"}

	for _, testCase := range cases {
		generator := generatorBase{
			appPlatform:        testCase.platform,
			yellowskinPrefixes: testCase.ysPrefixes,
			hostTurbo:          "yandex.ru",
		}

		for _, id := range ids {
			t.Run(fmt.Sprintf("%s-%d-%s", testCase.platform, testCase.version, id),
				func(t *testing.T) {
					url := "https://ya.ru"
					got, err := generator.MakeYellowskinURL(url, id, true, false, None)
					assert.NoError(t, err)
					assert.Equal(t, testCase.expected[id], got)
				})
		}

	}
}

func TestIntentWp(t *testing.T) {
	generator := generatorBase{appPlatform: "wp"}
	url := "http://yandex.ru?a"
	got, err := generator.MakeIntentURL(url, "music", "", "", "", "", "", "", false)
	assert.NoError(t, err)
	assert.Equal(t, url, got)
}

func TestIntentAndroid(t *testing.T) {
	cases := []struct {
		url         string
		app         string
		pkg         string
		fallbackURL string
		intent      string
		intentArgs  string
		expected    string
	}{
		{
			url:      "https://maps.yandex.ru",
			pkg:      "ru.maps",
			expected: "intent://#MakeIntentURL;S.browser_fallback_url=https%3A%2F%2Fmaps.yandex.ru;package=ru.maps;end;",
		},
		{
			url:      "http://maps.yandex.ru",
			pkg:      "ru.maps",
			expected: "intent://#MakeIntentURL;S.browser_fallback_url=http%3A%2F%2Fmaps.yandex.ru;package=ru.maps;end;",
		},
		{
			url:      "//maps.yandex.ru",
			pkg:      "ru.maps",
			expected: "intent://#MakeIntentURL;S.browser_fallback_url=https%3A%2F%2Fmaps.yandex.ru;package=ru.maps;end;",
		},
		{
			url:      "https://maps.yandex.ru",
			pkg:      "ru.maps",
			intent:   "https://maps.yandex.ru",
			expected: "intent://maps.yandex.ru#MakeIntentURL;S.browser_fallback_url=https%3A%2F%2Fmaps.yandex.ru;package=ru.maps;scheme=http;end;",
		},
		{
			url:      "http://maps.yandex.ru",
			pkg:      "ru.maps",
			intent:   "http://maps.yandex.ru",
			expected: "intent://maps.yandex.ru#MakeIntentURL;S.browser_fallback_url=http%3A%2F%2Fmaps.yandex.ru;package=ru.maps;scheme=http;end;",
		},
		{
			url:      "//maps.yandex.ru",
			pkg:      "ru.maps",
			intent:   "//maps.yandex.ru",
			expected: "intent://maps.yandex.ru#MakeIntentURL;S.browser_fallback_url=https%3A%2F%2Fmaps.yandex.ru;package=ru.maps;scheme=http;end;",
		},
		{
			url:      "//maps.yandex.ru",
			expected: "//maps.yandex.ru",
		},
		{
			url:      "//maps.yandex.ru",
			intent:   "//maps.yandex.ru",
			expected: "intent://maps.yandex.ru#MakeIntentURL;S.browser_fallback_url=https%3A%2F%2Fmaps.yandex.ru;scheme=http;end;",
		},
		{
			pkg:      "ru.maps",
			expected: "intent://#MakeIntentURL;package=ru.maps;end;",
		},
		{
			app: "maps",
		},
		{
			url:         "https://maps.yandex.ru/?l=map,trf&ll=37.620393,55.75396&z=10",
			app:         "maps",
			fallbackURL: "https://maps.yandex.ru/moscow_traffic",
			intent:      "http://maps.yandex.ru",
			intentArgs:  "l=map,trf&ll=37.620393,55.75396&z=10",
			pkg:         "ru.yandex.yandexmaps",
			expected:    "intent://maps.yandex.ru?l=map,trf&ll=37.620393,55.75396&z=10#MakeIntentURL;S.browser_fallback_url=https%3A%2F%2Fmaps.yandex.ru%2Fmoscow_traffic;package=ru.yandex.yandexmaps;scheme=http;end;",
		},
	}

	generator := generatorBase{
		appPlatform: "android",
		isIntentOn:  true,
	}
	for _, testCase := range cases {
		got, err := generator.MakeIntentURL(testCase.url, testCase.app, testCase.pkg, testCase.intent, "", testCase.fallbackURL, "", testCase.intentArgs, false)
		assert.NoError(t, err)
		assert.Equal(t, testCase.expected, got)
	}
}
