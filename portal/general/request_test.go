package models

import (
	"fmt"
	"math"
	"net/url"
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/library/go/test/assertpb"
	mordadata "a.yandex-team.ru/portal/avocado/proto/morda_data"
)

const flagsCount = 3

func TestNewRequest(t *testing.T) {
	type args struct {
		dto *mordadata.Request
	}
	type testCase struct {
		name string
		args args
		want *Request
	}
	tests := []testCase{
		{
			name: "all simple fields",
			args: args{
				dto: &mordadata.Request{
					IsInternal:   true,
					IsStaffLogin: true,
					IsPumpkin:    true,
					Url:          []byte("/ab/cde/"),
					Ip:           []byte("1.2.3.4"),
					Cgi:          map[string]*mordadata.Request_BytesSlice{},
					Host:         []byte("yandex.ru"),
				},
			},
			want: &Request{
				IsInternal:        true,
				IsStaffLogin:      true,
				IsPumpkin:         true,
				URL:               "/ab/cde/",
				IP:                "1.2.3.4",
				CGI:               url.Values{},
				Host:              "yandex.ru",
				SearchAppFeatures: make([]SearchAppFeature, 0),
			},
		},
		{
			name: "nil cgi",
			args: args{
				dto: &mordadata.Request{
					Cgi: nil,
				},
			},
			want: &Request{
				CGI:               url.Values{},
				SearchAppFeatures: make([]SearchAppFeature, 0),
			},
		},
		{
			name: "nil Request",
			args: args{
				dto: nil,
			},
			want: nil,
		},
		{
			name: "filled cgi",
			args: args{
				dto: &mordadata.Request{
					Cgi: map[string]*mordadata.Request_BytesSlice{
						"animal": {
							Value: [][]byte{
								[]byte("dog"),
								[]byte("cat"),
								[]byte("goat"),
							},
						},
						"fruit": {
							Value: [][]byte{
								[]byte("apple"),
								[]byte("banana"),
							},
						},
						"city": {
							Value: [][]byte{
								[]byte("Moscow"),
							},
						},
						"drink": {
							Value: [][]byte{},
						},
						"season": {
							Value: nil,
						},
					},
				},
			},
			want: &Request{
				CGI: url.Values{
					"animal": {"dog", "cat", "goat"},
					"fruit":  {"apple", "banana"},
					"city":   {"Moscow"},
					"drink":  {},
					"season": nil,
				},
				SearchAppFeatures: make([]SearchAppFeature, 0),
			},
		},
		{
			name: "request with apiInfo",
			args: args{
				dto: &mordadata.Request{
					ApiInfo: &mordadata.Request_APIInfo{
						Name:        []byte("name"),
						Version:     5,
						RealName:    []byte("real_name"),
						RealVersion: 9,
					},
				},
			},
			want: &Request{
				APIInfo: APIInfo{
					Name:        "name",
					Version:     5,
					RealName:    "real_name",
					RealVersion: 9,
				},
				CGI:               url.Values{},
				SearchAppFeatures: make([]SearchAppFeature, 0),
			},
		},
		{
			name: "request with SearchApp features",
			args: args{
				dto: &mordadata.Request{
					SearchAppFeatures: []*mordadata.Request_SearchAppFeature{
						{
							Name:    "keyboard",
							Enabled: false,
						},
						{
							Name:    "darktheme",
							Enabled: true,
						},
						{
							Name:    "widget",
							Enabled: false,
							Parameters: map[string]string{
								"type": "searchlib_4x2",
							},
						},
						{
							Name:    "widget",
							Enabled: true,
							Parameters: map[string]string{
								"type": "2x1",
							},
						},
					},
				},
			},
			want: &Request{
				SearchAppFeatures: SearchAppFeatures{
					{
						Name:    "keyboard",
						Enabled: false,
					},
					{
						Name:    "darktheme",
						Enabled: true,
					},
					{
						Name:    "widget",
						Enabled: false,
						Parameters: map[string]string{
							"type": "searchlib_4x2",
						},
					},
					{
						Name:    "widget",
						Enabled: true,
						Parameters: map[string]string{
							"type": "2x1",
						},
					},
				},
				CGI: url.Values{},
			},
		},
	}

	for _, pair := range shuffleFlags() {
		pair.model.CGI = url.Values{}
		pair.model.SearchAppFeatures = make([]SearchAppFeature, 0)
		model := pair.model

		tests = append(tests, testCase{
			name: fmt.Sprintf("shuffle flags: %t %t %t",
				pair.dto.IsInternal, pair.dto.IsStaffLogin, pair.dto.IsPumpkin),
			args: args{
				dto: pair.dto,
			},
			want: &model,
		})
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := NewRequest(tt.args.dto)
			assert.Equal(t, tt.want, got)
		})
	}
}

