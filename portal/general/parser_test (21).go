package yabs

import (
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
)

func TestParser_Parse(t *testing.T) {
	tests := []struct {
		name     string
		response *Response
		want     *models.Yabs
	}{
		{
			name:     "nil response",
			response: nil,
			want:     nil,
		},
		{
			name:     "no options",
			response: &Response{},
			want: &models.Yabs{
				BKFlags: make(map[string]models.BKFlag),
			},
		},
		{
			name: "response from web, option in banners",
			response: &Response{
				Banners: responseBanners{
					Options: []responseOption{
						{
							BsData: responseBsData{
								CountLinks: responseCountLinks{
									LinkTail: "link_tail",
								},
								CloseCounter: "close_url",
							},
							DirectData: responseDirectData{
								Option: "some_flag",
							},
						},
					},
				},
			},
			want: &models.Yabs{
				BKFlags: map[string]models.BKFlag{
					"some_flag": {
						ClickURL: "",
						CloseURL: "close_url",
						LinkNext: "link_tail",
					},
				},
			},
		},
		{
			name: "response from web with click url, option in banners",
			response: &Response{
				Banners: responseBanners{
					Options: []responseOption{
						{
							BsData: responseBsData{
								CountLinks: responseCountLinks{
									LinkTail: "link_tail",
								},
								CloseCounter: "close_url",
								ResourceLinks: responseResourceLinks{
									DirectData: resourceLinksDirectData{
										CounterClick: "click_url",
									},
								},
							},
							DirectData: responseDirectData{
								Option: "some_flag",
							},
						},
					},
				},
			},
			want: &models.Yabs{
				BKFlags: map[string]models.BKFlag{
					"some_flag": {
						ClickURL: "click_url",
						CloseURL: "close_url",
						LinkNext: "link_tail",
					},
				},
			},
		},
		{
			name: "response from SearchApp, option in data",
			response: &Response{
				Data: responseData{
					LinkHead: "",
					Options: []responseOption{
						{
							BsData: responseBsData{
								CountLinks: responseCountLinks{
									LinkTail: "link_tail",
								},
								CloseCounter: "close_url",
							},
							DirectData: responseDirectData{
								Option: "some_app_flag",
							},
						},
					},
				},
			},
			want: &models.Yabs{
				BKFlags: map[string]models.BKFlag{
					"some_app_flag": {
						ClickURL: "",
						CloseURL: "close_url",
						LinkNext: "link_tail",
					},
				},
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			var p parser
			actual := p.Parse(tt.response)
			assert.Equal(t, tt.want, actual)
		})
	}
}
