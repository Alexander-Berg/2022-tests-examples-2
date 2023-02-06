package searchapp

import (
	"encoding/json"
	"fmt"
	"net/http"
	"strconv"
	"strings"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"github.com/valyala/fastjson"

	"a.yandex-team.ru/library/go/core/xerrors"
	"a.yandex-team.ru/portal/avocado/tests"
)

/*

Прямая схема

https://morda-go-pr-1933046.hometest.yandex.ru/portal/api/search/2?app_version=29000000&app_platform=android&app_id=ru.yandex.searchplugin
	&test-id=359286&ab_flags=topnews_from_avocado=0 -> для срабатывания прямой схемы

ВХОД: GET-запрос
ВЫХОД: JSON-нина с телом


*/

const (
	div2BlockType   = "div2"
	nativeBlockType = "topnews"
	topnewsBlockID  = "topnews"
)

type topnewsMode int

const (
	div2FromTopnews topnewsMode = iota
	div2FromGreenbox
	nativeFromPerlFallback
)

func (suite *SearchAppSuite) Test_TopNewsStraightScheme() {
	t := suite.T()

	testCases := []topnewsTestCase{
		{
			name:                "Russia_Moscow",
			lang:                "ru-RU",
			geoid:               213,
			expectedRegionAlias: "moscow",
			needToCheckLocale:   true,
		},
		{
			name:                "Ukraine_Kyiv",
			lang:                "ru-UA",
			geoid:               143,
			expectedRegionAlias: "",
			needToCheckLocale:   true,
		},
		{
			name:              "Belarus_Minsk",
			lang:              "be-BY",
			geoid:             157,
			needToCheckLocale: true,
		},
		{
			name:              "Kazakhstan_NurSultan",
			lang:              "kk-KZ",
			geoid:             163,
			needToCheckLocale: true,
		},
		{
			name:              "Uzbekistan_Tashkent",
			lang:              "uz-UZ",
			geoid:             10335,
			needToCheckLocale: true,
		},
		{
			// Новости Украины для русской локали
			name:                "Ukraine_Kyiv_InRussian",
			lang:                "ru-UA",
			geoid:               143,
			expectedRegionAlias: "",
			needToCheckLocale:   true,
		},
		{
			// Новости конкретного региона для Санкт-Петербурга в России
			name:                "Russia_SaintPetersburg",
			lang:                "ru-RU",
			geoid:               2,
			expectedRegionAlias: "Saint_Petersburg",
			needToCheckLocale:   true,
		},
		{
			//  Новости конкретного региона для Харькова в Украине
			name:                "Ukraine_Kharkiv",
			lang:                "ru-UA",
			geoid:               147,
			expectedRegionAlias: "",
			needToCheckLocale:   true,
		},
		{
			// Попытка получить новости региона для Гомеля в Беларуси, но там нет отдельного таба.
			name:              "Belarus_Gomel",
			lang:              "ru-BY",
			geoid:             155,
			needToCheckLocale: true,
			needToCheckAlias:  true,
		},
		{
			// Запрос из экзотического региона, где нет отдельных Яндекс.Новостей
			name:                "Italy_Rome",
			lang:                "ru-IT",
			geoid:               10445,
			expectedRegionAlias: "italy",
			needToCheckLocale:   true,
		},
		{
			// Запрос из региона, где Яндекс почти не популярен. Оттуда часто стреляют боты.
			name:              "Indonesia_Jakarta",
			lang:              "en-ID",
			geoid:             10574,
			expectedLocale:    "ru",
			needToCheckLocale: true,
		},
		// Запросы из ПП с экзотическими локалями, для которых нет переводов регионального таба.
		{
			name:                "German language in SearchApp",
			lang:                "de-DE",
			geoid:               213,
			expectedRegionAlias: "moscow",
			needToCheckLocale:   false,
		},
		{
			name:                "Uzbek language in SearchApp",
			lang:                "uz-UZ",
			geoid:               213,
			expectedRegionAlias: "moscow",
			needToCheckLocale:   false,
		},
		{
			name:                "French language in SearchApp",
			lang:                "fr-FR",
			geoid:               213,
			expectedRegionAlias: "moscow",
			needToCheckLocale:   false,
		},
		{
			name:                "Czech language in SearchApp",
			lang:                "cs-CZ",
			geoid:               213,
			expectedRegionAlias: "moscow",
			needToCheckLocale:   false,
		},
		{
			name:                "Dutch language in SearchApp",
			lang:                "nl-NL",
			geoid:               213,
			expectedRegionAlias: "moscow",
			needToCheckLocale:   false,
		},
	}

	minSearchAppVersions := []struct {
		platform string
		version  string
	}{
		{"android", "21050000"},
		{"iphone", "63000000"},
	}

	for _, minVersion := range minSearchAppVersions {
		for _, testCase := range testCases {
			for _, isZenActivated := range []bool{false, true} {
				disabledStraightScheme := []bool{false}
				if testCase.needToCheckDisabledStraightScheme {
					disabledStraightScheme = []bool{false, true}
				}
				for _, isStraightSchemeDisabled := range disabledStraightScheme {
					for _, mode := range []topnewsMode{div2FromTopnews, div2FromGreenbox, nativeFromPerlFallback} {
						testCaseName := fmt.Sprintf("%s_%s_%s", testCase.name, minVersion.platform, minVersion.version)

						if isZenActivated {
							testCaseName += "_ZenFeed"
						}
						switch mode {
						case div2FromGreenbox:
							testCaseName += "_ForceGreenbox"
						case nativeFromPerlFallback:
							testCaseName += "_FallbackFromPerl"
						}
						t.Run(testCaseName, func(t *testing.T) {
							u, err := testCase.buildSearchAppURL(suite.GetURL(), minVersion.platform, minVersion.version, isZenActivated, mode, isStraightSchemeDisabled)
							require.NoError(t, err)

							t.Logf("SearchApp URL: %s\n", u)

							httpResponse, err := http.Get(u)
							require.NoError(t, err)
							defer func() {
								err := httpResponse.Body.Close()
								require.NoError(t, err)
							}()

							setraceID := httpResponse.Header.Get("X-Yandex-Req-Id")
							t.Logf("SETrace: https://setrace.yandex-team.ru/ui/search/?reqid=%s\n", setraceID)

							if isStraightSchemeDisabled {
								topnewsSideSchemeSetraceID := httpResponse.Header.Get("X-Topnews-Side-Req-Id")
								assert.NotEmpty(t, topnewsSideSchemeSetraceID, "check request ID from Topnews side scheme")
							}

							require.Equal(t, http.StatusOK, httpResponse.StatusCode, "check HTTP return code")

							response, err := newSearchAppResponse(httpResponse)
							require.NoError(t, err)

							var expectedBlockType string
							switch mode {
							case div2FromGreenbox, div2FromTopnews:
								expectedBlockType = div2BlockType
							case nativeFromPerlFallback:
								expectedBlockType = nativeBlockType
							}

							topnewsBlock, err := response.getTopnewsBlock()
							require.NotNil(t, topnewsBlock)
							require.NoError(t, err)
							require.Equal(t, expectedBlockType, topnewsBlock.Type, "check Topnews card type in blocks")

							layoutItem, err := response.getTopnewsLayoutItem()
							require.NotNil(t, layoutItem)
							require.NoError(t, err)
							assert.Equal(t, expectedBlockType, layoutItem.Type, "check Topnews card type in layout")

							// offline_item отдаётся только Андроиду
							if minVersion.platform == "android" {
								offlineItem, err := response.getTopnewsOfflineLayoutItem()
								require.NotNil(t, offlineItem, "check Topnews layout item in offline_layout")
								require.NoError(t, err)
								assert.Equal(t, expectedBlockType, offlineItem.Type, "check Topnews card type in offline_layout")
							}

							if expectedBlockType == div2BlockType {
								data, err := topnewsBlock.extractTopnewsData()
								require.NoError(t, err)
								require.NotEmpty(t, data.tabsTitles)

								// Проверяем локаль.
								if testCase.needToCheckLocale {
									expectedIndexTab := indexTabTranslations[testCase.getExpectedLocale()]
									assert.Contains(t, data.getTabsTitles(), expectedIndexTab)
								}

								// Проверяем наличие/отсутствие регионального таба и его корректность.
								if testCase.expectedRegionAlias != "" || testCase.needToCheckAlias {
									assert.Equal(t, strings.ToLower(testCase.expectedRegionAlias), strings.ToLower(data.regionAlias))
								}
							}

							// Если включена лента Дзена, то проверяем наличие блока Новостей в списке плейсхолдеров
							if isZenActivated {
								placeholderItem := response.getTopnewsZenPlaceholder()
								require.NotNil(t, placeholderItem, "no Zen placeholder item for Topnews block")
								switch minVersion.platform {
								case "android":
									assert.Equal(t, "topnews", placeholderItem.ID, "check Topnews card ID in Zen placeholder")
									assert.Equal(t, expectedBlockType, placeholderItem.Type, "check Topnews card type in Zen placeholder")
								case "iphone":
									assert.Equal(t, "topnews", placeholderItem.Block.ID, "check Topnews card ID in block in Zen placeholder")
									assert.Equal(t, expectedBlockType, placeholderItem.Block.Type, "check Topnews card type in block in Zen placeholder")
								}
							}
						})
					}
				}
			}
		}
	}

}

