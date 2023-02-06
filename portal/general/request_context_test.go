package newinternal

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestExtractGeohelperRequestPath(t *testing.T) {
	t.Run("is working path", func(t *testing.T) {
		testCases := map[string]string{
			"/geohelper_avocado/get":              "/get",
			"/geohelper/get":                      "/get",
			"/geohelper_avocado/api/v1/searchapp": "/api/v1/searchapp",
			"/geohelper_avocado":                  "/",
		}

		for testCase, testReference := range testCases {
			t.Run(testCase, func(t *testing.T) {
				assert.Equal(t, testReference, extractGeohelperRequestPath(testCase))
			})

		}
	})

	t.Run("is broken path", func(t *testing.T) {
		testCases := map[string]string{
			"/portal":               "",
			"/ololo/":               "",
			"/portal/mobilesearch":  "",
			"/portal/api/yabrowser": "",
		}

		for testCase, testReference := range testCases {
			t.Run(testCase, func(t *testing.T) {
				assert.Equal(t, testReference, extractGeohelperRequestPath(testCase))
			})

		}
	})
}
