package topnews

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestGetIDFromURL(t *testing.T) {
	tests := []struct {
		name          string
		URL           string
		expectedID    string
		expectedValid bool
	}{
		{
			name:          "URL with valid ID",
			URL:           "https://yandex.ua/news/story/Rejderi_zablokuvali_odnogo_z_najblshikh_virobnkv_pitno_vodi_Ekonya--856fd5ce033608e22f12af479358eb3e",
			expectedID:    "856fd5ce",
			expectedValid: true,
		},
		{
			name:          "URL two IDs",
			URL:           "https://yandex.ua/news/story/Rejderi_zablokuvali_odnogo_z_najblshikh_virobnkv_pitno_vodi_Ekonya--856fd5ce033608e22f12af479358eb3e--hf47g838g482g4fyg28fyf28g",
			expectedID:    "856fd5ce",
			expectedValid: true,
		},
		{
			name:          "URL with invalid ID: ID length is less then 8",
			URL:           "https://yandex.ua/news/story/Rejderi_zablokuvali_odnogo_z_najblshikh_virobnkv_pitno_vodi_Ekonya--856fd",
			expectedID:    "",
			expectedValid: false,
		},
		{
			name:          "URL with invalid ID: URL does not contain id",
			URL:           "https://yandex.ua/news/story/Rejderi_zablokuvali_odnogo_z_najblshikh_virobnkv_pitno_vodi_Ekonya",
			expectedID:    "",
			expectedValid: false,
		},
		{
			name:          "URL with invalid ID: empty URL",
			URL:           "",
			expectedID:    "",
			expectedValid: false,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			id, valid := getIDFromURL(tt.URL)
			require.Equal(t, tt.expectedID, id)
			require.Equal(t, tt.expectedValid, valid)
		})
	}
}

func TestSignURL(t *testing.T) {
	tests := []struct {
		name            string
		URL             string
		time            int64
		expectedSignURL string
		expectedErr     error
	}{
		{
			name:            "URL with exclude",
			URL:             "https://news.yandex.ru/api/v2/rubric?preset=morda_top_news_personal_touch&exclude=187390746%2C187389602%2C187384361%2C187388949%2C187378805%2C187383717%2C187389148%2C187367719%2C187385043%2C187385820%2C187387314%2C187381062%2C187387646%2C187369550%2C187361847%2C187384359%2C187374209%2C187390504%2C187373200%2C187383679%2C187369784%2C187374385%2C187378529%2C187378577%2C187385185%2C186164627%2C184806713%2C187375331%2C187381873%2C187369797&count=15&get_favorites_for=465177457&userid=465177457",
			time:            1648039779,
			expectedSignURL: "https://news.yandex.ru/api/v2/rubric?count=15&exclude=187390746%2C187389602%2C187384361%2C187388949%2C187378805%2C187383717%2C187389148%2C187367719%2C187385043%2C187385820%2C187387314%2C187381062%2C187387646%2C187369550%2C187361847%2C187384359%2C187374209%2C187390504%2C187373200%2C187383679%2C187369784%2C187374385%2C187378529%2C187378577%2C187385185%2C186164627%2C184806713%2C187375331%2C187381873%2C187369797&get_favorites_for=465177457&preset=morda_top_news_personal_touch&sign=6401abfbf5a26dbd1202efa190ae106b&userid=465177457",
			expectedErr:     nil,
		},
		{
			name:            "URL without exclude",
			URL:             "https://news.yandex.ru/api/v2/rubric?preset=morda_top_news_personal_touch&count=15&get_favorites_for=465177457&userid=465177457",
			time:            1648039779,
			expectedSignURL: "https://news.yandex.ru/api/v2/rubric?count=15&get_favorites_for=465177457&preset=morda_top_news_personal_touch&sign=5fa962f1128ba26ae0452cb01ba65018&userid=465177457",
			expectedErr:     nil,
		},
		{
			name:            "URL trusted",
			URL:             "https://news.yandex.ru/api/v2/rubric?preset=morda_top_news_personal_touch&exclude=187390746%2C187389602%2C187384361%2C187388949%2C187378805%2C187383717%2C187389148%2C187367719%2C187385043%2C187385820%2C187387314%2C187381062%2C187387646%2C187369550%2C187361847%2C187384359%2C187374209%2C187390504%2C187373200%2C187383679%2C187369784%2C187374385%2C187378529%2C187378577%2C187385185%2C186164627%2C184806713%2C187375331%2C187381873%2C187369797&count=15&get_favorites_for=465177457&userid=465177457&trusted=1",
			time:            1648039779,
			expectedSignURL: "https://news.yandex.ru/api/v2/rubric?count=15&exclude=187390746%2C187389602%2C187384361%2C187388949%2C187378805%2C187383717%2C187389148%2C187367719%2C187385043%2C187385820%2C187387314%2C187381062%2C187387646%2C187369550%2C187361847%2C187384359%2C187374209%2C187390504%2C187373200%2C187383679%2C187369784%2C187374385%2C187378529%2C187378577%2C187385185%2C186164627%2C184806713%2C187375331%2C187381873%2C187369797&get_favorites_for=465177457&preset=morda_top_news_personal_touch&sign=8725d7741e6e397f5bcd36f1ef7adf52&trusted=1&userid=465177457",
			expectedErr:     nil,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			sign, err := signURL(tt.URL, tt.time)
			require.Equal(t, tt.expectedSignURL, sign)
			require.Equal(t, tt.expectedErr, err)
		})
	}
}