var (
	indexTabTranslations = map[string]string{
		"ru": "Главное",
		"be": "Галоўнае",
		"uk": "Головне",
		"kk": "Басты",
		"uz": "Asosiy",
	}
)

type topnewsTestCase struct {
	name string

	lang  string
	geoid int

	// Ожидаемый алиас региона, присутствующий в ссылке на таб региональных новостей вида yandex.TLD/news/region/alias.
	expectedRegionAlias string
	// В некоторых тестах геопозиция явно не указывается, она определяется в Морде по некоторым данным (в частности, по хэдерам LaaS).
	needToCheckAlias bool

	// В некоторых тестах язык интерфейса может отличаться от запрашиваемого.
	expectedLocale string
	// Ряд тестов используют локаль, в котором заведомо нет перевода. Для них срабатывает фолбэк в другую локаль,
	// которую не нужно проверять
	needToCheckLocale bool

	// Нужно ли сделать проверку с явно выключенной прямой схемой. В этом случае структура ответа меняться не должна,
	// а в хэдерах должен приехать айдишник запроса в боковую схему.
	needToCheckDisabledStraightScheme bool
}

func (c *topnewsTestCase) getExpectedLocale() string {
	if c.expectedLocale != "" {
		return c.expectedLocale
	}
	items := strings.SplitN(c.lang, "-", 2)
	return items[0]
}

