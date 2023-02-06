package authentication

import (
	"context"
	"testing"

	"go.uber.org/zap/zaptest"

	"a.yandex-team.ru/library/go/core/log"
	"a.yandex-team.ru/library/go/core/log/zap"
	"a.yandex-team.ru/noc/alexandria/internal/usecases/ctxutils"
)

func makeLogger(t *testing.T) log.Logger {
	return &zap.Logger{L: zaptest.NewLogger(t)}
}

func makeWithLoggerCtx(t *testing.T) context.Context {
	return ctxutils.WithRequestLogger(context.Background(), makeLogger(t))
}
