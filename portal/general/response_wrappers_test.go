package searchapp

import (
	"io/ioutil"
	"strconv"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"github.com/valyala/fastjson"

	protoanswers "a.yandex-team.ru/apphost/lib/proto_answers"
	apphost_utils "a.yandex-team.ru/portal/avocado/libs/utils/apphost"
	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/libs/utils/errors/v3"
	"a.yandex-team.ru/portal/avocado/libs/utils/lang"
	"a.yandex-team.ru/portal/avocado/libs/utils/log3"
	"a.yandex-team.ru/portal/avocado/morda-go/pkg/exports"
	"a.yandex-team.ru/portal/avocado/proto/topnews"
)

type topnewsBlockWrapper interface {
	createBlockToBeMerged() (*fastjson.Value, error)
	extractDivTemplateNames() []string
	applyPatchTo(apiSearch2Response *apiSearch2ResponseWrapper, data *fastjson.Value)
}

type topnewsWrapper struct {
	*topnewsSubgraphResponseWrapper
}

func (w *topnewsWrapper) createBlockToBeMerged() (*fastjson.Value, error) {
	return w.topnewsSubgraphResponseWrapper.createBlockToBeMerged()
}

func (w *topnewsWrapper) extractDivTemplateNames() []string {
	return extractDivTemplateNames(w.Value, divTemplatesKey)
}

func (w *topnewsWrapper) applyPatchTo(apiSearch2Response *apiSearch2ResponseWrapper, data *fastjson.Value) {
	templates := w.getDivTemplates()
	options := exports.Options{}
	apiSearch2Response.patchTopnews(data, templates, options, w.isHotNews, models.ABFlags{})
}

type bulkBlockWrapper struct {
	*divBulkRendererResponse
}

func (w *bulkBlockWrapper) createBlockToBeMerged() (*fastjson.Value, error) {

	return w.divBulkRendererResponse.createBlockToBeMerged("topnews_extended"), nil
}

func (w *bulkBlockWrapper) extractDivTemplateNames() []string {
	return extractDivTemplateNames(w.JSON, bulkDivTemplatesKey)
}

func (w *bulkBlockWrapper) applyPatchTo(apiSearch2Response *apiSearch2ResponseWrapper, data *fastjson.Value) {
	_ = data
	//Обработка ошибок происходит так же в методе patchTopnews
	if err := apiSearch2Response.patchBulkRenderer(w.divBulkRendererResponse); err != nil {
		apiSearch2Response.logger.Warn(errors.Wrap(err, "cannot patch API response with Topnews block"))
	}
}

func newTopnewsBlockWrapper(blockID string, testdata string, info models.AppInfo) (topnewsBlockWrapper, error) {
	if blockID == topnewsBlockID {
		response, err := newTopnewsResponseStub(testdata, info)
		return &topnewsWrapper{response}, err
	} else {
		response, err := newDivRendererBulkResponseStub(testdata, info)
		return &bulkBlockWrapper{response}, err
	}
}

func newAPIResponseStub(testdata string) (*apiSearch2ResponseWrapper, error) {
	jsonBody, err := ioutil.ReadFile(testdata)
	if err != nil {
		return nil, err
	}
	httpResponse := &protoanswers.THttpResponse{Content: jsonBody}

	appInfo := models.AppInfo{
		Version:  "28000000",
		Platform: "android",
	}
	logger, err := log3.NewLogger(log3.WithCritHandler(nil))
	if err != nil {
		return nil, err
	}
	return newAPISearch2ResponseWrapper(httpResponse, new(fastjson.Parser), new(fastjson.Parser), new(fastjson.Arena), appInfo, logger)
}

func newTopnewsResponseStub(testdata string, info models.AppInfo) (*topnewsSubgraphResponseWrapper, error) {
	jsonBody, err := ioutil.ReadFile(testdata)
	if err != nil {
		return nil, err
	}
	topnewsResponse := &topnews.TResponse{
		Data: jsonBody,
	}

	return newTopnewsSubgraphResponseWrapper(topnewsResponse, "topnews", "ru", new(fastjson.Parser), new(fastjson.Arena), info, exports.TopnewsOptions{}, nil)
}

