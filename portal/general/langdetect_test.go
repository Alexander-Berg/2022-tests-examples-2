package langdetect

// Тесты переписаны на Go из следующих источников:
// https://svn.yandex.ru/websvn/wsvn/lang-detect/trunk/library/tests/lookup_test.cpp
// https://svn.yandex.ru/websvn/wsvn/lang-detect/trunk/library/python/test.py (частично или полностью пересекаются с предыдущими)

import (
	"fmt"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/test/yatest"
)

var dataPath = yatest.SourcePath("portal/avocado/libs/utils/langdetect/data/lang_detect_data.txt")

type fields struct {
	geo, language, domain string
	cookie                int
	filter                []string
	def                   string
}

func newLookup(t testing.TB) Lookup {
	lookup, err := NewLookup(dataPath)
	if err == ErrNotSupported {
		t.Skip("CGO_ENABLED=0 build is ok")
	}

	require.NoError(t, err)
	return lookup
}

func TestFilepath(t *testing.T) {
	lookup := newLookup(t)
	defer lookup.Destroy()

	path, err := lookup.Filepath()
	require.NoError(t, err)
	require.Equal(t, dataPath, path)
}

func TestList(t *testing.T) {
	lookup := newLookup(t)
	defer lookup.Destroy()

	type testCase struct {
		name    string
		fields  fields
		want    []LangInfo
		wantErr bool
	}

	tests := []testCase{
		{
			name: "test_list_unfiltered",
			fields: fields{
				language: "fr;q=0.8, en;q=0.7, HE",
				domain:   "yandex.com.tr",
			},
			want: []LangInfo{
				{Code: "tr", Name: "Tr"},
				{Code: "en", Name: "En"},
				{Code: "fr", Name: "Fr"},
				{Code: "he", Name: "Il"},
			},
		},
		{
			name: "test_find_tt_filtered_1",
			fields: fields{
				domain:   "yandex.ru",
				filter:   []string{"ru", "uk", "kk"},
				language: "be",
				cookie:   4,
			},
			want: []LangInfo{
				{Code: "ru"},
				{Code: "kk"},
			},
		},
		{
			name: "test_find_tt_filtered_2",
			fields: fields{
				domain:   "yandex.ru",
				filter:   []string{"ru", "uk", "kk"},
				language: "be",
				cookie:   5,
			},
			want: []LangInfo{
				{Code: "ru"},
			},
		},
		{
			name: "test_find_tr_filtered_1",
			fields: fields{
				filter:   []string{"ru", "tr", "uk", "kk", "en"},
				domain:   "yandex.com.tr",
				language: "be",
				cookie:   4,
				geo:      "24896,20529,20524,187,166,10001,10000", // Борислав
			},
			want: []LangInfo{
				{Code: "tr"},
				{Code: "en"},
				{Code: "kk"},
				{Code: "ru"},
				{Code: "uk"},
			},
		},
		{
			name: "test_find_tr_filtered_2",
			fields: fields{
				filter:   []string{"ru", "tr", "uk", "kk", "en"},
				domain:   "yandex.com.tr",
				language: "be",
				cookie:   5,
				geo:      "24896,20529,20524,187,166,10001,10000", // Борислав
			},
			want: []LangInfo{
				{Code: "tr"},
				{Code: "en"},
				{Code: "ru"},
				{Code: "uk"},
			},
		},
		{
			name: "check_en_in_yandex_team_ru_for_tr",
			fields: fields{
				filter:   []string{"ru", "en"},
				domain:   "yandex-team.ru",
				language: "tr",
				def:      "en",
			},
			want: []LangInfo{
				{Code: "ru"},
				{Code: "en"},
			},
		},
		{
			name: "check_ru_in_yandex_team_ru_for_tr",
			fields: fields{
				filter:   []string{"ru"},
				domain:   "yandex-team.ru",
				language: "tr",
				def:      "en",
			},
			want: []LangInfo{
				{Code: "ru"},
			},
		},
		{
			name: "check_ru_in_yandex_team_ru_for_uk",
			fields: fields{
				filter:   []string{"ru", "en"},
				domain:   "yandex-team.ru",
				language: "uk",
				def:      "ru",
			},
			want: []LangInfo{
				{Code: "ru"},
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			list, err := lookup.List(tt.fields.geo, tt.fields.language, tt.fields.domain, tt.fields.cookie, tt.fields.filter, tt.fields.def)

			if tt.wantErr {
				require.Error(t, err)
			} else {
				require.NoError(t, err)

				require.Equal(t, len(tt.want), len(list))

				for i, li := range list {
					require.NotEmpty(t, li.Name)
					require.NotEmpty(t, li.Code)
					require.NotEmpty(t, li.CookieValue)

					if tt.want[i].Name != "" {
						require.Equal(t, tt.want[i].Name, li.Name)
					}
					if tt.want[i].Code != "" {
						require.Equal(t, tt.want[i].Code, li.Code)
					}
					if tt.want[i].CookieValue != 0 {
						require.Equal(t, tt.want[i].CookieValue, li.CookieValue)
					}
				}
			}
		})
	}
}

