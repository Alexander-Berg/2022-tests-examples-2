package utils_test

import (
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/security/yadi/libs/maven/utils"
)

func TestStep(t *testing.T) {
	var separator = "."
	var cases = []struct {
		in  string
		n   int
		out []string
	}{
		{"1.2.3", 0, []string{}},
		{"1.2.3", 1, []string{"1.2.3"}},
		{"1.2.3", 2, []string{"1", "2.3"}},
		{"1-2-3", 2, []string{"1-2-3"}},
		{"1.2.3", -1, []string{"1", "2", "3"}},
		{"1.2.3-4", -1, []string{"1", "2", "3-4"}},
	}

	for _, tc := range cases {
		t.Run(tc.in, func(t *testing.T) {
			result := utils.SplitNWithAnySep(tc.in, separator, tc.n)
			assert.Len(t, result, len(tc.out))
			for i := range result {
				assert.Equal(t, tc.out[i], result[i])
			}
		})
	}
}

func TestMultiSeparators(t *testing.T) {
	var cases = []struct {
		in, sepset string
		n          int
		out        []string
	}{
		{"1.2-3", "-", 2, []string{"1.2", "3"}},
		{"1.2.3", ".", -1, []string{"1", "2", "3"}},
		{"1-2.3", ".-", -1, []string{"1", "2", "3"}},
		{"1-2-3.4.5-6", "!.-_", -1, []string{"1", "2", "3", "4", "5", "6"}},
		{"1-2.3-4", "-.", 3, []string{"1", "2", "3-4"}},
		{".1.-.2--3..4!", ".-", -1, []string{"1", "2", "3", "4!"}},
	}

	for _, tc := range cases {
		t.Run(tc.in, func(t *testing.T) {
			result := utils.SplitNWithAnySep(tc.in, tc.sepset, tc.n)
			assert.Len(t, result, len(tc.out))
			for i := range result {
				assert.Equal(t, tc.out[i], result[i])
			}
		})
	}
}
