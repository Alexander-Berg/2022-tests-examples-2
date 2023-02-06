package common

import (
	"net/http"
	"net/url"
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/libs/utils/staticparams"
)

func TestHTTPRequestWrapper_isInternal(t *testing.T) {
	testCases := []struct {
		headers  map[string]string
		expected bool
		caseName string
	}{
		{
			headers: map[string]string{
				"X-Yandex-Internal-Request": "1",
			},
			expected: true,
			caseName: "regular_case",
		},
		{
			headers: map[string]string{
				"X-YANDEX-INTERNAL-REQUEST": "1",
			},
			expected: true,
			caseName: "upper_case",
		},
		{
			headers: map[string]string{
				"X-NOT-YANDEX-INTERNAL-REQUEST": "1",
			},
			expected: false,
			caseName: "upper_case",
		},
		{
			headers:  nil,
			expected: false,
			caseName: "no_headers",
		},
		{
			headers: map[string]string{
				"X-Yandex-Internal-Request": "yes",
			},
			expected: false,
			caseName: "incorrect_value",
		},
	}
	for _, testCase := range testCases {
		t.Run(testCase.caseName, func(t *testing.T) {
			headers := http.Header{}
			for k, v := range testCase.headers {
				headers.Add(k, v)
			}
			ctrl := gomock.NewController(t)
			originRequestMock := NewMockoriginRequestKeeper(ctrl)
			originRequestMock.EXPECT().GetOriginRequest().Return(&models.OriginRequest{Headers: headers}, nil).AnyTimes()

			wrapper := NewHTTPRequestWrapper(originRequestMock, url.Values{})
			require.NotNil(t, wrapper)
			assert.Equal(t, testCase.expected, wrapper.IsInternalRequest())
		})
	}
}

func TestHTTPRequestWrapper_getUSaaSHeaderFromTHttpRequest(t *testing.T) {
	type answer struct {
		flags string
		boxes string
	}
	testCases := []struct {
		headers  map[string]string
		location staticparams.Location
		expected answer
		caseName string
	}{
		{
			headers: map[string]string{
				"X-Yandex-ExpFlags":     "AAA",
				"X-Yandex-ExpBoxes":     "BBB",
				"X-Yandex-ExpFlags-Pre": "CCC",
				"X-Yandex-ExpBoxes-Pre": "DDD",
			},
			location: "vla",
			expected: answer{
				flags: "CCC",
				boxes: "DDD",
			},
			caseName: "prestable headers in VLA",
		},
		{
			headers: map[string]string{
				"X-Yandex-ExpFlags":     "AAA",
				"X-Yandex-ExpBoxes":     "BBB",
				"X-Yandex-ExpFlags-Pre": "CCC",
				"X-Yandex-ExpBoxes-Pre": "DDD",
			},
			location: "sas",
			expected: answer{
				flags: "AAA",
				boxes: "BBB",
			},
			caseName: "stable headers not in VLA",
		},
		{
			headers: map[string]string{
				"X-Yandex-ExpFlags":     "AAA",
				"X-Yandex-ExpBoxes":     "BBB",
				"X-Yandex-ExpFlags-Pre": "CCC",
				"X-Yandex-ExpBoxes-Pre": "DDD",
			},
			location: "",
			expected: answer{
				flags: "AAA",
				boxes: "BBB",
			},
			caseName: "stable headers by default",
		},
		{
			headers: map[string]string{
				"X-Yandex-ExpFlags-Pre": "CCC",
				"X-Yandex-ExpBoxes-Pre": "DDD",
			},
			location: "vla",
			expected: answer{
				flags: "CCC",
				boxes: "DDD",
			},
			caseName: "only prestable, VLA location",
		},
		{
			headers: map[string]string{
				"X-Yandex-ExpFlags-Pre": "CCC",
				"X-Yandex-ExpBoxes-Pre": "DDD",
			},
			location: "sas",
			expected: answer{
				flags: "",
				boxes: "",
			},
			caseName: "only prestable, not VLA location",
		},
		{
			headers: map[string]string{
				"X-Yandex-ExpFlags": "AAA",
				"X-Yandex-ExpBoxes": "BBB",
			},
			location: "",
			expected: answer{
				flags: "AAA",
				boxes: "BBB",
			},
			caseName: "only stable",
		},
		{
			headers: map[string]string{
				"X-Yandex-ExpFlags": "AAA",
				"X-Yandex-ExpBoxes": "BBB",
			},
			location: "vla",
			expected: answer{
				flags: "AAA",
				boxes: "BBB",
			},
			caseName: "only stable in VLA",
		},
		{
			headers: map[string]string{
				"x-yandex-expflags":     "AAA",
				"x-yandex-expboxes":     "BBB",
				"x-yandex-expflags-pre": "CCC",
				"x-yandex-expBoxes-pre": "DDD",
			},
			location: "vla",
			expected: answer{
				flags: "CCC",
				boxes: "DDD",
			},
			caseName: "lower_case in VLA",
		},
		{
			headers: map[string]string{
				"X-Yandex-ExpFlags":     "AAA",
				"X-Yandex-ExpBoxes":     "BBB",
				"X-Yandex-ExpFlags-Pre": "",
				"X-Yandex-ExpBoxes-Pre": "",
			},
			location: "vla",
			expected: answer{
				flags: "AAA",
				boxes: "BBB",
			},
			caseName: "empty_prestable_headers in VLA",
		},
	}
	for _, testCase := range testCases {
		t.Run(testCase.caseName, func(t *testing.T) {
			headers := http.Header{}
			for k, v := range testCase.headers {
				headers.Add(k, v)
			}
			ctrl := gomock.NewController(t)
			originRequestMock := NewMockoriginRequestKeeper(ctrl)
			originRequestMock.EXPECT().GetOriginRequest().Return(&models.OriginRequest{Headers: headers}, nil).AnyTimes()

			wrapper := NewHTTPRequestWrapper(originRequestMock, url.Values{})
			require.NotNil(t, wrapper)
			assert.Equal(t, testCase.expected.flags, wrapper.GetExpFlags(testCase.location))
			assert.Equal(t, testCase.expected.boxes, wrapper.GetExpBoxes(testCase.location))
		})
	}
}