func TestFind(t *testing.T) {
	lookup := newLookup(t)
	defer lookup.Destroy()

	type testCase struct {
		name    string
		fields  fields
		want    LangInfo
		wantErr bool
	}

	tests := []testCase{
		{
			name: "testDOCENGINE608",
			fields: fields{
				domain: "www.yandex.ru",
				filter: []string{"ru", "en"},
				def:    "en",
			},
			want: LangInfo{
				Code: "ru",
			},
		},
		{
			name: "testLIB672",
			fields: fields{
				domain:   "www.yandex.uz",
				filter:   []string{"en", "uz", "ru"},
				language: "uz,ru;q=0.8",
				def:      "ru",
			},
			want: LangInfo{
				Code: "uz",
			},
		},
		{
			name: "testLIB161_FindWithLocale_1",
			fields: fields{
				domain:   "www.yandex.com",
				filter:   []string{"zh", "en", "pt-br"},
				language: "zh,en;q=0.8",
				def:      "zh",
			},
			want: LangInfo{
				Code: "zh",
			},
		},
		{
			name: "testLIB161_FindWithLocale_2",
			fields: fields{
				domain:   "www.yandex.com",
				filter:   []string{"zh-Hant", "en", "pt-br"},
				language: "zh-Hant,en;q=0.8",
				def:      "zh-Hant",
			},
			want: LangInfo{
				Code: "en", // zh-Hant в оригинале
			},
		},
		{
			name: "testLIB161_FindWithLocale_3",
			fields: fields{
				domain:   "www.yandex.com",
				filter:   []string{"fi", "ru"},
				language: "fi,en;q=0.8",
				def:      "en",
			},
			want: LangInfo{
				Code: "fi",
			},
		},
		{
			name: "testFindLang_FRinFR",
			fields: fields{
				domain: "www.yandex.fr",
				filter: []string{"fr"},
				geo:    "109140,152771,152753,104381,124,111,10001,10000",
			},
			want: LangInfo{
				Code: "fr",
			},
		},
		{
			name: "testFindLang_FRinCOM",
			fields: fields{
				domain:   "www.yandex.com",
				filter:   []string{"fr", "en"},
				language: "fr,en;q=0.8",
			},
			want: LangInfo{
				Code: "fr",
			},
		},
		{
			name: "testFindLangLocale_FRinCOM",
			fields: fields{
				domain:   "www.yandex.com",
				filter:   []string{"fr-FR", "fr", "en"},
				language: "fr-FR,fr;q=0.8,en-US;q=0.6,en;q=0.4",
			},
			want: LangInfo{
				Code: "fr", // fr-FR в оригинале
			},
		},
		{
			name: "testLIB723_FindLang_RUinGE",
			fields: fields{
				domain:   "yandex.com.ge",
				filter:   []string{"ru", "en"},
				language: "ru,en;q=0.8",
			},
			want: LangInfo{
				Code: "ru",
			},
		},
		{
			name: "testLIB723_FindLang_RUinGE_2",
			fields: fields{
				domain:   "yandex.com.ge",
				filter:   []string{"ru", "en"},
				language: "uk",
				def:      "ru",
			},
			want: LangInfo{
				Code: "ru",
			},
		},
		{
			name: "testLIB698_FindLangLocale_RUinGE1",
			fields: fields{
				domain:   "yandex.com.ge",
				filter:   []string{"ru", "en"},
				language: "ru,en-US;q=0.8",
				def:      "ru",
				geo:      "213, 1, 3, 225, 10001, 10000",
			},
			want: LangInfo{
				Code: "ru",
			},
		},
		{
			name: "testLIB698_FindLangLocale_RUinGE2",
			fields: fields{
				domain:   "yandex.com.ge",
				filter:   []string{"ru", "en-US"},
				language: "ru-RU,en-US;q=0.8",
				def:      "ru",
				geo:      "213, 1, 3, 225, 10001, 10000",
			},
			want: LangInfo{
				Code: "ru",
			},
		},
		{
			name: "testLIB698_FindLangLocale_RUinGE3",
			fields: fields{
				domain:   "yandex.com.ge",
				filter:   []string{"ru-RU", "en-US"},
				language: "ru-RU,en-US;q=0.8",
			},
			want: LangInfo{
				Code: "ru", // ru-RU в оригинале
			},
		},
		{
			name: "testLIB723_FindLangViaRegion_ENinGE",
			fields: fields{
				domain:   "yandex.com.ge",
				geo:      "51,120861,11131,40,225,10001,10000", // Самара
				filter:   []string{"ru", "en"},
				language: "en,en-UK;q=0.8",
				def:      "en",
			},
			want: LangInfo{
				Code: "en",
			},
		},
		{
			name: "testLIB723_FindLangWoRegion_ENinGE",
			fields: fields{
				domain:   "yandex.com.ge",
				filter:   []string{"ru", "en"},
				language: "en,en-UK;q=0.8",
				def:      "en",
			},
			want: LangInfo{
				Code: "en",
			},
		},
		{
			name: "testLIB788_FindLangLocale_FRinCOM",
			fields: fields{
				domain:   "mapseditor.yandex.com",
				filter:   []string{"en", "FR", "hy"},
				language: "fr-fr",
				def:      "en",
			},
			want: LangInfo{
				Code: "fr",
			},
		},
		{
			name: "testFindLangLocale_WithComplexAcceptLang1",
			fields: fields{
				domain:   "mapseditor.yandex.com",
				filter:   []string{"En", "FR", "hY"},
				language: "ru-RU,en-US;q=0.8",
				def:      "ar",
			},
			want: LangInfo{
				Code: "en",
			},
		},
		{
			name: "testFindLang_just_quick",
			fields: fields{
				domain:   "avia-frontend.mangin.avia.dev.yandex.com",
				filter:   []string{"en", "de"},
				language: "de-li",
				def:      "ru",
				geo:      "9999,213,1,3,225,10001,10000",
			},
			want: LangInfo{
				Code: "de",
			},
		},
		{
			name: "testFindLang_Lt_nonEN",
			fields: fields{
				domain:   "www.yandex.lt",
				filter:   []string{"en", "ru", "lt"},
				language: "kk,uk,lt,pl;q=0.5",
				def:      "en",
				geo:      "11475, 104260, 117, 111, 10001, 10000",
			},
			want: LangInfo{
				Code: "lt",
			},
		},
		{
			name: "testFindDefDomain_1",
			fields: fields{
				language: "ru-ru, ru-ua, uk",
			},
			wantErr: true,
		},
		{
			name: "testFindDefDomain_2",
			fields: fields{
				domain:   "yandex.com",
				language: "kk, uk",
			},
			want: LangInfo{
				Code: "en",
				Name: "En",
			},
		},
		{
			name: "testFindDefDomain_3",
			fields: fields{
				domain:   "yandex.ru",
				language: "kk, uk",
			},
			want: LangInfo{
				Code: "ru",
				Name: "Ru",
			},
		},
		{
			name: "testFindRuUpper",
			fields: fields{
				language: "RU-ru,uk;q=0.5",
			},
			want: LangInfo{
				Code: "ru", // RU-ru в оригинале
				Name: "Ru",
			},
		},
		{
			name: "testFindTT_1",
			fields: fields{
				language: "tt",
			},
			want: LangInfo{
				Code: "tt",
				Name: "Tat",
			},
		},
		{
			name: "testFindTT_2",
			fields: fields{
				language: "be, uk-ua, uk",
			},
			wantErr: true,
		},
		{
			name: "testFindTT_4",
			fields: fields{
				cookie: 4,
			},
			want: LangInfo{
				Code: "kk",
				Name: "Kz",
			},
		},
	}

	// batches

	for _, tld := range []string{"lv", "lt", "ee", "com.ge", "pl", "fi"} {
		tests = append(tests, testCase{
			name: fmt.Sprintf("testFindLang_euro5_EN__tld=%s", tld),
			fields: fields{
				domain:   "www.yandex." + tld,
				filter:   []string{"en", "ru", "by"},
				language: "kk,uk,pl;q=0.9",
				def:      "en",
			},
			want: LangInfo{
				Code: "en",
			},
		})
	}

	for _, tld := range []string{"eu", "pl", "fi"} {
		cases := []struct {
			lang, want string
		}{
			{lang: getUserLangs("pl", "ru", "en"), want: "pl"},
			{lang: getUserLangs("en", "ru", "pl"), want: "en"},
			{lang: getUserLangs("ru", "pl", "en"), want: "ru"},
			{lang: getUserLangs("en", "ru", ""), want: "en"},
		}
		for _, c := range cases {
			for _, deflang := range []string{"pl", "ru", "en"} {
				tests = append(tests, testCase{
					name: fmt.Sprintf("test_FindLangsInEU__tld=%s;lang=%s;default=%s", tld, c.lang, deflang),
					fields: fields{
						domain:   "www.yandex." + tld,
						filter:   []string{"ru", "pl", "en"},
						language: c.lang,
						def:      deflang,
					},
					want: LangInfo{
						Code: c.want,
					},
				})
			}
		}
	}

	tldAndLocals := []struct{ tld, local string }{
		{tld: "ee", local: "et"},
		{tld: "lt", local: "lt"},
		{tld: "lv", local: "lv"},
	}
	for _, tldAndLocal := range tldAndLocals {
		tld, local := tldAndLocal.tld, tldAndLocal.local
		cases := []struct {
			lang, want string
		}{
			{lang: getUserLangs(local, "ru", "en"), want: local},
			{lang: getUserLangs(local, "en", "ru"), want: local},
			{lang: getUserLangs("ru", "en", local), want: "ru"},
			{lang: getUserLangs("ru", local, "en"), want: "ru"},
			{lang: getUserLangs("en", "ru", local), want: "en"},
			{lang: getUserLangs("en", local, "ru"), want: "en"},
			{lang: getUserLangs("en", "ru", ""), want: "en"},
		}
		for _, c := range cases {
			for _, deflang := range []string{"ru", "en", local} {
				tests = append(tests, testCase{
					name: fmt.Sprintf("testLIB946_BalticLangs__tld=%s;localLang=%s;lang=%s;default=%s",
						tld, local, c.lang, deflang),
					fields: fields{
						domain:   "www.yandex." + tld,
						filter:   []string{"ru", "en", local},
						language: c.lang,
						def:      deflang,
					},
					want: LangInfo{
						Code: c.want,
					},
				})
			}
		}
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			li, err := lookup.Find(tt.fields.geo, tt.fields.language, tt.fields.domain, tt.fields.cookie, tt.fields.filter, tt.fields.def)

			if tt.wantErr {
				require.Error(t, err)
			} else {
				require.NoError(t, err)

				require.NotEmpty(t, li.Name)
				require.NotEmpty(t, li.Code)
				require.NotEmpty(t, li.CookieValue)

				if tt.want.Name != "" {
					require.Equal(t, tt.want.Name, li.Name)
				}
				if tt.want.Code != "" {
					require.Equal(t, tt.want.Code, li.Code)
				}
				if tt.want.CookieValue != 0 {
					require.Equal(t, tt.want.CookieValue, li.CookieValue)
				}
			}
		})
	}
}

func getUserLangs(l1, l2, l3 string) string {
	if l3 == "" {
		return fmt.Sprintf("%s,%s;q=0.9", l1, l2)
	}
	return fmt.Sprintf("%s,%s;q=0.8;%s=0.6", l1, l2, l3)
}
