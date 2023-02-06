package agent

import (
	"fmt"
	"os"
	"testing"

	"a.yandex-team.ru/security/skotty/robossh/internal/logger"
)

func TestMain(m *testing.M) {
	if err := logger.InitLogger(true); err != nil {
		panic(fmt.Sprintf("setup logger: %v", err))
	}

	os.Exit(m.Run())
}
