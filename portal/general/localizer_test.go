package topnews

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	gb "a.yandex-team.ru/library/go/yandex/geobase"
	"a.yandex-team.ru/portal/avocado/libs/utils/lang"
	"a.yandex-team.ru/portal/avocado/libs/utils/log3"
	"a.yandex-team.ru/portal/avocado/proto/topnews"
)

type providerStub struct {
	fallbackLocales map[string]string
}

func (p *providerStub) Get(key string, locale string) string {
	return ""
}

func (p *providerStub) GetFallbackLocale(locale string) string {
	return p.fallbackLocales[locale]
}

func (p *providerStub) GetInternalName(locale string) string {
	return ""
}

type geobaseWrapperStub struct {
	translations map[string]string
}

func (g *geobaseWrapperStub) GetCapitalID(id gb.ID) (gb.ID, error) {
	return 0, nil
}

func (g *geobaseWrapperStub) GetParentsIDs(id gb.ID, crimea ...gb.CrimeaStatus) ([]gb.ID, error) {
	return nil, nil
}

func (g *geobaseWrapperStub) GetParentsIDsDef(id gb.ID) ([]gb.ID, error) {
	return nil, nil
}

func (g *geobaseWrapperStub) GetOnlyParentsIDsDef(id gb.ID) ([]gb.ID, error) {
	return nil, nil
}

func (g *geobaseWrapperStub) MakePinpointGeolocation(input gb.GeolocationInput, ypCookie string, ysCookie string) (gb.Geolocation, error) {
	return gb.Geolocation{}, nil
}

func (g *geobaseWrapperStub) GetLinguistics(id gb.ID, lang string) (*gb.Linguistics, error) {
	return &gb.Linguistics{NominativeCase: g.translations[lang]}, nil
}

func (g *geobaseWrapperStub) GetTimezoneByID(id gb.ID) (*gb.Timezone, error) {
	return nil, nil
}

func (g *geobaseWrapperStub) Destroy() {
}

func (g *geobaseWrapperStub) GetRegionByID(id gb.ID) (*gb.Region, error) {
	return nil, nil
}

func TestLocalizeGeo(t *testing.T) {
	provider := &providerStub{
		fallbackLocales: map[string]string{
			"de": "de",
			"nl": "en",
			"ru": "ru",
		},
	}
	geobaseWrapper := &geobaseWrapperStub{
		translations: map[string]string{
			"ru": "Москва",
			"en": "Moscow",
			"de": "Moskau",
		},
	}

	logger := log3.NewLoggerStub()
	madmGeoTitles := []*topnews.TGeoTitles{
		{
			Geo:  1,
			Text: "Москва и область",
		},
	}
	loc := newLocalizer("", "ru", provider, geobaseWrapper, logger, madmGeoTitles)

	testCases := []struct {
		caseName string

		geoID    int
		locale   string
		expected string
	}{
		{
			caseName: "existing russian locale",

			geoID:    213,
			locale:   "ru",
			expected: "Москва",
		},
		{
			caseName: "existing non-russian locale",

			geoID:    213,
			locale:   "de",
			expected: "Moskau",
		},
		{
			caseName: "fallback locale",

			geoID:    213,
			locale:   "nl",
			expected: "Moscow",
		},
		{
			caseName: "existing russian locale, title from madm",

			geoID:    1,
			locale:   "ru",
			expected: "Москва и область",
		},
	}
	for _, testCase := range testCases {
		t.Run(testCase.caseName, func(t *testing.T) {
			loc.locale = testCase.locale
			tab := &tab{
				ID:  testCase.geoID,
				URL: "region",
			}
			err := loc.localizeTab(tab)
			require.NoError(t, err)
			assert.Equal(t, testCase.expected, tab.Name)
		})
	}
}

func TestTopnewsGlobalTabName(t *testing.T) {
	provider := lang.GetResourceLocalizer()
	geobaseWrapper := &geobaseWrapperStub{}

	logger := log3.NewLoggerStub()
	var madmGeoTitles []*topnews.TGeoTitles
	loc := newLocalizer("", "ru", provider, geobaseWrapper, logger, madmGeoTitles)

	tab := newGlobalTab("ru")

	require.NoError(t, loc.localizeTab(tab))

	assert.Equal(t, "Главное", tab.Name)
}
