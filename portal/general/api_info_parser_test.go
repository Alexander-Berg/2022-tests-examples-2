package requests

import (
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
)

func Test_apiInfoParser_parse(t *testing.T) {
	testCases := []struct {
		name string
		path string
		want models.APIInfo
	}{
		{
			name: "empty path",
		},
		{
			name: "usual api search 2",
			path: "/portal/api/search/2",
			want: models.APIInfo{
				Name:    "search",
				Version: 2,
			},
		},
		{
			name: "usual api search 2 with trailing slash",
			path: "/portal/api/search/2/",
			want: models.APIInfo{
				Name:    "search",
				Version: 2,
			},
		},
		{
			name: "no api version",
			path: "/no/version/api/name",
			want: models.APIInfo{
				Name: "name",
			},
		},
		{
			name: "no api version, trailing slash",
			path: "/no/version/api/name/",
			want: models.APIInfo{
				Name: "name",
			},
		},
		{
			name: "no api version, no api name",
			path: "/no/version/no/name/api",
			want: models.APIInfo{},
		},
		{
			name: "no api version, no api name, trailing slash",
			path: "/no/version/no/name/api/",
			want: models.APIInfo{},
		},
		{
			name: "remapped api",
			path: "/portal/api/yabrowser/2",
			want: models.APIInfo{
				Name:        "search",
				Version:     2,
				RealName:    "yabrowser",
				RealVersion: 2,
			},
		},
	}
	for _, tt := range testCases {
		t.Run(tt.name, func(t *testing.T) {
			if tt.want.RealName == "" {
				tt.want.RealName = tt.want.Name
			}
			if tt.want.RealVersion == 0 {
				tt.want.RealVersion = tt.want.Version
			}

			parser := NewAPIInfoParser()

			got := parser.Parse(tt.path)
			assert.Equal(t, tt.want, got)
		})
	}
}

func Test_apiInfoParser_stripCGI(t *testing.T) {
	tests := []struct {
		name      string
		urlString string
		want      string
	}{
		{
			name:      "no cgi",
			urlString: "yandex.ru/1/2/3/",
			want:      "yandex.ru/1/2/3/",
		},
		{
			name:      "with cgi",
			urlString: "yandex.ru/1/2/3/?test=1",
			want:      "yandex.ru/1/2/3/",
		},
		{
			name:      "several separators",
			urlString: "yandex.ru/1/2/3/?test=1&city=moscow?fruit=apple",
			want:      "yandex.ru/1/2/3/",
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			parser := &apiInfoParser{}
			got := parser.stripCGI(tt.urlString)
			assert.Equal(t, tt.want, got)
		})
	}
}
