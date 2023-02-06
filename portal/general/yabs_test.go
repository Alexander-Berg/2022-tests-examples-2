package models

import (
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/library/go/test/assertpb"
	mordadata "a.yandex-team.ru/portal/avocado/proto/morda_data"
)

func TestNewYabs(t *testing.T) {
	type testCase struct {
		name string
		dto  *mordadata.Yabs
		want *Yabs
	}
	tests := []testCase{
		{
			name: "nil dto",
			dto:  nil,
			want: nil,
		},
		{
			name: "nil flags",
			dto: &mordadata.Yabs{
				BkFlags: nil,
			},
			want: &Yabs{
				BKFlags: make(map[string]BKFlag),
			},
		},
		{
			name: "empty flags",
			dto: &mordadata.Yabs{
				BkFlags: make(map[string]*mordadata.Yabs_BkFlag),
			},
			want: &Yabs{
				BKFlags: make(map[string]BKFlag),
			},
		},
		{
			name: "flag with empty links",
			dto: &mordadata.Yabs{
				BkFlags: map[string]*mordadata.Yabs_BkFlag{
					"some_flag": {
						LinkNext: nil,
						CloseUrl: nil,
						ClickUrl: nil,
					},
				},
			},
			want: &Yabs{
				BKFlags: map[string]BKFlag{
					"some_flag": {
						LinkNext: "",
						CloseURL: "",
						ClickURL: "",
					},
				},
			},
		},
		{
			name: "regular value",
			dto: &mordadata.Yabs{
				BkFlags: map[string]*mordadata.Yabs_BkFlag{
					"some_flag": {
						LinkNext: []byte("link_next"),
						CloseUrl: []byte("close_url"),
						ClickUrl: []byte("click_url"),
					},
				},
			},
			want: &Yabs{
				BKFlags: map[string]BKFlag{
					"some_flag": {
						LinkNext: "link_next",
						CloseURL: "close_url",
						ClickURL: "click_url",
					},
				},
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := NewYabs(tt.dto)
			assert.Equal(t, tt.want, got)
		})
	}
}

func TestYabs_DTO(t *testing.T) {
	type testCase struct {
		name  string
		model *Yabs
		want  *mordadata.Yabs
	}

	tests := []testCase{
		{
			name:  "nil model",
			model: nil,
			want:  nil,
		},
		{
			name: "nil flags",
			model: &Yabs{
				BKFlags: nil,
			},
			want: &mordadata.Yabs{
				BkFlags: make(map[string]*mordadata.Yabs_BkFlag),
			},
		},
		{
			name: "empty flags",
			model: &Yabs{
				BKFlags: make(map[string]BKFlag),
			},
			want: &mordadata.Yabs{
				BkFlags: make(map[string]*mordadata.Yabs_BkFlag),
			},
		},
		{
			name: "flag with empty urls",
			model: &Yabs{
				BKFlags: map[string]BKFlag{
					"some_flag": {
						ClickURL: "",
						CloseURL: "",
						LinkNext: "",
					},
				},
			},
			want: &mordadata.Yabs{
				BkFlags: map[string]*mordadata.Yabs_BkFlag{
					"some_flag": {
						ClickUrl: []byte(""),
						CloseUrl: []byte(""),
						LinkNext: []byte(""),
					},
				},
			},
		},
		{
			name: "regular case",
			model: &Yabs{
				BKFlags: map[string]BKFlag{
					"some_flag": {
						ClickURL: "click_url",
						CloseURL: "close_url",
						LinkNext: "link_next",
					},
				},
			},
			want: &mordadata.Yabs{
				BkFlags: map[string]*mordadata.Yabs_BkFlag{
					"some_flag": {
						ClickUrl: []byte("click_url"),
						CloseUrl: []byte("close_url"),
						LinkNext: []byte("link_next"),
					},
				},
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := tt.model.DTO()
			assertpb.Equal(t, tt.want, got)
		})
	}
}

func TestYabs_GetOrderedBkFlags(t *testing.T) {
	type testCase struct {
		name  string
		model Yabs
		want  []string
	}

	cases := []testCase{
		{
			name:  "nil bk flags",
			model: Yabs{BKFlags: nil},
			want:  make([]string, 0),
		},
		{
			name: "empty bk flags",
			model: Yabs{
				BKFlags: make(map[string]BKFlag),
			},
			want: make([]string, 0),
		},
		{
			name: "single bk flag",
			model: Yabs{
				BKFlags: map[string]BKFlag{
					"some_flag": {
						ClickURL: "click_url",
						CloseURL: "close_url",
						LinkNext: "link_next",
					},
				},
			},
			want: []string{"some_flag"},
		},
		{
			name: "several bk flags",
			model: Yabs{
				BKFlags: map[string]BKFlag{
					"flag_D": {},
					"flag_B": {},
					"flag_E": {},
					"flag_A": {},
					"flag_C": {},
				},
			},
			want: []string{"flag_A", "flag_B", "flag_C", "flag_D", "flag_E"},
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			got := tt.model.GetOrderedBkFlags()
			assert.Equal(t, tt.want, got)
		})
	}
}
