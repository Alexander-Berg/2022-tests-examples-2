package model

import (
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/valid"
)

func Test_Validation_err(t *testing.T) {
	tests := []struct {
		name     string
		val      interface{}
		expected string
	}{
		{"min_len char param", struct {
			F1 string `valid:"min_len=d"`
		}{"drt"}, "can't parse param d"},
		{"max_len char param", struct {
			F1 string `valid:"max_len=d"`
		}{"drt"}, "can't parse param d"},
		{"min_len null string", struct {
			F1 *NullString `valid:"min_len=1"`
		}{&NullString{}}, "string is null"},
		{"max_len null string", struct {
			F1 *NullString `valid:"max_len=1"`
		}{&NullString{}}, "string is null"},
		{"non_empty null", struct {
			F1 *interface{} `valid:"non_empty"`
		}{nil}, "must not be empty"},
		{"non_empty slice", struct {
			F1 []int `valid:"non_empty"`
		}{nil}, "must not be empty"},
		{"regexp nil", struct {
			F1 *NullString `valid:"regexp=^\\d$"`
		}{nil}, `must match ^\d$`},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			ctx := NewValidationCtx()
			err := valid.Struct(ctx, test.val)
			require.EqualError(t, err, test.expected)
		})
	}
}