func newAppInfo(isAndroid bool, isIOS bool, version int) models.AppInfo {
	var platform string
	if isAndroid {
		platform = "android"
	}

	if isIOS {
		platform = "ios"
	}

	return models.AppInfo{
		Platform: platform,
		Version:  strconv.Itoa(version),
	}
}

func newDivRendererBulkResponseStub(testdata string, info models.AppInfo) (*divBulkRendererResponse, error) {
	jsonBody, err := ioutil.ReadFile(testdata)
	if err != nil {
		return nil, err
	}

	json, err := new(fastjson.Parser).ParseBytes(jsonBody)
	if err != nil {
		return nil, err
	}

	return &divBulkRendererResponse{
		JSONValueWrapper:           apphost_utils.JSONValueWrapper{JSON: json},
		arena:                      new(fastjson.Arena),
		sentToBulkRendererBlockIDs: []string{"topnews_extended"},
		provider:                   lang.GetResourceLocalizer(),
		appInfo:                    info,
		patcherMetrics:             nil,
	}, nil
}

type testCase struct {
	topnewsInLayout         bool
	topnewsInZenPlaceholder bool
	topnewsBlock            bool
	appSearchJSONTestData   string
}

type testCaseOption func(c *testCase)

func newTestCase(opts ...testCaseOption) testCase {
	c := testCase{}
	for _, opt := range opts {
		opt(&c)
	}
	return c
}

func withTopnewsInLayout() testCaseOption {
	return func(c *testCase) {
		c.topnewsInLayout = true
	}
}

func withTopnewsInZenPlaceholder() testCaseOption {
	return func(c *testCase) {
		c.topnewsInZenPlaceholder = true
	}
}

func withTopnewsBlock() testCaseOption {
	return func(c *testCase) {
		c.topnewsBlock = true
	}
}

func withAppSearchJSONTestData(testdata string) testCaseOption {
	return func(c *testCase) {
		c.appSearchJSONTestData = testdata
	}
}

const (
	topnewsResponseFileName         = "testdata/topnews_subgraph_response.json"
	divRendererBulkResponseFileName = "testdata/div_renderer_bulk_response.json"
)

func extractDivTemplateNames(value *fastjson.Value, templateKey string) []string {
	if value == nil {
		return nil
	}
	divTemplatesObject := value.GetObject(templateKey)
	if divTemplatesObject == nil {
		return nil
	}
	names := make([]string, 0, divTemplatesObject.Len())
	divTemplatesObject.Visit(func(key []byte, v *fastjson.Value) {
		names = append(names, string(key))
	})
	return names
}

func patchTopnewsBlockID(apiResponse *apiSearch2ResponseWrapper, blockID string) {
	if blockID == topnewsBlockID {
		return
	}
	if layoutItem := apiResponse.getBlockInLayoutArray(topnewsBlockID); layoutItem != nil {
		layoutItem.Set("id", apiResponse.arena.NewString(bulkTopnewsExtendedBlockID))
		apiResponse.getBlockInOfflineLayout(topnewsBlockID).Set("id", apiResponse.arena.NewString(bulkTopnewsExtendedBlockID))
	}
	if zenPlaceholder := apiResponse.getZenExtensionPlaceholder(topnewsBlockID); zenPlaceholder != nil {
		zenPlaceholder.Set("id", apiResponse.arena.NewString(bulkTopnewsExtendedBlockID))
	}
}