func TestRequest_DTO(t *testing.T) {
	type testCase struct {
		name  string
		model *Request
		want  *mordadata.Request
	}

	tests := []testCase{
		{
			name:  "model is nil",
			model: nil,
			want:  nil,
		},
		{
			name: "all simple fields",
			model: &Request{
				IsInternal:   true,
				IsStaffLogin: true,
				IsPumpkin:    true,
				URL:          "/ab/cde/",
				IP:           "1.2.3.4",
				CGI:          url.Values{},
				Host:         "yandex.ru",
			},
			want: &mordadata.Request{
				IsInternal:   true,
				IsStaffLogin: true,
				IsPumpkin:    true,
				Url:          []byte("/ab/cde/"),
				Ip:           []byte("1.2.3.4"),
				Cgi:          map[string]*mordadata.Request_BytesSlice{},
				Host:         []byte("yandex.ru"),
				ApiInfo:      &mordadata.Request_APIInfo{},
			},
		},
		{
			name: "nil cgi",
			model: &Request{
				CGI: nil,
			},
			want: &mordadata.Request{
				Cgi:               map[string]*mordadata.Request_BytesSlice{},
				Url:               []byte(""),
				Ip:                []byte(""),
				ApiInfo:           &mordadata.Request_APIInfo{},
				SearchAppFeatures: make([]*mordadata.Request_SearchAppFeature, 0),
			},
		},
		{
			name: "filled cgi",
			model: &Request{
				CGI: url.Values{
					"animal": {"dog", "cat", "goat"},
					"fruit":  {"apple", "banana"},
					"city":   {"Moscow"},
					"drink":  {},
					"season": nil,
				},
			},
			want: &mordadata.Request{
				Cgi: map[string]*mordadata.Request_BytesSlice{
					"animal": {
						Value: [][]byte{
							[]byte("dog"),
							[]byte("cat"),
							[]byte("goat"),
						},
					},
					"fruit": {
						Value: [][]byte{
							[]byte("apple"),
							[]byte("banana"),
						},
					},
					"city": {
						Value: [][]byte{
							[]byte("Moscow"),
						},
					},
					"drink": {
						Value: [][]byte{},
					},
					"season": {
						Value: nil,
					},
				},
				Url:               []byte(""),
				Ip:                []byte(""),
				Host:              []byte(""),
				ApiInfo:           &mordadata.Request_APIInfo{},
				SearchAppFeatures: make([]*mordadata.Request_SearchAppFeature, 0),
			},
		},
		{
			name: "request with apiInfo",
			model: &Request{
				APIInfo: APIInfo{
					Name:        "name",
					Version:     5,
					RealName:    "real_name",
					RealVersion: 9,
				},
			},
			want: &mordadata.Request{
				Cgi: map[string]*mordadata.Request_BytesSlice{},
				ApiInfo: &mordadata.Request_APIInfo{
					Name:        []byte("name"),
					Version:     5,
					RealName:    []byte("real_name"),
					RealVersion: 9,
				},
				SearchAppFeatures: make([]*mordadata.Request_SearchAppFeature, 0),
			},
		},
		{
			name: "request with SearchApp features",
			model: &Request{
				SearchAppFeatures: SearchAppFeatures{
					{
						Name:    "keyboard",
						Enabled: false,
					},
					{
						Name:    "darktheme",
						Enabled: true,
					},
					{
						Name:    "widget",
						Enabled: false,
						Parameters: map[string]string{
							"type": "searchlib_4x2",
						},
					},
					{
						Name:    "widget",
						Enabled: true,
						Parameters: map[string]string{
							"type": "2x1",
						},
					},
				},
			},
			want: &mordadata.Request{
				SearchAppFeatures: []*mordadata.Request_SearchAppFeature{
					{
						Name:    "keyboard",
						Enabled: false,
					},
					{
						Name:    "darktheme",
						Enabled: true,
					},
					{
						Name:    "widget",
						Enabled: false,
						Parameters: map[string]string{
							"type": "searchlib_4x2",
						},
					},
					{
						Name:    "widget",
						Enabled: true,
						Parameters: map[string]string{
							"type": "2x1",
						},
					},
				},
				Cgi:     map[string]*mordadata.Request_BytesSlice{},
				ApiInfo: &mordadata.Request_APIInfo{},
			},
		},
	}

	for _, pair := range shuffleFlags() {
		pair.dto.Cgi = map[string]*mordadata.Request_BytesSlice{}
		pair.dto.ApiInfo = &mordadata.Request_APIInfo{}
		// pair.dto.SearchAppFeatures = make([]*mordadata.Request_SearchAppFeature, 0)
		model := pair.model

		tests = append(tests, testCase{
			name: fmt.Sprintf("shuffle flags: %t %t %t",
				pair.dto.IsInternal, pair.dto.IsStaffLogin, pair.dto.IsPumpkin),
			model: &model,
			want:  pair.dto,
		})
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := tt.model.DTO()
			assertpb.Equal(t, tt.want, got)
		})
	}
}

