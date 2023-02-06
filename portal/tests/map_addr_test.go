package tests

import (
	"encoding/json"
	"fmt"
	"net/http"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

type mapAddrResponse struct {
	Formatted string `json:"formatted"`
}

func newMapAddrResponse(r *http.Response) (*mapAddrResponse, error) {
	response := &mapAddrResponse{}
	if err := json.NewDecoder(r.Body).Decode(response); err != nil {
		return nil, err
	}
	return response, nil
}

func (s *Suite) Test_MapAddr_differentLanguages() {
	t := s.T()

	// Координаты БЦ "Морозов"
	latitude := 55.733974
	longitude := 37.587093
	const (
		russianAddress   = "Россия, Москва, улица Льва Толстого, 16"
		englishAddress   = "Russia, Moscow, Lva Tolstogo Street, 16"
		ukrainianAddress = "Росія, Москва, вулиця Льва Толстого, 16"
	)

	type testCase struct {
		name              string
		language          string
		skipLanguage      bool
		expectedFormatted string
	}

	cases := []testCase{
		{
			name:              "Russian",
			language:          "ru",
			expectedFormatted: russianAddress,
		},
		{
			name:              "English",
			language:          "en",
			expectedFormatted: englishAddress,
		},
		{
			name:              "Ukrainian",
			language:          "uk",
			expectedFormatted: ukrainianAddress,
		},
		{
			name:              "Empty locale, fallback to default",
			language:          "",
			expectedFormatted: russianAddress,
		},
		{
			name:              "Incorrect locale, fallback to default",
			language:          "completely_not_a_locale",
			expectedFormatted: russianAddress,
		},
		{
			name:              "no locale, fallback to default",
			skipLanguage:      true,
			expectedFormatted: russianAddress,
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			url := s.GetURL()
			u := url.WithPath("/geohelper/map_addr")
			u.AddCGIArg("lat", fmt.Sprintf("%f", latitude))
			u.AddCGIArg("lon", fmt.Sprintf("%f", longitude))
			if !tt.skipLanguage {
				u.AddCGIArg("lang", tt.language)
			}
			requestURL := u.String()

			t.Logf("MapAddr request URL: %s\n", requestURL)

			httpResponse, err := http.Get(requestURL)
			require.NoError(t, err)
			defer func() {
				err := httpResponse.Body.Close()
				require.NoError(t, err)
			}()

			setraceID := httpResponse.Header.Get("X-Yandex-Req-Id")
			t.Logf("SETrace: https://setrace.yandex-team.ru/ui/search/?reqid=%s\n", setraceID)

			require.Equal(t, http.StatusOK, httpResponse.StatusCode, "check HTTP return code")

			response, err := newMapAddrResponse(httpResponse)
			require.NoError(t, err)

			assert.Equal(t, tt.expectedFormatted, response.Formatted, "check formatted address")
		})
	}
}
