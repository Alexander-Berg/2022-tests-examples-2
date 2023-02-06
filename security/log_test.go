package simplelog_test

import (
	"bytes"
	"errors"
	"strings"
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/security/libs/go/simplelog"
)

func TestInternalCA(t *testing.T) {
	var out bytes.Buffer
	logger := simplelog.NewLogger(&simplelog.LoggerOpts{
		Writer: &out,
	})

	logger.Info("info", "foo", "bar")
	assert.Regexp(t, `\[INFO\] \[[^]]+\] info\s+foo="bar"$`, strings.TrimSpace(out.String()))
	out.Reset()

	logger.Warn("warning", "foo", 1, "bar", 2)
	assert.Regexp(t, `\[WARN\] \[[^]]+\] warning\s+foo="1" bar="2"$`, strings.TrimSpace(out.String()))
	out.Reset()

	logger.Error("error", "err", errors.New("test err"))
	assert.Regexp(t, `\[EROR\] \[[^]]+\] error\s+err="test err"$`, strings.TrimSpace(out.String()))
	out.Reset()
}