func (c *topnewsTestCase) buildSearchAppURL(mordaURL tests.URL, appPlatform string, appVersion string, zenFeedEnabled bool, mode topnewsMode, disableStraightScheme bool) (string, error) {
	u := mordaURL.WithPath("/portal/api/search/2")

	u.AddCGIArg("app_platform", appPlatform)
	u.AddCGIArg("app_version", appVersion)

	if c.geoid != 0 {
		u.AddCGIArg("geo", strconv.Itoa(c.geoid))
	}
	u.AddCGIArg("lang", c.lang)
	if disableStraightScheme {
		u.AddCGIArg("ab_flags", "true_avocado=0:topnews_extended=0")
	} else {
		u.AddCGIArg("ab_flags", "true_avocado=1:topnews_extended=0")
	}

	switch appPlatform {
	case "android":
		u.AddCGIArg("app_id", "ru.yandex.searchplugin")
	case "iphone":
		u.AddCGIArg("app_id", "ru.yandex.mobile")
	}

	if zenFeedEnabled {
		u.AddCGIArg("zen_extensions", "true")
	}

	switch mode {
	case div2FromTopnews:
		u.AddCGIArg("srcrwr", "TOP_NEWS:::10s")
	case div2FromGreenbox:
		u.AddCGIArg("srcskip", "TOP_NEWS")
	case nativeFromPerlFallback:
		u.AddCGIArg("srcskip", "TOPNEWS_SUBGRAPH")
	}

	return u.String(), nil
}

type SearchAppResponse struct {
	Blocks         []SearchAppResponseBlock `json:"block"`
	Layout         []LayoutItem             `json:"layout"`
	OfflineLayout  []LayoutItem             `json:"offline_layout"`
	ExtensionBlock `json:"extension_block"`
}

