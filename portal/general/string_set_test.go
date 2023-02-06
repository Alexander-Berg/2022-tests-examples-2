package common

import (
	"sort"
	"testing"

	"github.com/stretchr/testify/require"
)

func TestNewStringSet(t *testing.T) {
	type args struct {
		values []string
	}
	tests := []struct {
		name string
		args args
		want StringSet
	}{
		{
			name: "Empty input values",
			args: args{
				values: nil,
			},
			want: StringSet{},
		},
		{
			name: "One Value",
			args: args{
				values: []string{"test"},
			},
			want: StringSet{"test": struct{}{}},
		},
		{
			name: "Several different values",
			args: args{
				values: []string{"test", "smth", "587"},
			},
			want: StringSet{"587": struct{}{}, "test": struct{}{}, "smth": struct{}{}},
		},
		{
			name: "Several values with repetitions",
			args: args{
				values: []string{"test", "smth", "test", "587", "test", "test", "587"},
			},
			want: StringSet{"587": struct{}{}, "test": struct{}{}, "smth": struct{}{}},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := NewStringSet(tt.args.values...)

			require.Equal(t, tt.want, got)
		})
	}
}

func TestStringSet_Add(t *testing.T) {
	type args struct {
		values []string
	}
	tests := []struct {
		name string
		s    StringSet
		args args
		want StringSet
	}{
		{
			name: "Zero add to empty stringSet",
			s:    StringSet{},
			args: args{
				values: nil,
			},
			want: StringSet{},
		},
		{
			name: "Add one to empty stringSet",
			s:    StringSet{},
			args: args{
				values: []string{"test"},
			},
			want: StringSet{
				"test": struct{}{},
			},
		},
		{
			name: "Add one to not empty stringSet",
			s: StringSet{
				"odzo": struct{}{},
				"test": struct{}{},
			},
			args: args{
				values: []string{"587"},
			},
			want: StringSet{
				"odzo": struct{}{},
				"test": struct{}{},
				"587":  struct{}{},
			},
		},
		{
			name: "Add several values with repetitions to not empty stringSet",
			s: StringSet{
				"odzo": struct{}{},
				"test": struct{}{},
			},
			args: args{
				values: []string{"587", "odzo", "587", "odzo", "new"},
			},
			want: StringSet{
				"odzo": struct{}{},
				"test": struct{}{},
				"587":  struct{}{},
				"new":  struct{}{},
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			tt.s.Add(tt.args.values...)

			require.Equal(t, tt.want, tt.s)
		})
	}
}

func TestStringSet_Remove(t *testing.T) {
	type args struct {
		values []string
	}
	tests := []struct {
		name string
		s    StringSet
		args args
		want StringSet
	}{
		{
			name: "Try to remove from empty stringSet",
			s:    StringSet{},
			args: args{},
			want: StringSet{},
		},
		{
			name: "Try to remove non-existent element",
			s: StringSet{
				"test": struct{}{},
			},
			args: args{
				values: []string{"for_delete"},
			},
			want: StringSet{
				"test": struct{}{},
			},
		},
		{
			name: "Try to remove from empty stringSet",
			s:    StringSet{},
			args: args{
				values: []string{"for_delete"},
			},
			want: StringSet{},
		},
		{
			name: "Remove one existent element",
			s: StringSet{
				"test": struct{}{},
			},
			args: args{
				values: []string{"test"},
			},
			want: StringSet{},
		},
		{
			name: "Mix case",
			s: StringSet{
				"test": struct{}{},
				"odzo": struct{}{},
				"587":  struct{}{},
			},
			args: args{
				values: []string{"odzo", "test", "odzo", "non-existent"},
			},
			want: StringSet{
				"587": struct{}{},
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			tt.s.Remove(tt.args.values...)

			require.Equal(t, tt.want, tt.s)
		})
	}
}

func TestStringSet_IsEmpty(t *testing.T) {
	tests := []struct {
		name string
		s    StringSet
		want bool
	}{
		{
			name: "Empty stringSet",
			s:    StringSet{},
			want: true,
		},
		{
			name: "Nil stringSet",
			s:    nil,
			want: true,
		},
		{
			name: "Have one elem",
			s:    StringSet{"test": struct{}{}},
			want: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := tt.s.IsEmpty()

			require.Equal(t, tt.want, got)
		})
	}
}

func TestStringSet_Has(t *testing.T) {
	type args struct {
		v string
	}
	tests := []struct {
		name string
		s    StringSet
		args args
		want bool
	}{
		{
			name: "No elem with required key in stringSet",
			s: StringSet{
				"test": struct{}{},
			},
			args: args{
				v: "required",
			},
			want: false,
		},
		{
			name: "Has elem with required key in stringSet",
			s: StringSet{
				"test":     struct{}{},
				"required": struct{}{},
			},
			args: args{
				v: "required",
			},
			want: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := tt.s.Has(tt.args.v)

			require.Equal(t, tt.want, got)
		})
	}
}

func TestStringSet_AsSlice(t *testing.T) {
	tests := []struct {
		name string
		s    StringSet
		want []string
	}{
		{
			name: "Empty stringSet",
			s:    StringSet{},
			want: []string{},
		},
		{
			name: "One element in stringSet",
			s: StringSet{
				"test": struct{}{},
			},
			want: []string{"test"},
		},
		{
			name: "Several elements in stringSet",
			s: StringSet{
				"test": struct{}{},
				"587":  struct{}{},
				"odzo": struct{}{},
				"new":  struct{}{},
			},
			want: []string{"test", "587", "odzo", "new"},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := tt.s.AsSlice()

			sort.Strings(tt.want)
			sort.Strings(got)
			require.Equal(t, tt.want, got)
		})
	}
}

func TestStringSet_AsSortedSlice(t *testing.T) {
	tests := []struct {
		name string
		s    StringSet
		want []string
	}{
		{
			name: "Empty stringSet",
			s:    StringSet{},
			want: []string{},
		},
		{
			name: "One element in stringSet",
			s: StringSet{
				"test": struct{}{},
			},
			want: []string{"test"},
		},
		{
			name: "Several elements in stringSet",
			s: StringSet{
				"Test": struct{}{},
				"new":  struct{}{},
				"odzo": struct{}{},
				"587":  struct{}{},
				"ABC":  struct{}{},
			},
			want: []string{"587", "ABC", "Test", "new", "odzo"},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := tt.s.AsSortedSlice()

			sort.Strings(tt.want)
			sort.Strings(got)
			require.Equal(t, tt.want, got)
		})
	}
}

func TestStringSet_Copy(t *testing.T) {
	tests := []struct {
		name   string
		s      StringSet
		action func(s StringSet)
		want   StringSet
	}{
		{
			name: "No actions",
			s: StringSet{
				"test": struct{}{},
			},
			action: func(s StringSet) {},
			want: StringSet{
				"test": struct{}{},
			},
		},
		{
			name: "Add after copy; no changes in copied stringSet",
			s: StringSet{
				"test": struct{}{},
			},
			action: func(s StringSet) {
				s.Add("added")
			},
			want: StringSet{
				"test": struct{}{},
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := tt.s.Copy()

			tt.action(tt.s)

			require.Equal(t, tt.want, got)
		})
	}
}
