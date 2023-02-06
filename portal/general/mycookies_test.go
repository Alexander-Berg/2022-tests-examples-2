package models

import (
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/library/go/test/assertpb"
	"a.yandex-team.ru/portal/avocado/proto/morda_data"
)

func TestNewMyCookies(t *testing.T) {
	type args struct {
		dto *morda_data.Cookie_My
	}
	tests := []struct {
		name string
		args args
		want MyCookie
	}{
		{
			name: "nil",
			args: args{dto: nil},
			want: MyCookie{},
		},
		{
			name: "nil map",
			args: args{
				dto: &morda_data.Cookie_My{
					Parsed: nil,
				},
			},
			want: MyCookie{Parsed: map[uint32][]int32{}},
		},
		{
			name: "empty map",
			args: args{
				dto: &morda_data.Cookie_My{
					Parsed: map[uint32]*morda_data.Cookie_My_MyValue{},
				},
			},
			want: MyCookie{Parsed: map[uint32][]int32{}},
		},
		{
			name: "map with values and nils",
			args: args{
				dto: &morda_data.Cookie_My{
					Parsed: map[uint32]*morda_data.Cookie_My_MyValue{
						1: nil,
						2: {Values: nil},
						3: {Values: []int32{}},
						4: {Values: []int32{42}},
						5: {Values: []int32{42, 43}},
					},
				},
			},
			want: MyCookie{
				Parsed: map[uint32][]int32{
					1: nil,
					2: nil,
					3: {},
					4: {42},
					5: {42, 43},
				},
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := NewMyCookie(tt.args.dto)
			assert.Equal(t, tt.want, got)
		})
	}
}

func TestMyCookies_DTO(t *testing.T) {
	tests := []struct {
		name  string
		model *MyCookie
		want  *morda_data.Cookie_My
	}{
		{
			name:  "nil",
			model: nil,
			want:  nil,
		},
		{
			name: "nil map",
			model: &MyCookie{
				Parsed: nil,
			},
			want: &morda_data.Cookie_My{
				Parsed: map[uint32]*morda_data.Cookie_My_MyValue{},
			},
		},
		{
			name: "empty map",
			model: &MyCookie{
				Parsed: map[uint32][]int32{},
			},
			want: &morda_data.Cookie_My{
				Parsed: map[uint32]*morda_data.Cookie_My_MyValue{},
			},
		},
		{
			name: "map with values and nils",
			model: &MyCookie{
				Parsed: map[uint32][]int32{
					1: nil,
					2: {},
					3: {42},
					4: {42, 43},
				},
			},
			want: &morda_data.Cookie_My{
				Parsed: map[uint32]*morda_data.Cookie_My_MyValue{
					1: {Values: nil},
					2: {Values: []int32{}},
					3: {Values: []int32{42}},
					4: {Values: []int32{42, 43}},
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

func TestMyCookies_Get(t *testing.T) {
	type args struct {
		key uint32
	}
	tests := []struct {
		name  string
		model *MyCookie
		args  args
		want  []int32
	}{
		{
			name:  "nil model",
			model: nil,
			want:  nil,
		},
		{
			name:  "nil map",
			model: &MyCookie{Parsed: nil},
			want:  nil,
		},
		{
			name:  "no value in map",
			model: &MyCookie{Parsed: map[uint32][]int32{41: {}}},
			args:  args{key: 42},
			want:  nil,
		},
		{
			name:  "nil value in map",
			model: &MyCookie{Parsed: map[uint32][]int32{42: nil}},
			args:  args{key: 42},
			want:  nil,
		},
		{
			name:  "empty value in map",
			model: &MyCookie{Parsed: map[uint32][]int32{42: {}}},
			args:  args{key: 42},
			want:  []int32{},
		},
		{
			name:  "value in map",
			model: &MyCookie{Parsed: map[uint32][]int32{42: {99, 100}}},
			args:  args{key: 42},
			want:  []int32{99, 100},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := tt.model.Get(tt.args.key)
			assert.Equal(t, tt.want, got)
		})
	}
}

func TestMyCookies_GetLanguage(t *testing.T) {
	type fields struct {
		Parsed map[uint32][]int32
	}
	tests := []struct {
		name      string
		fields    fields
		wantValue int
		wantOk    bool
	}{
		{
			name: "got nil",
			fields: fields{
				Parsed: nil,
			},
			wantValue: 0,
			wantOk:    false,
		},
		{
			name: "got empty slice",
			fields: fields{
				Parsed: map[uint32][]int32{
					languageSlot: {},
				},
			},
			wantOk:    false,
			wantValue: 0,
		},
		{
			name: "got slice with single value",
			fields: fields{
				Parsed: map[uint32][]int32{
					languageSlot: {1},
				},
			},
			wantOk:    false,
			wantValue: 0,
		},
		{
			name: "got slice with value",
			fields: fields{
				Parsed: map[uint32][]int32{
					languageSlot: {1, 1},
				},
			},
			wantOk:    true,
			wantValue: 1,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			m := &MyCookie{
				Parsed: tt.fields.Parsed,
			}
			gotValue, gotOk := m.GetLanguage()
			if gotValue != tt.wantValue {
				t.Errorf("GetLanguage() gotValue = %v, want %v", gotValue, tt.wantValue)
			}
			if gotOk != tt.wantOk {
				t.Errorf("GetLanguage() gotOk = %v, want %v", gotOk, tt.wantOk)
			}
		})
	}
}

func TestMyCookies_IsBigForced(t *testing.T) {
	type fields struct {
		Parsed map[uint32][]int32
	}
	tests := []struct {
		name   string
		fields fields
		want   bool
	}{
		{
			name: "got nil",
			fields: fields{
				Parsed: nil,
			},
			want: false,
		},
		{
			name: "got empty slice",
			fields: fields{
				Parsed: map[uint32][]int32{
					forceMobileSlot: {},
				},
			},
			want: false,
		},
		{
			name: "got several 1 values",
			fields: fields{
				Parsed: map[uint32][]int32{
					forceMobileSlot: {1, 1, 1},
				},
			},
			want: true,
		},
		{
			name: "got 1 value",
			fields: fields{
				Parsed: map[uint32][]int32{
					forceMobileSlot: {1},
				},
			},
			want: true,
		},
		{
			name: "got non-1 value",
			fields: fields{
				Parsed: map[uint32][]int32{
					forceMobileSlot: {0},
				},
			},
			want: false,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			m := &MyCookie{
				Parsed: tt.fields.Parsed,
			}
			if got := m.IsBigForced(); got != tt.want {
				t.Errorf("IsBigForced() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestMyCookies_IsMobileForced(t *testing.T) {
	type fields struct {
		Parsed map[uint32][]int32
	}
	tests := []struct {
		name   string
		fields fields
		want   bool
	}{
		{
			name: "got nil",
			fields: fields{
				Parsed: nil,
			},
			want: false,
		},
		{
			name: "got empty slice",
			fields: fields{
				Parsed: map[uint32][]int32{
					forceMobileSlot: {},
				},
			},
			want: false,
		},
		{
			name: "got non-0 value",
			fields: fields{
				Parsed: map[uint32][]int32{
					forceMobileSlot: {1, 1, 1},
				},
			},
			want: false,
		},
		{
			name: "got 0 value",
			fields: fields{
				Parsed: map[uint32][]int32{
					forceMobileSlot: {0},
				},
			},
			want: true,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			m := &MyCookie{
				Parsed: tt.fields.Parsed,
			}
			if got := m.IsMobileForced(); got != tt.want {
				t.Errorf("IsMobileForced() = %v, want %v", got, tt.want)
			}
		})
	}
}
