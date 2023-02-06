package searchapp

import (
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

const (
	topnewsExtendedBlockID = "topnews_extended"
)

func (suite *SearchAppSuite) Test_TopNewsExtendedStraightScheme() {
	t := suite.T()

	testCases := []topnewsExtendedTestCase{
		{
			name:                         "Russia_Moscow",
			lang:                         "ru-RU",
			geoid:                        213,
			domain:                       "ru",
			expectedRegionAlias:          "moscow",
			needToCheckLocale:            true,
			isZenFeedAvailable:           true,
			isTopnewsExtended:            false,
			isTopnewsExtendedFromAvocado: false,
		},
		{
			name:                         "Russia_Moscow",
			lang:                         "ru-RU",
			geoid:                        213,
			domain:                       "ru",
			expectedRegionAlias:          "moscow",
			needToCheckLocale:            true,
			isZenFeedAvailable:           true,
			isTopnewsExtended:            true,
			isTopnewsExtendedFromAvocado: false,
		},
		{
			name:                         "Russia_Moscow",
			lang:                         "ru-RU",
			geoid:                        213,
			domain:                       "ru",
			expectedRegionAlias:          "moscow",
			needToCheckLocale:            true,
			isZenFeedAvailable:           true,
			isTopnewsExtended:            false,
			isTopnewsExtendedFromAvocado: true,
		},
		{
			name:                         "Russia_Moscow",
			lang:                         "ru-RU",
			geoid:                        213,
			domain:                       "ru",
			expectedRegionAlias:          "moscow",
			needToCheckLocale:            true,
			isZenFeedAvailable:           true,
			isTopnewsExtended:            true,
			isTopnewsExtendedFromAvocado: true,
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
			zenArgs := []bool{false}
			if testCase.isZenFeedAvailable {
				zenArgs = []bool{false, true}
			}
			for _, isZenActivated := range zenArgs {
				t.Run(fmt.Sprintf("%s_%s_%s", testCase.name, minVersion.platform, minVersion.version), func(t *testing.T) {
					u, err := testCase.buildSearchAppURL(suite.GetURL(), minVersion.platform, minVersion.version, isZenActivated,
						testCase.isTopnewsExtended, testCase.isTopnewsExtendedFromAvocado)
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

					require.Equal(t, http.StatusOK, httpResponse.StatusCode, "check HTTP return code")

					// buf := new(bytes.Buffer)
					// buf.ReadFrom(httpResponse.Body)
					// s := buf.String()
					// spew.Println(s)
					response, err := newSearchAppResponse(httpResponse)
					require.NoError(t, err)

					topnewsBlock, err := response.getTopnewsExtendedBlock()
					require.NotNil(t, topnewsBlock)
					require.NoError(t, err)
					require.Equal(t, div2BlockType, topnewsBlock.Type, "check Topnews Extended card type in blocks")

					layoutItem, err := response.getTopnewsExtendedLayoutItem()
					require.NotNil(t, layoutItem)
					require.NoError(t, err)
					assert.Equal(t, div2BlockType, layoutItem.Type, "check Topnews Extended card type in layout")

					// offline_item отдаётся только Андроиду
					if minVersion.platform == "android" {
						offlineItem, err := response.getTopnewsExtendedOfflineLayoutItem()
						require.NotNil(t, offlineItem, "check Topnews Extended layout item in offline_layout")
						require.NoError(t, err)
						assert.Equal(t, div2BlockType, offlineItem.Type, "check Topnews Extended card type in offline_layout")
					}

					data, err := topnewsBlock.extractTopnewsExtendedData()
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

					// Если включена лента Дзена, то проверяем наличие блока Новостей в списке плейсхолдеров
					if isZenActivated {
						placeholderItem := response.getTopnewsExtendedZenPlaceholder()
						require.NotNil(t, placeholderItem, "no Zen placeholder item for Topnews Extended block")
						switch minVersion.platform {
						case "android":
							assert.Equal(t, "topnews_extended", placeholderItem.ID, "check Topnews Extended card ID in Zen placeholder")
							assert.Equal(t, div2BlockType, placeholderItem.Type, "check Topnews Extended card type in Zen placeholder")
						case "iphone":
							assert.Equal(t, "topnews_extended", placeholderItem.Block.ID, "check Topnews Extended card ID in block in Zen placeholder")
							assert.Equal(t, div2BlockType, placeholderItem.Block.Type, "check Topnews Extended card type in block in Zen placeholder")
						}
					}
				})
			}
		}
	}

}

type topnewsExtendedTestCase struct {
	name string

	lang   string
	geoid  int
	domain string

	// Ожидаемый алиас региона, присутствующий в ссылке на таб региональных новостей вида yandex.TLD/news/region/alias.
	expectedRegionAlias string
	// В некоторых тестах геопозиция явно не указывается, она определяется в Морде по некоторым данным (в частности, по хэдерам LaaS).
	needToCheckAlias bool

	// В некоторых тестах язык интерфейса может отличаться от запрашиваемого.
	expectedLocale string
	// Ряд тестов использует локаль, в которой заведомо нет перевода. Для них срабатывает фолбэк в другую локаль,
	// которую не нужно проверять
	needToCheckLocale bool

	// Доступна ли лента Дзена в данном регионе. Если да, то нужно проверять ответ портальной ручки
	// как с выключенной, так и с включённой лентой
	isZenFeedAvailable bool

	// Включена ли сводная карточка
	isTopnewsExtended bool

	// Обрабатываем ли сводную карточку в Avocado
	isTopnewsExtendedFromAvocado bool

	// Ходим в прямую схему
	//is
}

func (c *topnewsExtendedTestCase) getExpectedLocale() string {
	if c.expectedLocale != "" {
		return c.expectedLocale
	}
	items := strings.SplitN(c.lang, "-", 2)
	return items[0]
}

func (c *topnewsExtendedTestCase) buildSearchAppURL(mordaURL tests.URL, appPlatform string, appVersion string, zenFeedEnabled bool, topnewsExtended bool, topnewsExtendedFromAvocado bool) (string, error) {
	u := mordaURL.WithTLD(c.domain).WithPath("/portal/api/search/2")

	u.AddCGIArg("app_platform", appPlatform)
	u.AddCGIArg("app_version", appVersion)

	if c.geoid != 0 {
		u.AddCGIArg("geo", strconv.Itoa(c.geoid))
	}
	u.AddCGIArg("lang", c.lang)
	u.AddCGIArg("ab_flags", "true_avocado=1:topnews_extended_from_avocado=1:topnews_extended=1")

	switch appPlatform {
	case "android":
		u.AddCGIArg("app_id", "ru.yandex.searchplugin")
	case "iphone":
		u.AddCGIArg("app_id", "ru.yandex.mobile")
	}

	if zenFeedEnabled {
		u.AddCGIArg("zen_extensions", "true")
	}

	// Нужно, чтобы Новости точно ответили
	u.AddCGIArg("srcrwr", "TOP_NEWS:::10s")

	u.AddCGIArg("afisha_version", "3")
	u.AddCGIArg("api_key", "45de325a-08de-435d-bcc3-1ebf6e0ae41b")
	u.AddCGIArg("app_build_number", "210804042")
	u.AddCGIArg("app_version_name", "21.84")
	u.AddCGIArg("book_reader", "1")
	u.AddCGIArg("bropp", "1")
	u.AddCGIArg("bs_promo", "1")
	u.AddCGIArg("cellid", "310%2C260%2C91%2C3%2C0")
	u.AddCGIArg("country_init", "ru")
	u.AddCGIArg("dialog_onboarding_shows_count", "1")
	u.AddCGIArg("did", "12d6e30339da1c8f8870a36450fc5578")
	u.AddCGIArg("div_bs", "1")
	u.AddCGIArg("div_profile", "0")
	u.AddCGIArg("divkit_version", "2.3")
	u.AddCGIArg("dp", "3.5")
	u.AddCGIArg("gaid", "191cf921-0fc3-4c6e-976b-c874fb35eff9")
	u.AddCGIArg("geoblock_lite", "0")
	u.AddCGIArg("informersCard", "2")
	u.AddCGIArg("installed_launchers", "-1")
	u.AddCGIArg("locationPermission", "true")
	u.AddCGIArg("manufacturer", "unknown")
	u.AddCGIArg("model", "Android+SDK+built+for+x86")
	u.AddCGIArg("morda_ng", "1")
	u.AddCGIArg("nav_board_promo", "1")
	u.AddCGIArg("navigation_2021", "0")
	u.AddCGIArg("new_nav_panel", "1")
	u.AddCGIArg("os_version", "11")
	u.AddCGIArg("poiy", "1800")
	u.AddCGIArg("search_tab_lister", "local-template_morda")
	u.AddCGIArg("size", "1440%2C2000")
	u.AddCGIArg("uuid", "d72ed5a57d774c72944bd446e8b146c4&yuid=6480250211633506191")
	u.AddCGIArg("zen_pages", "1")

	return u.String(), nil
}

func (resp *SearchAppResponse) getTopnewsExtendedBlock() (*SearchAppResponseBlock, error) {
	for i, block := range resp.Blocks {
		if block.ID == topnewsExtendedBlockID {
			return &resp.Blocks[i], nil
		}
	}
	return nil, xerrors.New("no Topnews Extended block in the response")
}

func (resp *SearchAppResponse) findTopnewsExtendedLayoutItem(items []LayoutItem) *LayoutItem {
	for i, item := range items {
		if item.ID == topnewsExtendedBlockID {
			return &items[i]
		}
	}
	return nil
}

func (resp *SearchAppResponse) getTopnewsExtendedLayoutItem() (*LayoutItem, error) {
	if item := resp.findTopnewsExtendedLayoutItem(resp.Layout); item != nil {
		return item, nil
	}
	return nil, xerrors.New("no Topnews Extended layout item in the response")
}

func (resp *SearchAppResponse) getTopnewsExtendedOfflineLayoutItem() (*LayoutItem, error) {
	if item := resp.findTopnewsExtendedLayoutItem(resp.OfflineLayout); item != nil {
		return item, nil
	}
	return nil, xerrors.New("no Topnews Extended offline layout item in the response")
}

func (resp *SearchAppResponse) getTopnewsExtendedZenPlaceholder() *ZenExtension {
	for i, item := range resp.ZenExtensions {
		for _, zenID := range []string{topnewsExtendedBlockID, "zen_topnews_vertical", "zen_topnews_vertical_hot"} {
			if item.ZenID == zenID {
				return &resp.ZenExtensions[i]
			}
		}
	}
	return nil
}

type topnewsExtendedData struct {
	regionAlias string
	tabsTitles  []topnewsTab
}

func (data *topnewsExtendedData) getTabsTitles() []string {
	titles := make([]string, len(data.tabsTitles))
	for i, item := range data.tabsTitles {
		titles[i] = item.title
	}
	return titles
}

func (block *SearchAppResponseBlock) extractTopnewsExtendedData() (*topnewsExtendedData, error) {
	data := &topnewsExtendedData{}

	parsedJSON, err := fastjson.ParseBytes(block.Data)
	if err != nil {
		return nil, err
	}

	newsTabs := parsedJSON.GetArray("states", "0", "div", "items", "0", "items", "1", "tabs")
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
