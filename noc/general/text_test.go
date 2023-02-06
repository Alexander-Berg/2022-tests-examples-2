package text

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestTokenizer(t *testing.T) {
	tests := []struct {
		in  string
		out []string
	}{
		{in: "test", out: []string{"test"}},
		{in: "", out: []string{}},
		{in: "  Hello  World ", out: []string{"hello", "world"}},
		{in: "ПрОвЕРка", out: []string{"проверка"}},
		{in: "Разработка (DOC (Внутренняя документация))", out: []string{"разработка", "(doc", "doc", "(внутренняя", "внутренняя", "документация))", "документация"}},
	}

	for _, test := range tests {
		assert.Equalf(t, Tokenize(test.in), test.out, "Input: %s", test.in)
	}
}