func testPatchTopnews(t *testing.T, blockID string, testdata string) {
	testCases := []testCase{
		newTestCase(
			withAppSearchJSONTestData("testdata/api_search_2_response_no_topnews.json"),
		),
		newTestCase(
			withAppSearchJSONTestData("testdata/api_search_2_response_topnews_in_layout.json"),
			withTopnewsInLayout(),
			withTopnewsBlock(),
		),
		newTestCase(
			withAppSearchJSONTestData("testdata/api_search_2_response_topnews_in_layout_and_zen.json"),
			withTopnewsInLayout(),
			withTopnewsInZenPlaceholder(),
			withTopnewsBlock(),
		),
		newTestCase(
			withAppSearchJSONTestData("testdata/api_search_2_response_topnews_in_zen.json"),
			withTopnewsInZenPlaceholder(),
			withTopnewsBlock(),
		),
	}

	for _, testCase := range testCases {
		t.Run(testCase.appSearchJSONTestData, func(t *testing.T) {
			topnewsResponse, err := newTopnewsBlockWrapper(blockID, testdata, newAppInfo(true, false, 28_000_000))
			require.NoError(t, err)
			apiSearch2Response, err := newAPIResponseStub(testCase.appSearchJSONTestData)
			require.NoError(t, err)
			patchTopnewsBlockID(apiSearch2Response, blockID)

			topnewsBlock, err := topnewsResponse.createBlockToBeMerged()
			require.NoError(t, err)
			topnewsResponse.applyPatchTo(apiSearch2Response, topnewsBlock)

			block, _ := apiSearch2Response.getBlock(blockID)
			if testCase.topnewsBlock {
				assert.NotNil(t, block)
			} else {
				assert.Nil(t, block)
			}

			layoutItem := apiSearch2Response.getBlockInLayoutArray(blockID)
			offlineLayoutItem := apiSearch2Response.getBlockInOfflineLayout(blockID)
			if testCase.topnewsInLayout {
				assert.NotNil(t, layoutItem)
				assert.NotNil(t, offlineLayoutItem)
			} else {
				assert.Nil(t, layoutItem)
				assert.Nil(t, offlineLayoutItem)
			}

			zenExtensionItem := apiSearch2Response.getZenExtensionPlaceholder(blockID)
			if testCase.topnewsInZenPlaceholder {
				assert.NotNil(t, zenExtensionItem)
			} else {
				assert.Nil(t, zenExtensionItem)
			}

			apiSearch2DivTemplates := extractDivTemplateNames(apiSearch2Response.Value, divTemplatesKey)
			topnewsDivTemplates := topnewsResponse.extractDivTemplateNames()
			if testCase.topnewsBlock {
				assert.Subset(t, apiSearch2DivTemplates, topnewsDivTemplates)
			} else {
				//assert.NotSubset(t, apiSearch2DivTemplates, topnewsDivTemplates)
				assert.Nil(t, apiSearch2DivTemplates)
			}
		})
	}
}

func testTTV(t *testing.T, blockID string, testdata string) {

	testCases := []struct {
		info        models.AppInfo
		expectedTTV int
		name        string
	}{
		{
			info:        newAppInfo(true, false, 28_000_000),
			expectedTTV: 1209600,
			name:        "Android, version 28'000'000",
		},
		{
			info:        newAppInfo(true, false, 20_000_000),
			expectedTTV: 1200,
			name:        "Android, version 20'000'000",
		},
		{
			info:        newAppInfo(false, true, 28_000_000),
			expectedTTV: 1200,
			name:        "IOS",
		},
	}

	for i := range testCases {
		t.Run(testCases[i].name, func(t *testing.T) {
			response, err := newTopnewsBlockWrapper(blockID, testdata, testCases[i].info)
			assert.NoError(t, err)
			json, err := response.createBlockToBeMerged()
			assert.NoError(t, err)
			assert.Equal(t, testCases[i].expectedTTV, json.GetInt("ttv"))
		})
	}
}

func testLayoutItemType(t *testing.T, blockID string, testdata string) {
	topnewsResponse, err := newTopnewsBlockWrapper(blockID, testdata, newAppInfo(true, false, 28_000_000))
	assert.NoError(t, err)

	apiSearch2Response, err := newAPIResponseStub("testdata/api_search_2_response_topnews_in_layout.json")
	assert.NoError(t, err)
	patchTopnewsBlockID(apiSearch2Response, blockID)

	topnewsBlock, err := topnewsResponse.createBlockToBeMerged()
	assert.NoError(t, err)
	topnewsResponse.applyPatchTo(apiSearch2Response, topnewsBlock)

	layoutItem := apiSearch2Response.getBlockInLayoutArray(blockID)
	assert.Equal(t, "div2", string(layoutItem.GetStringBytes("type")))

	offlineLayoutItem := apiSearch2Response.getBlockInOfflineLayout(blockID)
	assert.Equal(t, "div2", string(offlineLayoutItem.GetStringBytes("type")))
}

