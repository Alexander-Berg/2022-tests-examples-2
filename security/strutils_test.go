package strutils_test

import (
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/security/libs/go/porto/internal/strutils"
)

func TestEmptyString(t *testing.T) {
	result := strutils.SplitQuoted(``, ';')
	assert.Empty(t, result, "split empty string -> empty slice")
}

func TestSingle(t *testing.T) {
	result := strutils.SplitQuoted(`test`, ';')
	assert.Equal(t, []string{"test"}, result)
}

func TestWoEscaped(t *testing.T) {
	result := strutils.SplitQuoted(`test1;test2;test3`, ';')
	assert.Equal(t, []string{"test1", "test2", "test3"}, result)
}

func TestWEscaped(t *testing.T) {
	result := strutils.SplitQuoted(`tes\;t1;te\st2;test3`, ';')
	assert.Equal(t, []string{`tes;t1`, `te\st2`, `test3`}, result)
}

func TestStrip(t *testing.T) {
	result := strutils.SplitQuoted(`test1 ; test2 `, ';')
	assert.Equal(t, []string{`test1`, `test2`}, result)
}

func TestEmpty(t *testing.T) {
	result := strutils.SplitQuoted(`test1 ; ;;; test2 ;  `, ';')
	assert.Equal(t, []string{`test1`, `test2`}, result)
}

func TestLastbackslash(t *testing.T) {
	result := strutils.SplitQuoted(`test1 ; test2 ;\`, ';')
	assert.Equal(t, []string{`test1`, `test2`, `\`}, result)
}
