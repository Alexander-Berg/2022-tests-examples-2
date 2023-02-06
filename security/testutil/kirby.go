package testutil

import (
	"bytes"
	"context"
	"fmt"
	"net"
	"path/filepath"
	"time"

	"github.com/go-resty/resty/v2"

	"a.yandex-team.ru/library/go/core/log"
	"a.yandex-team.ru/library/go/test/yatest"
	"a.yandex-team.ru/security/kirby/internal/app"
	"a.yandex-team.ru/security/kirby/internal/config"
	"a.yandex-team.ru/security/libs/go/retry"
	"a.yandex-team.ru/security/libs/go/retry/backoff"
)

func StartKirby(goProxyURL string) (string, func(), error) {
	kirbyPort, err := getFreePort()
	if err != nil {
		return "", nil, fmt.Errorf("can't find free port: %w", err)
	}

	kirbyPath := yatest.WorkPath("kirby")
	cfg := config.Config{
		LogLevel:       log.DebugString,
		HTTPPort:       kirbyPort,
		DirectDownload: true,
		Storage: config.Storage{
			Kind: config.StorageKingDisk,
			Disk: config.DiskStorage{
				Dir: filepath.Join(kirbyPath, "cache"),
			},
		},
		Gopher: config.Gopher{
			ListTTL: 1 * time.Minute,
			GoProxy: config.GoProxy{
				Enabled:  true,
				Timeout:  30 * time.Second,
				Endpoint: goProxyURL,
			},
		},
	}
	Logger.Info("starting kirby", log.Any("cfg", cfg))

	instance, err := app.NewApp(Logger, &cfg)
	if err != nil {
		return "", nil, fmt.Errorf("can't create kirby instance: %w", err)
	}

	go func() {
		err := instance.Start()
		if err != nil {
			Logger.Error("kirby start fail", log.Error(err))
		}
	}()

	kirbyURL := fmt.Sprintf("http://localhost:%d", kirbyPort)
	httpc := resty.New().SetBaseURL(kirbyURL)

	retrier := retry.New(retry.WithAttempts(10), retry.WithBackOff(backoff.NewFixed(2*time.Second)))
	err = retrier.TryNotify(
		context.Background(),
		func(_ context.Context) error {
			rsp, err := httpc.R().Get("/ping/readiness")
			if err != nil {
				return err
			}

			if !rsp.IsSuccess() {
				return fmt.Errorf("non-success status: %s", rsp.Status())
			}

			if !bytes.Equal(rsp.Body(), []byte(`ok`)) {
				return fmt.Errorf("unknown response: %s", rsp.Body())
			}
			return nil
		},
		func(err error, delay time.Duration) {
			Logger.Error("check Kirby fail", log.Error(err), log.Duration("delay", delay))
		},
	)

	closer := func() {
		_ = instance.Shutdown(context.Background())
	}

	if err != nil {
		closer()
		return "", nil, err
	}

	return kirbyURL, closer, nil
}

func getFreePort() (int, error) {
	addr, err := net.ResolveTCPAddr("tcp", "localhost:0")
	if err != nil {
		return 0, err
	}

	l, err := net.ListenTCP("tcp", addr)
	if err != nil {
		return 0, err
	}
	defer func() { _ = l.Close() }()

	return l.Addr().(*net.TCPAddr).Port, nil
}
