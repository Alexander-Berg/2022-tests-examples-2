package models

import (
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/library/go/test/assertpb"
	"a.yandex-team.ru/portal/avocado/proto/morda_data"
)

func TestCookie_DTO(t *testing.T) {
	tests := []struct {
		name  string
		model *Cookie
		want  *morda_data.Cookie
	}{
		{
			name:  "nil",
			model: nil,
			want:  nil,
		},
		{
			name:  "nil fields",
			model: &Cookie{},
			want: &morda_data.Cookie{
				Parsed: map[string]*morda_data.Cookie_Value{},
			},
		},
		{
			name: "empty fields",
			model: &Cookie{
				Parsed: map[string][]string{},
			},
			want: &morda_data.Cookie{
				Parsed: map[string]*morda_data.Cookie_Value{},
			},
		},
		{
			name: "filled map",
			model: &Cookie{
				Parsed: map[string][]string{
					"a": nil,
					"b": {},
					"c": {""},
					"d": {"", "d"},
				},
			},
			want: &morda_data.Cookie{
				Parsed: map[string]*morda_data.Cookie_Value{
					"a": {Values: [][]byte{}},
					"b": {Values: [][]byte{}},
					"c": {Values: [][]byte{[]byte("")}},
					"d": {Values: [][]byte{[]byte(""), []byte("d")}},
				},
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if tt.model != nil && tt.want != nil {
				tt.want = tt.model.DTO()
			}

			got := tt.model.DTO()
			assertpb.Equal(t, tt.want, got)
		})
	}
}

func TestNewCookie(t *testing.T) {
	tests := []struct {
		name string
		dto  *morda_data.Cookie
		want *Cookie
	}{
		{
			name: "nil",
			dto:  nil,
			want: nil,
		},
		{
			name: "nil fields",
			dto: &morda_data.Cookie{
				Parsed: nil,
				My:     nil,
			},
			want: &Cookie{
				Parsed: map[string][]string{},
				My:     MyCookie{},
			},
		},
		{
			name: "empty fields",
			dto: &morda_data.Cookie{
				Parsed: map[string]*morda_data.Cookie_Value{},
				My:     &morda_data.Cookie_My{},
			},
			want: &Cookie{
				Parsed: map[string][]string{},
			},
		},
		{
			name: "filled map",
			dto: &morda_data.Cookie{
				Parsed: map[string]*morda_data.Cookie_Value{
					"a": nil,
					"b": {Values: nil},
					"c": {Values: [][]byte{}},
					"d": {Values: [][]byte{[]byte("d")}},
					"e": {Values: [][]byte{[]byte("d"), []byte("e")}},
				},
				My: &morda_data.Cookie_My{},
			},
			want: &Cookie{
				Parsed: map[string][]string{
					"a": {},
					"b": {},
					"c": {},
					"d": {"d"},
					"e": {"d", "e"},
				},
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if tt.want != nil {
				tt.want.My = NewMyCookie(tt.dto.GetMy())
			}
			got := NewCookie(tt.dto)

			assert.Equal(t, tt.want, got)
		})
	}
}