func TestSearchAppFeatures_GetEnabled(t *testing.T) {
	type testCase struct {
		name  string
		model SearchAppFeatures
		want  []string
	}

	cases := []testCase{
		{
			name:  "nil request",
			model: nil,
			want:  make([]string, 0),
		},
		{
			name:  "nil features",
			model: make([]SearchAppFeature, 0),
			want:  make([]string, 0),
		},
		{
			name: "no enabled features",
			model: SearchAppFeatures{
				{
					Name:    "keyboard",
					Enabled: false,
				},
				{
					Name:    "darktheme",
					Enabled: false,
				},
				{
					Name:    "account",
					Enabled: false,
				},
			},
			want: make([]string, 0),
		},
		{
			name: "has some enabled features",
			model: SearchAppFeatures{
				{
					Name:    "keyboard",
					Enabled: true,
				},
				{
					Name:    "darktheme",
					Enabled: false,
				},
				{
					Name:    "account",
					Enabled: true,
				},
			},
			want: []string{"account", "keyboard"},
		},
		{
			name: "disabled mutliple features with same name and different params",
			model: SearchAppFeatures{
				{
					Name:    "widget",
					Enabled: false,
					Parameters: map[string]string{
						"type": "searchlib_weather",
					},
				},
				{
					Name:    "widget",
					Enabled: false,
					Parameters: map[string]string{
						"type": "searchlib_4x2",
					},
				},
				{
					Name:    "widget",
					Enabled: false,
					Parameters: map[string]string{
						"type": "2x1",
					},
				},
			},
			want: make([]string, 0),
		},
		{
			name: "mutliple features with same name and different params with one enabled",
			model: SearchAppFeatures{
				{
					Name:    "widget",
					Enabled: false,
					Parameters: map[string]string{
						"type": "searchlib_weather",
					},
				},
				{
					Name:    "widget",
					Enabled: false,
					Parameters: map[string]string{
						"type": "searchlib_4x2",
					},
				},
				{
					Name:    "widget",
					Enabled: true,
					Parameters: map[string]string{
						"type": "2x1",
					},
				},
			},
			want: []string{"widget"},
		},
		{
			name: "mutliple features with same name and different params with several enabled",
			model: SearchAppFeatures{
				{
					Name:    "widget",
					Enabled: true,
					Parameters: map[string]string{
						"type": "searchlib_weather",
					},
				},
				{
					Name:    "widget",
					Enabled: true,
					Parameters: map[string]string{
						"type": "searchlib_4x2",
					},
				},
				{
					Name:    "widget",
					Enabled: true,
					Parameters: map[string]string{
						"type": "2x1",
					},
				},
			},
			want: []string{"widget"},
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			actual := tt.model.GetEnabled()
			assert.Equal(t, tt.want, actual)
		})
	}
}

type pair struct {
	model Request
	dto   *mordadata.Request
}

