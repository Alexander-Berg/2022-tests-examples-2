package compare

import (
	"encoding/json"
	"fmt"
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"github.com/valyala/fastjson"

	"a.yandex-team.ru/portal/avocado/libs/utils/lang"
	"a.yandex-team.ru/portal/avocado/libs/utils/madm/v2"
	"a.yandex-team.ru/portal/avocado/libs/utils/unistat"
)

func Test_exportsComparator_compare(t *testing.T) {
	langProvider := lang.GetResourceLocalizer()

	testCases := []struct {
		name            string
		expectedExports map[string]string
		gotExports      map[string]string
		shouldError     bool
	}{
		{
			name: "nothing to compare",
		},
		{
			name: "unknown export",
			expectedExports: map[string]string{
				"doesn't exist": `[{"a": 123}]`,
			},
			shouldError: true,
		},
		{
			name: "known export",
			expectedExports: map[string]string{
				"does exist": `[{"a": 123}]`,
			},
			gotExports: map[string]string{
				"does exist": `[{"a": 123}]`,
			},
		},
		{
			name: "one of known exports",
			expectedExports: map[string]string{
				"does exist": `[{"a": 123}]`,
			},
			gotExports: map[string]string{
				"does exist":      `[{"a": 123}]`,
				"also does exist": `[{"a": 123}]`,
			},
		},
		{
			name: "known export with slight format difference",
			expectedExports: map[string]string{
				"does exist": `[{"a": 123}]`,
			},
			gotExports: map[string]string{
				"does exist": `[{"a": "123"}]`,
			},
		},
		{
			name: "known export with difference",
			expectedExports: map[string]string{
				"does exist": `[{"a": 123}]`,
			},
			gotExports: map[string]string{
				"does exist": `[{"a": 124}]`,
			},
			shouldError: true,
		},
		{
			name: "known export with conversion difference in locale/lang",
			expectedExports: map[string]string{
				"does exist": `[
					{"a": 42, "lang": "ua"},
					{"a": 43, "lang": "kk"},
					{"a": 44, "lang": "be"},
					{"a": 45, "lang": "ru"}
				]`,
			},
			gotExports: map[string]string{
				"does exist": `[
					{"a": 42, "lang": "uk"},
					{"a": 43, "lang": "kz"},
					{"a": 44, "lang": "by"},
					{"a": 45, "lang": "ru"}
				]`,
			},
		},
		{
			name: "known export with real difference in locale/lang",
			expectedExports: map[string]string{
				"does exist": `[
					{"a": 42, "lang": "ua"},
					{"a": 43, "lang": "kk"},
					{"a": 44, "lang": "be"},
					{"a": 45, "lang": "ru"}
				]`,
			},
			gotExports: map[string]string{
				"does exist": `[
					{"a": 42, "lang": "be"},
					{"a": 43, "lang": "ru"},
					{"a": 44, "lang": "by"},
					{"a": 45, "lang": "kz"}
				]`,
			},
			shouldError: true,
		},
	}
	for _, testCase := range testCases {
		t.Run(testCase.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)

			expected := NewMockComparableContextExpected(ctrl)
			expectedExports := make(map[string][]json.RawMessage)
			for name, content := range testCase.expectedExports {
				var parsedContent []json.RawMessage
				require.NoError(t, json.Unmarshal([]byte(content), &parsedContent))
				expectedExports[name] = parsedContent
			}
			expected.EXPECT().GetExports().Return(expectedExports)

			got := NewMockComparableContextGot(ctrl)

			madmDataGetter := NewMockmadmDataGetter(ctrl)
			registeredMatches := make([]gomock.Matcher, 0)
			for name, content := range testCase.gotExports {
				parsed, err := fastjson.ParseBytes([]byte(content))
				require.NoError(t, err)
				require.True(t, parsed.Type() == fastjson.TypeArray)
				array := parsed.GetArray()
				items := make(madm.Items, 0, len(array))
				for _, value := range array {
					items = append(items, madm.NewItem(value))
				}
				exportName := madm.ExportName(name)
				madmDataGetter.EXPECT().StaticData(exportName, gomock.Any(), gomock.Any()).Return(items, nil).AnyTimes()
				registeredMatches = append(registeredMatches, gomock.Eq(exportName))
			}
			madmDataGetter.EXPECT().StaticData(gomock.All(registeredMatches...), gomock.Any(), gomock.Any()).Return(nil, fmt.Errorf("not registered")).AnyTimes()

			comparator := newExportsComparator(unistat.NewRegistry(""), madmDataGetter, langProvider)
			err := comparator.compare(expected, got)
			if testCase.shouldError {
				assert.Error(t, err)
			} else {
				assert.NoError(t, err)
			}
		})
	}
}
