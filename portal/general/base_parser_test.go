package req

import (
	"testing"

	"github.com/stretchr/testify/require"

	protobigb "a.yandex-team.ru/ads/bsyeti/eagle/collect/proto"
	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/libs/utils/common"
	"a.yandex-team.ru/portal/avocado/libs/utils/yabs"
	"a.yandex-team.ru/portal/morda-go/tests/prepared"
)

var emptyBigB = models.BigB{
	TargetingInfo: models.TargetingInfo{
		PromoGroups:      common.NewStringSet(),
		RecentlyServices: map[string]models.Services{},
		Age:              []models.NumericSegment{},
		Gender:           []models.NumericSegment{},
		StatefulSearch:   map[string]models.StatefulSearch{},
	},
}
var emptyBigBURL = &protobigb.TQueryParams{}

func Test_ParseCompare(t *testing.T) {
	tests := []struct {
		name    string
		content string
		want    *base
		wantErr bool
	}{
		{
			name:    "empty json",
			content: ``,
			wantErr: true,
		},
		{
			name:    "empty object",
			content: `{}`,
			want: &base{
				device: models.Device{
					BrowserDesc: &models.BrowserDesc{},
				},
				bigB:    emptyBigB,
				bigBURL: emptyBigBURL,
			},
		},
		{
			name: "empty compare",
			content: `{
				"compare": {}
			}`,
			want: &base{
				device: models.Device{
					BrowserDesc: &models.BrowserDesc{},
				},
				bigB:    emptyBigB,
				bigBURL: emptyBigBURL,
			},
		},
		{
			name: "empty ab flags",
			content: `{
				"compare": {
					"abFlags": {}
				}
			}`,
			want: &base{
				device: models.Device{
					BrowserDesc: &models.BrowserDesc{},
				},
				bigB:    emptyBigB,
				bigBURL: emptyBigBURL,
			},
		},
		{
			name: "empty ab flags",
			content: `{
				"compare": {
					"abFlags": {
						"flags": {}
					}
				}
			}`,
			want: &base{
				abFlags: models.ABFlags{
					Flags: map[string]string{},
				},
				device: models.Device{
					BrowserDesc: &models.BrowserDesc{},
				},
				bigB:    emptyBigB,
				bigBURL: emptyBigBURL,
			},
		},
		{
			name: "filled ab flags",
			content: `{
				"compare": {
					"abFlags": {
						"flags": {
							"city": {"value": "moscow"},
							"car": {"value": "bmw"},
							"colour": {"value": "red"},
							"number": {"value": 2}
						},
						"slices": ["123", "qwe"]
					}
				}
			}`,
			want: &base{
				abFlags: models.ABFlags{
					Flags: map[string]string{
						"city":   "moscow",
						"car":    "bmw",
						"colour": "red",
						"number": "2",
					},
					SliceNames: []string{"123", "qwe"},
				},
				device: models.Device{
					BrowserDesc: &models.BrowserDesc{},
				},
				bigB:    emptyBigB,
				bigBURL: emptyBigBURL,
			},
		},
		{
			name: "filled morda zone",
			content: `{
				"compare": {
					"mordaZone": "ru"
				}
			}`,
			want: &base{
				mordazone: models.MordaZone{
					Value: "ru",
				},
				device: models.Device{
					BrowserDesc: &models.BrowserDesc{},
				},
				bigB:    emptyBigB,
				bigBURL: emptyBigBURL,
			},
		},
		{
			name: "filled morda content",
			content: `{
				"compare": {
					"mordaContent": "big"
				}
			}`,
			want: &base{
				mordaContent: models.MordaContent{
					Value: "big",
				},
				device: models.Device{
					BrowserDesc: &models.BrowserDesc{},
				},
				bigB:    emptyBigB,
				bigBURL: emptyBigBURL,
			},
		},
		{
			name: "filled gramps as 1",
			content: `{
				"compare": {
					"gramps": 1
				}
			}`,
			want: &base{
				device: models.Device{
					BrowserDesc: &models.BrowserDesc{
						IsGramps: true,
					},
				},
				geo:     models.Geo{},
				bigB:    emptyBigB,
				bigBURL: emptyBigBURL,
			},
		},
		{
			name: "filled gramps as 0",
			content: `{
				"compare": {
					"gramps": 0
				}
			}`,
			want: &base{
				device: models.Device{
					BrowserDesc: &models.BrowserDesc{
						IsGramps: false,
					},
				},
				geo:     models.Geo{},
				bigB:    emptyBigB,
				bigBURL: emptyBigBURL,
			},
		},
		{
			name: "filled gramps as string",
			content: `{
				"compare": {
					"gramps": "1"
				}
			}`,
			want: &base{
				device: models.Device{
					BrowserDesc: &models.BrowserDesc{
						IsGramps: true,
					},
				},
				geo:     models.Geo{},
				bigB:    emptyBigB,
				bigBURL: emptyBigBURL,
			},
		},
		{
			name: "filled touchGramps as 1",
			content: `{
				"compare": {
					"touchGramps": 1
				}
			}`,
			want: &base{
				device: models.Device{
					BrowserDesc: &models.BrowserDesc{
						IsTouchGramps: true,
					},
				},
				geo:     models.Geo{},
				bigB:    emptyBigB,
				bigBURL: emptyBigBURL,
			},
		},
		{
			name: "filled touchGramps as 0",
			content: `{
				"compare": {
					"touchGramps": 0
				}
			}`,
			want: &base{
				device: models.Device{
					BrowserDesc: &models.BrowserDesc{
						IsTouchGramps: false,
					},
				},
				geo:     models.Geo{},
				bigB:    emptyBigB,
				bigBURL: emptyBigBURL,
			},
		},
		{
			name: "filled touchGramps as string",
			content: `{
				"compare": {
					"touchGramps": "1"
				}
			}`,
			want: &base{
				device: models.Device{
					BrowserDesc: &models.BrowserDesc{
						IsTouchGramps: true,
					},
				},
				geo:     models.Geo{},
				bigB:    emptyBigB,
				bigBURL: emptyBigBURL,
			},
		},
		{
			name: "filled yandexuid",
			content: `{
				"compare": {
					"auth": {
						"yandexuid": "1234567890987"
					}
				}
			}`,
			want: &base{
				yandexUID: "1234567890987",
				device: models.Device{
					BrowserDesc: &models.BrowserDesc{},
				},
				bigB:    emptyBigB,
				bigBURL: emptyBigBURL,
			},
		},
		{
			name: "filled yandexuid as number",
			content: `{
				"compare": {
					"auth": {
						"yandexuid": 1234567890987
					}
				}
			}`,
			want: &base{
				yandexUID: "1234567890987",
				device: models.Device{
					BrowserDesc: &models.BrowserDesc{},
				},
				bigB:    emptyBigB,
				bigBURL: emptyBigBURL,
			},
		},
		{
			name: "filled geo",
			content: `{
				"compare": {
					"geo": {
						"GeoByDomainIp": "213",
						"GeoAndParentsList": ["1", "100"]
					}
				}
			}`,
			want: &base{
				geo: models.Geo{
					RegionID: 213,
					Parents:  []uint32{1, 100},
				},
				device: models.Device{
					BrowserDesc: &models.BrowserDesc{},
				},
				bigB:    emptyBigB,
				bigBURL: emptyBigBURL,
			},
		},
		{
			name: "filled geo with numbers",
			content: `{
				"compare": {
					"geo": {
						"GeoByDomainIp": 213,
						"GeoAndParentsList": ["1", "100"]
					}
				}
			}`,
			want: &base{
				geo: models.Geo{
					RegionID: 213,
					Parents:  []uint32{1, 100},
				},
				device: models.Device{
					BrowserDesc: &models.BrowserDesc{},
				},
				bigB:    emptyBigB,
				bigBURL: emptyBigBURL,
			},
		},
		{
			name: "filled yabs",
			content: `{
				"compare": {
					"yabs": {
						"bk_flags": {
							"flag_aaa": {
								"click_url": "",
								"close_url": "http://yabs.yandex.ru/count/7777/15111992",
								"linknext": "=WN4ejI_AAA"
							},
							"flag_bbb": {
								"click_url": "http://yabs.yandex.ru/count/QQQQQQ",
								"close_url": "http://yabs.yandex.ru/count/8888/15111992",
								"linknext": "=WN4ejI_BBB"
							}
						}
					}
				}
			}`,
			want: &base{
				device: models.Device{
					BrowserDesc: &models.BrowserDesc{},
				},
				yabs: models.Yabs{
					BKFlags: map[string]models.BKFlag{
						"flag_aaa": {
							ClickURL: "",
							CloseURL: "http://yabs.yandex.ru/count/7777/15111992",
							LinkNext: "=WN4ejI_AAA",
						},
						"flag_bbb": {
							ClickURL: "http://yabs.yandex.ru/count/QQQQQQ",
							CloseURL: "http://yabs.yandex.ru/count/8888/15111992",
							LinkNext: "=WN4ejI_BBB",
						},
					},
				},
				bigB:    emptyBigB,
				bigBURL: emptyBigBURL,
			},
		},
		{
			name: "filled yabs url",
			content: `{
				"compare": {
					"yabs": {
						"url": {
							"host": "yabs.yandex.ru",
							"path": "/page/123456",
							"cgi_args": {
								"fruit": "apple",
								"town": "korolyov",
								"number": "15111992"
							}
						}
					}
				}
			}`,
			want: &base{
				device: models.Device{
					BrowserDesc: &models.BrowserDesc{},
				},
				bigB:    emptyBigB,
				bigBURL: emptyBigBURL,
				yabsURL: yabs.Request{
					Host: "yabs.yandex.ru",
					Path: "/page/123456",
					CGIArgs: map[string]string{
						"fruit":  "apple",
						"town":   "korolyov",
						"number": "15111992",
					},
				},
			},
		},
		{
			name: "filled locale",
			content: `{
				"compare": {
					"locale": "ru"
				}
			}`,
			want: &base{
				locale: models.Locale{
					Value: "ru",
				},
				device: models.Device{
					BrowserDesc: &models.BrowserDesc{},
				},
				bigB:    emptyBigB,
				bigBURL: emptyBigBURL,
			},
		},
		{
			name: "filled clid",
			content: `{
				"compare": {
					"clid": "12345"
				}
			}`,
			want: &base{
				clid: models.Clid{
					Client: "12345",
				},
				device: models.Device{
					BrowserDesc: &models.BrowserDesc{},
				},
				bigB:    emptyBigB,
				bigBURL: emptyBigBURL,
			},
		},
		{
			name: "filled clid as number",
			content: `{
				"compare": {
					"clid": 12345
				}
			}`,
			want: &base{
				clid: models.Clid{
					Client: "12345",
				},
				device: models.Device{
					BrowserDesc: &models.BrowserDesc{},
				},
				bigB:    emptyBigB,
				bigBURL: emptyBigBURL,
			},
		},
		{
			name: "filled bigB",
			content: `{
				"compare": {
					"bigB": {
						"targeting_info": {
							"cryptaid2": 6304896188630272087,
							"data_bass": [],
							"promo-groups": {
								"557:2000428359": 1,
								"557:2000718804": 1,
								"557:2001383267": 1
							},
							"recently_services": {
								"visits_common": {
									"news": {
										"name": "news",
										"updatetime": 1647007493,
										"weight": 3.651119471
									}
								},
								"watch_common": {
									"maps": {
										"name": "maps",
										"updatetime": 1649991865,
										"weight": 1
									},
									"pogoda": {
										"name": "pogoda",
										"updatetime": 1650291618,
										"weight": 1.999997616
									}
								}
							},
							"age": [
								{
									"id": 175,
									"value": 1,
									"weight": 90069
								},
								{
									"id": 175,
									"value": 2,
									"weight": 751134
								},
								{
									"id": 175,
									"value": 4,
									"weight": 15809
								}
							],
							"gender": [
								{
									"id": 174,
									"value": 0,
									"weight": 958280
								},
								{
									"id": 174,
									"value": 1,
									"weight": 41719
								}
							],
							"market_cart": {
								"total_cost": 9999,
								"count": 4
							},
							"stateful_search": {
								"pregnancy": {
									"name": "pregnancy",
									"refused": 0,
									"theme_id": 2174754698598328073
								},
								"travel": {
									"name": "travel",
									"refused": 0,
									"theme_id": 16287450586626029612
								}
							},
							"clid_type": 42,
							"top-internal": 43,
							"social": 44
						}
					}
				}
			}`,
			want: &base{
				device: models.Device{
					BrowserDesc: &models.BrowserDesc{},
				},
				bigB:    prepared.TestModelBigBVer1,
				bigBURL: emptyBigBURL,
			},
		},
		{
			name: "filled bigB with strings",
			content: `{
				"compare": {
					"bigB": {
						"targeting_info": {
							"cryptaid2": "6304896188630272087",
							"data_bass": [],
							"promo-groups": {
								"557:2000428359": "1",
								"557:2000718804": "1",
								"557:2001383267": "1"
							},
							"recently_services": {
								"visits_common": {
									"news": {
										"name": "news",
										"updatetime": "1647007493",
										"weight": "3.651119471"
									}
								},
								"watch_common": {
									"maps": {
										"name": "maps",
										"updatetime": "1649991865",
										"weight": "1"
									},
									"pogoda": {
										"name": "pogoda",
										"updatetime": "1650291618",
										"weight": "1.999997616"
									}
								}
							},
							"age": [
								{
									"id": "175",
									"value": "1",
									"weight": "90069"
								},
								{
									"id": "175",
									"value": "2",
									"weight": "751134"
								},
								{
									"id": "175",
									"value": "4",
									"weight": "15809"
								}
							],
							"gender": [
								{
									"id": "174",
									"value": "0",
									"weight": "958280"
								},
								{
									"id": "174",
									"value": "1",
									"weight": "41719"
								}
							],
							"market_cart": {
								"total_cost": "9999",
								"count": "4"
							},
							"stateful_search": {
								"pregnancy": {
									"name": "pregnancy",
									"refused": "0",
									"theme_id": "2174754698598328073"
								},
								"travel": {
									"name": "travel",
									"refused": "0",
									"theme_id": "16287450586626029612"
								}
							},
							"clid_type": "42",
							"top-internal": "43",
							"social": "44"
						}
					}
				}
			}`,
			want: &base{
				device: models.Device{
					BrowserDesc: &models.BrowserDesc{},
				},
				bigB:    prepared.TestModelBigBVer1,
				bigBURL: emptyBigBURL,
			},
		},
		{
			name: "filled madm content",
			content: `{
				"compare": {
					"madmContent": ["all", "big"]
				}
			}`,
			want: &base{
				bigB:    emptyBigB,
				bigBURL: emptyBigBURL,
				device: models.Device{
					BrowserDesc: &models.BrowserDesc{},
				},
				madmContent: models.MadmContent{
					Values: []string{"all", "big"},
				},
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			parser := NewBaseParser()
			got, err := parser.Parse([]byte(tt.content))
			if !tt.wantErr {
				require.NoError(t, err)
				require.Equal(t, tt.want, got)
			} else {
				require.Nil(t, got)
				require.Error(t, err)
			}
		})
	}
}