func TestPatchTopnews(t *testing.T) {
	testPatchTopnews(t, topnewsBlockID, topnewsResponseFileName)
}

func TestPatchBulkBlock(t *testing.T) {
	testPatchTopnews(t, bulkTopnewsExtendedBlockID, divRendererBulkResponseFileName)
}

func TestPatchHeavyReqPayload(t *testing.T) {
	type layoutItem struct {
		id, typ string
	}

	testCases := []struct {
		testdata           string
		blockID            string
		expectedAfterPatch []layoutItem
	}{
		{
			testdata: "testdata/heavy_req/native_topnews.json",
			blockID:  "topnews",
			expectedAfterPatch: []layoutItem{
				{id: "search", typ: "search"},
				{id: "informers", typ: "div2"},
				{id: "alice_div2", typ: "div2"},
				{id: "topnews", typ: "div2"},
				{id: "stocks", typ: "div2"},
				{id: "native_ad_1", typ: "native_ad"},
				{id: "general_div2", typ: "div2"},
				{id: "native_ad_2", typ: "native_ad"},
				{id: "weather", typ: "weather"},
				{id: "tv", typ: "tv"},
				{id: "autoru_div2", typ: "div2"},
				{id: "privacy_api", typ: "div2"},
			},
		},
		{
			testdata: "testdata/heavy_req/no_topnews.json",
			blockID:  "topnews",
			expectedAfterPatch: []layoutItem{
				{id: "search", typ: "search"},
				{id: "alice_div2", typ: "div2"},
				{id: "stocks", typ: "div2"},
				{id: "native_ad_1", typ: "native_ad"},
				{id: "news_div2", typ: "div2"},
				{id: "general_div2", typ: "div2"},
				{id: "native_ad_2", typ: "native_ad"},
				{id: "weather", typ: "weather"},
				{id: "tv", typ: "tv"},
				{id: "autoru_div2", typ: "div2"},
				{id: "privacy_api", typ: "div2"},
			},
		},
	}

	for _, testCase := range testCases {
		t.Run(testCase.testdata, func(t *testing.T) {
			apiSearch2Response, err := newAPIResponseStub(testCase.testdata)
			require.NoError(t, err)

			extractLayout := func() ([]layoutItem, error) {
				parsedPayload, err := fastjson.ParseBytes(apiSearch2Response.GetStringBytes("heavy_req", "payload"))
				if err != nil {
					return nil, err
				}
				layout := parsedPayload.GetArray("homeparams", "layout")
				result := make([]layoutItem, 0, len(layout))
				for _, item := range layout {
					result = append(result, layoutItem{
						id:  string(item.GetStringBytes("id")),
						typ: string(item.GetStringBytes("type")),
					})
				}
				return result, nil
			}

			err = apiSearch2Response.patchHeavyReqPayload(testCase.blockID)
			require.NoError(t, err)

			// Получаем содержимое payload'а после патча.
			layout, err := extractLayout()
			require.NoError(t, err)

			assert.Equal(t, testCase.expectedAfterPatch, layout)
		})
	}
}

func TestTopnewsLayoutItemType(t *testing.T) {
	testLayoutItemType(t, topnewsBlockID, topnewsResponseFileName)
}

func TestTopnewsExtendedLayoutItemType(t *testing.T) {
	testLayoutItemType(t, bulkTopnewsExtendedBlockID, divRendererBulkResponseFileName)
}

func TestTopnewsTTV(t *testing.T) {
	testTTV(t, topnewsBlockID, topnewsResponseFileName)
}

func TestTopnewsExtendedTTV(t *testing.T) {
	testTTV(t, bulkTopnewsExtendedBlockID, divRendererBulkResponseFileName)
}
