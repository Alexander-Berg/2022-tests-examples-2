package urlbuilder

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func Test_UpdateQuery(t *testing.T) {
	tests := []struct {
		name   string
		uri    string
		params map[string]string
		want   string
	}{
		{
			name: "replace app_version and add os",
			uri:  "https://yandex.ru/portal/api/search/2?app_platform=android&&app_version=2&page=abc&combo=s&page=def#u_4",
			params: map[string]string{
				"app_version": "4",
				"os":          "Linux",
			},
			want: "https://yandex.ru/portal/api/search/2?app_platform=android&app_version=4&combo=s&os=Linux&page=abc&page=def#u_4",
		},
		{
			name: "add appsearch_header",
			uri:  "https://yandex.ru/portal/api/search/2?from=multimorda&fix&app_id=ru.yandex.searchplugin&app_platform=android&app_version=9000500&did=441fca749cc11653fcee8bf3ed935477&uuid=a0ff0ef93281469f9e077d9de7617a4e",
			params: map[string]string{
				"appsearch_header": "1",
			},
			want: "https://yandex.ru/portal/api/search/2?app_id=ru.yandex.searchplugin&app_platform=android&app_version=9000500&appsearch_header=1&did=441fca749cc11653fcee8bf3ed935477&fix=&from=multimorda&uuid=a0ff0ef93281469f9e077d9de7617a4e",
		},
		{
			name: "add params",
			uri:  "ya.ru",
			params: map[string]string{
				"1": "2",
			},
			want: "ya.ru?1=2",
		},
		{
			name: "add params with slash",
			uri:  "ya.ru/",
			params: map[string]string{
				"1": "2",
			},
			want: "ya.ru/?1=2",
		},
		{
			name: "add params with question mark",
			uri:  "ya.ru/?",
			params: map[string]string{
				"1": "2",
			},
			want: "ya.ru/?1=2",
		},
		{
			name: "add params with question mark and amp",
			uri:  "ya.ru/?&",
			params: map[string]string{
				"1": "2",
			},
			want: "ya.ru/?1=2",
		},
		{
			name:   "without params",
			uri:    "ya.ru",
			params: nil,
			want:   "ya.ru",
		},
		{
			name:   "without params with slash",
			uri:    "ya.ru/",
			params: nil,
			want:   "ya.ru/",
		},
		{
			name:   "without params with hash mark",
			uri:    "ya.ru/#",
			params: nil,
			want:   "ya.ru/",
		},
		{
			name:   "without params with hash",
			uri:    "ya.ru/#a",
			params: nil,
			want:   "ya.ru/#a",
		},
		{
			name:   "without params with question mark",
			uri:    "ya.ru/?",
			params: nil,
			want:   "ya.ru/?",
		},
		{
			name:   "without params with query",
			uri:    "ya.ru/?1",
			params: nil,
			want:   "ya.ru/?1=",
		},
		{
			name:   "without params with question mark and amp",
			uri:    "ya.ru/?&",
			params: nil,
			want:   "ya.ru/",
		},
		{
			name:   "without params with query params",
			uri:    "ya.ru/?3=4",
			params: nil,
			want:   "ya.ru/?3=4",
		},
		{
			name:   "without params with full query",
			uri:    "ya.ru/?3=4#a",
			params: nil,
			want:   "ya.ru/?3=4#a",
		},
		{
			name: "add params to uri",
			uri:  "ya.ru/1=42",
			params: map[string]string{
				"1": "2",
			},
			want: "ya.ru/1=42?1=2",
		},
		{
			name: "add params to uri",
			uri:  "ya.ru/?3=4",
			params: map[string]string{
				"1": "2",
			},
			want: "ya.ru/?1=2&3=4",
		},
		{
			name: "add params to uri",
			uri:  "ya.ru/?3=4&5",
			params: map[string]string{
				"1": "2",
			},
			want: "ya.ru/?1=2&3=4&5=",
		},
		{
			name: "add params to uri with hash",
			uri:  "ya.ru/?3=4#1=3",
			params: map[string]string{
				"1": "2",
			},
			want: "ya.ru/?1=2&3=4#1=3",
		},
		{
			name: "replace query param",
			uri:  "ya.ru/?1=45",
			params: map[string]string{
				"1": "2",
			},
			want: "ya.ru/?1=2",
		},
		{
			name: "add query param value",
			uri:  "ya.ru/?1",
			params: map[string]string{
				"1": "2",
			},
			want: "ya.ru/?1=2",
		},
		{
			name: "add query param value to query",
			uri:  "ya.ru/?1&3=4",
			params: map[string]string{
				"1": "2",
			},
			want: "ya.ru/?1=2&3=4",
		},
		{
			name: "change query param when many",
			uri:  "ya.ru/?1=45&1=56&1=78",
			params: map[string]string{
				"1": "2",
			},
			want: "ya.ru/?1=2",
		},
		{
			name: "add to strange uri",
			uri:  "ya.ru/?1=45&&2=3&1=56",
			params: map[string]string{
				"1": "2",
			},
			want: "ya.ru/?1=2&2=3",
		},
		{
			name: "add to strange uri",
			uri:  "ya.ru/?1=45&&2=3&1=56",
			params: map[string]string{
				"1": "2",
			},
			want: "ya.ru/?1=2&2=3",
		},
		{
			name: "change only key=1",
			uri:  "ya.ru/?1=10&1-1=20&1-1-1=30",
			params: map[string]string{
				"1": "500",
			},
			want: "ya.ru/?1=500&1-1=20&1-1-1=30",
		},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			res, err := UpdateQuery(test.uri, test.params)

			require.NoError(t, err)
			assert.Equal(t, test.want, res)
		})
	}
}