func newSearchAppResponse(r *http.Response) (*SearchAppResponse, error) {
	response := &SearchAppResponse{}
	if err := json.NewDecoder(r.Body).Decode(response); err != nil {
		return nil, err
	}
	return response, nil
}

func (resp *SearchAppResponse) getTopnewsBlock() (*SearchAppResponseBlock, error) {
	for i, block := range resp.Blocks {
		if block.ID == topnewsBlockID {
			return &resp.Blocks[i], nil
		}
	}
	return nil, xerrors.New("no Topnews block in the response")
}

func (resp *SearchAppResponse) findTopnewsLayoutItem(items []LayoutItem) *LayoutItem {
	for i, item := range items {
		if item.ID == topnewsBlockID {
			return &items[i]
		}
	}
	return nil
}

func (resp *SearchAppResponse) getTopnewsLayoutItem() (*LayoutItem, error) {
	if item := resp.findTopnewsLayoutItem(resp.Layout); item != nil {
		return item, nil
	}
	return nil, xerrors.New("no Topnews layout item in the response")
}

func (resp *SearchAppResponse) getTopnewsOfflineLayoutItem() (*LayoutItem, error) {
	if item := resp.findTopnewsLayoutItem(resp.OfflineLayout); item != nil {
		return item, nil
	}
	return nil, xerrors.New("no Topnews offline layout item in the response")
}

func (resp *SearchAppResponse) getTopnewsZenPlaceholder() *ZenExtension {
	for i, item := range resp.ZenExtensions {
		for _, zenID := range []string{topnewsBlockID, "zen_topnews_vertical", "zen_topnews_vertical_hot"} {
			if item.ZenID == zenID {
				return &resp.ZenExtensions[i]
			}
		}
	}
	return nil
}

type topnewsTab struct {
	title string
	// Количество новостей.
	newsCount int
	// Есть ли кнопка "Показать ещё".
	hasHiddenNews bool
}

type topnewsData struct {
	regionAlias string
	tabsTitles  []topnewsTab
}

func (data *topnewsData) getTabsTitles() []string {
	titles := make([]string, len(data.tabsTitles))
	for i, item := range data.tabsTitles {
		titles[i] = item.title
	}
	return titles
}

type SearchAppResponseBlock struct {
	Type  string          `json:"type"`
	Topic string          `json:"topic"`
	ID    string          `json:"id"`
	Data  json.RawMessage `json:"data"`
}

type LayoutItem struct {
	HeavyFlag int    `json:"heavy"`
	ID        string `json:"id"`
	Type      string `json:"type"`
}

type ZenExtension struct {
	HeavyFlag int                    `json:"heavy"`
	ID        string                 `json:"id"`
	Type      string                 `json:"type"`
	ZenID     string                 `json:"zen_id"`
	Position  int                    `json:"position"`
	Block     SearchAppResponseBlock `json:"block"`
}

type ExtensionBlock struct {
	ZenExtensions []ZenExtension `json:"zen_extensions"`
}

func (block *SearchAppResponseBlock) extractTopnewsData() (*topnewsData, error) {
	data := &topnewsData{}

	parsedJSON, err := fastjson.ParseBytes(block.Data)
	if err != nil {
		return nil, err
	}

	newsTabs := parsedJSON.GetArray("states", "0", "div", "items", "1", "items")
	data.tabsTitles = make([]topnewsTab, len(newsTabs))

	for i, newsTab := range newsTabs {
		data.tabsTitles[i].title = string(newsTab.GetStringBytes("title"))
		for _, item := range newsTab.GetArray("div", "items", "0", "items") {
			itemType := string(item.GetStringBytes("type"))
			if strings.HasPrefix(itemType, "newsTopTabItem/") {
				data.tabsTitles[i].newsCount++
			}

			if string(item.GetStringBytes("div_id")) == "hidden_stories_0" {
				data.tabsTitles[i].hasHiddenNews = true
			}
		}
		tabURL := string(newsTab.GetStringBytes("title_click_action", "url"))
		if strings.Contains(tabURL, "region") {
			items := strings.Split(tabURL, "/")
			data.regionAlias = items[len(items)-1]
		}
	}

	return data, nil
}
