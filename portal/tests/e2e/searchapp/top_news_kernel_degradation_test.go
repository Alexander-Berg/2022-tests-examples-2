package searchapp

import (
	"bytes"
	"encoding/json"
	"io"
	"net/http"
	"net/url"
	"testing"

	"github.com/stretchr/testify/require"
	"github.com/valyala/fastjson"
)

type kernelDegradation struct {
	greenboxDisable bool
	topnewsDisable  bool
}

func (suite *SearchAppSuite) Test_KernelDegradation() {
	t := suite.T()

	commonQueryParams := url.Values{
		"lang":             {"ru-RU"},
		"country_init":     {"ru"},
		"app_platform":     {"android"},
		"app_version":      {"21060301"},
		"app_version_name": {"21.63"},
		"app_build_number": {"210603012"},
		"os_version":       {"8.1.0"},
		"ab_flags":         {"true_avocado:topnews_extended=0"},
	}

	testCases := []struct {
		caseName string
		url      url.URL
		expected kernelDegradation
	}{
		{
			caseName: "disabled traffic limiters",
			url: url.URL{
				Path: "/portal/api/search/2",
				RawQuery: commonQueryParams.Encode() + "&" + url.Values{
					"srcrwr":             {"TOP_NEWS:::5s"},
					"json_dump_requests": {":type"},
					"concat_json_dump":   {"html_comment"},
				}.Encode(),
			},
			expected: kernelDegradation{
				greenboxDisable: false,
				topnewsDisable:  false,
			},
		},
		{
			caseName: "disabled greenbox request",
			url: url.URL{
				Path: "/portal/api/search/2",
				RawQuery: commonQueryParams.Encode() + "&" + url.Values{
					"srcrwr":             {"TOP_NEWS:::5s"},
					"json_dump_requests": {":type"},
					"concat_json_dump":   {"html_comment"},
					"disable_gb_topnews": {"1"},
				}.Encode(),
			},
			expected: kernelDegradation{
				greenboxDisable: true,
				topnewsDisable:  false,
			},
		},
		{
			caseName: "disabled topnews request",
			url: url.URL{
				Path: "/portal/api/search/2",
				RawQuery: commonQueryParams.Encode() + "&" + url.Values{
					"srcrwr":             {"TOP_NEWS:::5s"},
					"json_dump_requests": {":type"},
					"concat_json_dump":   {"html_comment"},
					"disable_av_topnews": {"1"},
				}.Encode(),
			},
			expected: kernelDegradation{
				greenboxDisable: false,
				topnewsDisable:  true,
			},
		},
		{
			caseName: "disabled greenbox and topnews requests",
			url: url.URL{
				Path: "/portal/api/search/2",
				RawQuery: commonQueryParams.Encode() + "&" + url.Values{
					"srcrwr":             {"TOP_NEWS:::5s"},
					"json_dump_requests": {":type"},
					"concat_json_dump":   {"html_comment"},
					"disable_gb_topnews": {"1"},
					"disable_av_topnews": {"1"},
				}.Encode(),
			},
			expected: kernelDegradation{
				greenboxDisable: true,
				topnewsDisable:  true,
			},
		},
	}

	for _, testCase := range testCases {
		topnewsURL := suite.GetURL()
		topnewsURL.SetPath(testCase.url.Path)
		parsedURLQuery, _ := url.ParseQuery(testCase.url.RawQuery)
		topnewsURL.SetCgiArgs(parsedURLQuery)
		t.Run(testCase.caseName, func(t *testing.T) {
			httpResponse, err := http.Post(topnewsURL.String(), "application/json", bytes.NewBufferString("{}"))
			require.NoError(t, err)

			if setraceID := httpResponse.Header.Get("X-Yandex-Req-Id"); setraceID != "" {
				t.Logf("SETrace: https://setrace.yandex-team.ru/ui/search/?reqid=%s\n", setraceID)
			}
			t.Logf("URL=%s\n", topnewsURL.String())
			defer func() {
				err := httpResponse.Body.Close()
				require.NoError(t, err)
			}()

			body, err := io.ReadAll(httpResponse.Body)
			require.NoError(t, err)

			dumpStartSeparator := []byte("<!-- //json_dump_frame=")
			dumpEndSeparator := []byte(" -->")
			cutIndex := bytes.Index(body, dumpStartSeparator)
			require.NotEqual(
				t,
				-1,
				cutIndex,
			)

			cleanMordaResp := body[:cutIndex]
			response := &SearchAppResponse{}
			err = json.Unmarshal(cleanMordaResp, &response)
			require.NoError(t, err)

			_, err = response.getTopnewsBlock()
			require.NoError(t, err)

			topNewsDumpResp := body[cutIndex+len(dumpStartSeparator) : len(body)-len(dumpEndSeparator)]
			parser := fastjson.Parser{}
			value, err := parser.ParseBytes(topNewsDumpResp)
			require.NoError(t, err)

			require.NotEqual(
				t,
				testCase.expected.topnewsDisable,
				value.Exists("TOPNEWS_SUBGRAPH", "TOP_NEWS_POSTPROCESS"),
			)

			require.NotEqual(
				t,
				testCase.expected.greenboxDisable,
				value.Exists("TOPNEWS_SUBGRAPH", "GREENBOX"),
			)
		})
	}
}
