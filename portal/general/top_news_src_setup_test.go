package topnews

import (
	"net/url"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/portal/avocado/libs/utils/log3"
)

func TestFillFromURL(t *testing.T) {
	testCases := []struct {
		url      string
		expected limitersRestrictions
		caseName string
	}{
		{
			url: "",
			expected: limitersRestrictions{
				disableAVTopnews: false,
				disableGBTopnews: false,
			},
			caseName: "empty string",
		},
		{
			url: "/?disable_av_topnews=abc",
			expected: limitersRestrictions{
				disableAVTopnews: false,
				disableGBTopnews: false,
			},
			caseName: "unacceptable value=abc",
		},
		{
			url: "/?disable_av_topnews=2",
			expected: limitersRestrictions{
				disableAVTopnews: false,
				disableGBTopnews: false,
			},
			caseName: "unacceptable value=2",
		},
		{
			url: "/?disable_av_topnews=1",
			expected: limitersRestrictions{
				disableAVTopnews: true,
				disableGBTopnews: false,
			},
			caseName: "disable_av_topnews is enabled",
		},
		{
			url: "/?disable_gb_topnews=1",
			expected: limitersRestrictions{
				disableAVTopnews: false,
				disableGBTopnews: true,
			},
			caseName: "disable_gb_topnews is enabled",
		},
		{
			url: "/?disable_av_topnews=1&disable_gb_topnews=1",
			expected: limitersRestrictions{
				disableAVTopnews: true,
				disableGBTopnews: true,
			},
			caseName: "disable_av_topnews and disable_gb_topnews is enabled",
		},
	}

	for _, testCase := range testCases {
		limitersRestrictions := &limitersRestrictions{}
		t.Run(testCase.caseName, func(t *testing.T) {
			parsed, err := url.Parse(testCase.url)
			require.NoError(t, err)
			limitersRestrictions.fillFromCGI(parsed.Query(), log3.NewLoggerStub())
			assert.Equal(t, testCase.expected, *limitersRestrictions)
		})
	}
}

func TestNewLimitersRestrictions(t *testing.T) {
	testCases := []struct {
		url          string
		expected     limitersRestrictions
		isProduction bool
		caseName     string
	}{
		{
			url: "/",
			expected: limitersRestrictions{
				disableAVTopnews: false,
				disableGBTopnews: false,
			},
			isProduction: true,
			caseName:     "no args and production env",
		},
		{
			url: "/",
			expected: limitersRestrictions{
				disableAVTopnews: false,
				disableGBTopnews: false,
			},
			isProduction: false,
			caseName:     "no args and not production env",
		},
		{
			url: "/?disable_av_topnews=1",
			expected: limitersRestrictions{
				disableAVTopnews: true,
				disableGBTopnews: false,
			},
			isProduction: false,
			caseName:     "disable_av_topnews=1 and not production env",
		},
		{
			url: "/?disable_gb_topnews=1",
			expected: limitersRestrictions{
				disableAVTopnews: false,
				disableGBTopnews: true,
			},
			isProduction: false,
			caseName:     "disable_gb_topnews=1 and not production env",
		},
		{
			url: "/?disable_av_topnews=1&disable_gb_topnews=1",
			expected: limitersRestrictions{
				disableAVTopnews: true,
				disableGBTopnews: true,
			},
			isProduction: false,
			caseName:     "disable_av_topnews=1 and disable_gb_topnews=1 and not production env",
		},
	}

	for _, testCase := range testCases {
		t.Run(testCase.caseName, func(t *testing.T) {
			parsed, err := url.Parse(testCase.url)
			require.NoError(t, err)
			caseLimitersRestrictions := newLimitersRestrictions(parsed.Query(), testCase.isProduction, log3.NewLoggerStub())
			assert.Equal(t, testCase.expected, *caseLimitersRestrictions)
		})
	}
}