func Test_GlueParams(t *testing.T) {
	tests := []struct {
		name   string
		uri    string
		params map[string][]string
		want   string
	}{
		{
			name:   "don't add anything",
			uri:    "https://maps.yandex.ru",
			params: nil,
			want:   "https://maps.yandex.ru",
		},
		{
			name:   "don't add anything but slash",
			uri:    "https://maps.yandex.ru/",
			params: nil,
			want:   "https://maps.yandex.ru/",
		},
		{
			name:   "don't add anything but question mark",
			uri:    "https://maps.yandex.ru/?",
			params: nil,
			want:   "https://maps.yandex.ru/?",
		},
		{
			name: "add params",
			uri:  "https://maps.yandex.ru",
			params: map[string][]string{
				"test": {"1"},
			},
			want: "https://maps.yandex.ru?test=1",
		},
		{
			name: "add params only key",
			uri:  "https://maps.yandex.ru",
			params: map[string][]string{
				"test": nil,
			},
			want: "https://maps.yandex.ru?test=",
		},
		{
			name: "add params only key with question mark",
			uri:  "https://maps.yandex.ru",
			params: map[string][]string{
				"?test": {""},
			},
			want: "https://maps.yandex.ru?test=",
		},
		{
			name: "add params only key with amp",
			uri:  "https://maps.yandex.ru",
			params: map[string][]string{
				"&test": nil,
			},
			want: "https://maps.yandex.ru?test=",
		},

		{
			name: "add params with question mark in key",
			uri:  "https://maps.yandex.ru",
			params: map[string][]string{
				"?test": {"1"},
			},
			want: "https://maps.yandex.ru?test=1",
		},
		{
			name: "add params with amp in key",
			uri:  "https://maps.yandex.ru",
			params: map[string][]string{
				"&test": {"1"},
			},
			want: "https://maps.yandex.ru?test=1",
		},
		{
			name: "add some params ",
			uri:  "https://maps.yandex.ru",
			params: map[string][]string{
				"test1": {"1"},
				"test2": {"2"},
			},
			want: "https://maps.yandex.ru?test1=1&test2=2",
		},
		{
			name: "add some same params ",
			uri:  "https://maps.yandex.ru",
			params: map[string][]string{
				"test1": {"11", "12"},
				"test2": {"21", "22"},
			},
			want: "https://maps.yandex.ru?test1=11&test1=12&test2=21&test2=22",
		},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			res, err := GlueParams(test.uri, test.params)

			require.NoError(t, err)
			assert.Equal(t, test.want, res)
		})
	}
}
