package retry_test

import (
	"context"
	"fmt"
	"io"
	"net/http"
	"time"

	"a.yandex-team.ru/library/go/core/log"
	"a.yandex-team.ru/library/go/core/log/zap"
	"a.yandex-team.ru/security/libs/go/retry"
	"a.yandex-team.ru/security/libs/go/retry/backoff"
)

func ExampleRetrier() {
	zlog, err := zap.New(zap.ConsoleConfig(log.DebugLevel))
	if err != nil {
		panic(err)
	}

	retrier := retry.New(
		retry.WithAttempts(2),
		retry.WithBackOff(backoff.NewExponential(20*time.Millisecond, time.Second)),
	)

	var body []byte
	work := func(ctx context.Context) error {
		resp, err := http.Get("http://ya.ru")
		if err != nil {
			return err
		}

		defer func() { _ = resp.Body.Close() }()
		body, err = io.ReadAll(resp.Body)
		if err != nil {
			return err
		}
		return nil
	}

	notify := func(err error, delay time.Duration) {
		zlog.Warn("retry", log.String("operation", "get_ya_http"), log.Duration("delay", delay))
	}

	err = retrier.TryNotify(context.TODO(), work, notify)
	if err != nil {
		panic(err)
	}

	fmt.Println(string(body))
}
