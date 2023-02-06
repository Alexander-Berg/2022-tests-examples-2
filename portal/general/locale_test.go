package locales

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func Test_MordaLangs_InitMordaLangs(t *testing.T) {
	type testCase struct {
		name     string
		selector string
		want     []Lang
	}
	cases := []testCase{
		{
			name:     "yaru",
			selector: "yaru",
			want:     []Lang{RU},
		},
		{
			name:     "tel",
			selector: "tel",
			want:     []Lang{RU},
		},
		{
			name:     "tv",
			selector: "tv",
			want:     []Lang{RU},
		},
		{
			name:     "hw",
			selector: "hw",
			want:     []Lang{RU},
		},
		{
			name:     "big",
			selector: "big",
			want:     []Lang{RU, BE, KK, TT, UK},
		},
		{
			name:     "touch",
			selector: "touch",
			want:     []Lang{RU, BE, KK, TT, UK},
		},
		{
			name:     "mob",
			selector: "mob",
			want:     []Lang{RU, BE, KK, TT, UK},
		},
		{
			name:     "intercept404",
			selector: "intercept404",
			want:     []Lang{RU, BE, KK, TT, UK},
		},
		{
			name:     "yabrotab",
			selector: "yabrotab",
			want:     []Lang{RU, BE, KK, TT, UK},
		},
		{
			name:     "api_search_2",
			selector: "api_search_2",
			want:     []Lang{RU, BE, KK, TT, UK, UZ, TR},
		},
		{
			name:     "api_search_config",
			selector: "api_search_config",
			want:     []Lang{RU, BE, KK, TT, UK, UZ, TR, BG, CS, DA, DE, EL, EN, ES, FI, FR, HR, HU, IT, LT, NL, NO, PL, PT, RO, SK, SL, SV},
		},
		{
			name:     "api_search_2_euro",
			selector: "api_search_2_euro",
			want:     []Lang{RU, BE, KK, TT, UK, UZ, TR, BG, CS, DA, DE, EL, EN, ES, FI, FR, HR, HU, IT, LT, NL, NO, PL, PT, RO, SK, SL, SV},
		},
		{
			name:     "api_widget_2",
			selector: "api_widget_2",
			want:     []Lang{RU, BE, KK, TT, UK, UZ, EN, TR, IT, FR},
		},
		{
			name:     "ios_widget",
			selector: "ios_widget",
			want:     []Lang{RU, BE, KK, TT, UK, EN, IT, FR, TR},
		},
		{
			name:     "comtr",
			selector: "comtr",
			want:     []Lang{TR},
		},
		{
			name:     "api_data_big",
			selector: "api_data_big",
			want:     []Lang{RU, UK, BE, EN, KK},
		},
		{
			name:     "verticals",
			selector: "verticals",
			want:     []Lang{RU, BE, KK, UK},
		},
		{
			name:     "com",
			selector: "com",
			want:     []Lang{EN, ID},
		},
		{
			name:     "uz",
			selector: "uz",
			want:     []Lang{UZ, RU},
		},
		{
			name:     "samsung",
			selector: "samsung",
			want:     []Lang{RU, BE, KK, TT, UK, AZ, UZ, GE, AR},
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			mordaLangs := newMordaLangs()
			actualLangs, exist := mordaLangs.Values[tt.selector]
			require.True(t, exist)
			assert.Equal(t, tt.want, actualLangs)
		})
	}
}

func Test_MordaLangs_getDefaultMordaLang(t *testing.T) {
	type testCase struct {
		name     string
		selector string
		want     string
	}
	cases := []testCase{
		{
			name:     "emply selector",
			selector: "",
			want:     "ru",
		},
		{
			name:     "unknown selector",
			selector: "default",
			want:     "ru",
		},
		{
			name:     "exist selector",
			selector: "comtr",
			want:     "tr",
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			mordaLangs := newMordaLangs()
			assert.Equal(t, tt.want, mordaLangs.getDefaultMordaLang(tt.selector))
		})
	}
}
