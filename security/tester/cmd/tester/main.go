package main

import (
	"context"
	"flag"
	"fmt"
	"os"
	"os/signal"
	"syscall"
	"time"

	"a.yandex-team.ru/library/go/core/log"
	"a.yandex-team.ru/library/go/core/log/zap"
	"a.yandex-team.ru/security/skotty/tester/internal/app"
	"a.yandex-team.ru/security/skotty/tester/internal/staff"
)

func fatalf(format string, args ...interface{}) {
	_, _ = fmt.Fprintf(os.Stderr, format+"\n", args...)
	os.Exit(1)
}

func main() {
	var addr string
	flag.StringVar(&addr, "addr", ":9022", "addr to listen on")
	flag.Parse()

	logger, err := zap.NewDeployLogger(log.InfoLevel)
	if err != nil {
		fatalf("failed to create logger: %v", err)
	}

	staffc, err := staff.NewClient(staff.WithAuthToken(os.Getenv("STAFF_TOKEN")))
	if err != nil {
		fatalf("failed to create staff client: %v", err)
	}

	sshApp := app.NewApp(app.WithLogger(logger), app.WithStaffClient(staffc))
	errChan := make(chan error, 1)
	okChan := make(chan struct{}, 1)
	go func() {
		if err := sshApp.ListenAndServe(addr); err != nil {
			errChan <- err
		} else {
			okChan <- struct{}{}
		}
	}()

	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)
	defer logger.Info("stopped")

	select {
	case <-sigChan:
		logger.Info("shutting down gracefully by signal")

		ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
		defer cancel()

		sshApp.Shutdown(ctx)
	case <-okChan:
	case err := <-errChan:
		logger.Error("failed to start ssh app", log.Error(err))
	}
}