func shuffleFlags() []pair {
	var pairs []pair

	for i := 0; i < int(math.Pow(2, float64(flagsCount))); i++ {
		isInternal := bitValue(i, 0)
		isStaffLogin := bitValue(i, 1)
		isPumpkin := bitValue(i, 2)

		pairs = append(pairs, pair{
			model: Request{
				IsInternal:   isInternal,
				IsStaffLogin: isStaffLogin,
				IsPumpkin:    isPumpkin,
			},
			dto: &mordadata.Request{
				IsInternal:   isInternal,
				IsStaffLogin: isStaffLogin,
				IsPumpkin:    isPumpkin,
			},
		})
	}

	return pairs
}

func bitValue(n, pos int) bool {
	return (n>>pos)&1 == 1
}

func TestNewAPIInfo(t *testing.T) {
	type args struct {
		dto *mordadata.Request_APIInfo
	}
	tests := []struct {
		name string
		args args
		want APIInfo
	}{
		{
			name: "nil dto",
			args: args{
				dto: nil,
			},
			want: APIInfo{},
		},
		{
			name: "empty dto",
			args: args{
				dto: &mordadata.Request_APIInfo{},
			},
			want: APIInfo{},
		},
		{
			name: "filled dto",
			args: args{
				dto: &mordadata.Request_APIInfo{
					Name:        []byte("name"),
					Version:     5,
					RealName:    []byte("real_name"),
					RealVersion: 9,
				},
			},
			want: APIInfo{
				Name:        "name",
				Version:     5,
				RealName:    "real_name",
				RealVersion: 9,
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := NewAPIInfo(tt.args.dto)
			assert.Equal(t, tt.want, got)
		})
	}
}

func TestAPIInfo_DTO(t *testing.T) {
	tests := []struct {
		name  string
		model *APIInfo
		want  *mordadata.Request_APIInfo
	}{
		{
			name:  "nil apiInfo",
			model: nil,
			want:  nil,
		},
		{
			name:  "empty model",
			model: &APIInfo{},
			want: &mordadata.Request_APIInfo{
				Name:     []byte(""),
				RealName: []byte(""),
			},
		},
		{
			name: "filled model",
			model: &APIInfo{
				Name:        "name",
				Version:     5,
				RealName:    "real_name",
				RealVersion: 9,
			},
			want: &mordadata.Request_APIInfo{
				Name:        []byte("name"),
				Version:     5,
				RealName:    []byte("real_name"),
				RealVersion: 9,
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := tt.model.DTO()
			assert.Equal(t, tt.want, got)
		})
	}
}

func Test_APIInfo_IsData(t *testing.T) {
	tests := []struct {
		name    string
		apiInfo APIInfo
		want    bool
	}{
		{
			name: "success",
			apiInfo: APIInfo{
				Name: "data",
			},
			want: true,
		},
		{
			name: "failed",
			apiInfo: APIInfo{
				Name: "test",
			},
			want: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			assert.Equal(t, tt.want, tt.apiInfo.IsData())
		})
	}
}

func Test_APIInfo_IsYabrowser(t *testing.T) {
	tests := []struct {
		name    string
		apiInfo APIInfo
		want    bool
	}{
		{
			name: "Success",
			apiInfo: APIInfo{
				RealName: "yabrowser",
			},
			want: true,
		},
		{
			name: "Failed",
			apiInfo: APIInfo{
				RealName: "FailedRealName",
			},
			want: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			assert.Equal(t, tt.want, tt.apiInfo.IsYabrowser())
		})
	}
}

func Test_APIInfo_IsYabrowser2(t *testing.T) {
	tests := []struct {
		name    string
		apiInfo APIInfo
		want    bool
	}{
		{
			name: "Success",
			apiInfo: APIInfo{
				RealName:    "yabrowser",
				RealVersion: 2,
			},
			want: true,
		},
		{
			name: "Failed RealName",
			apiInfo: APIInfo{
				RealName:    "FailedRealName",
				RealVersion: 2,
			},
			want: false,
		},
		{
			name: "Failed RealVersion",
			apiInfo: APIInfo{
				RealName:    "yabrowser",
				RealVersion: 1,
			},
			want: false,
		},
		{
			name: "Failed RealName and RealVersion",
			apiInfo: APIInfo{
				RealName:    "FailedRealName",
				RealVersion: 1,
			},
			want: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			assert.Equal(t, tt.want, tt.apiInfo.IsYabrowser2())
		})
	}
}
