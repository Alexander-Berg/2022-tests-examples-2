package krl

import (
	"context"
	"crypto/md5"
	"crypto/tls"
	"encoding/hex"
	"errors"
	"fmt"
	"io"
	"strconv"
	"sync"
	"time"

	"github.com/go-resty/resty/v2"
	"github.com/klauspost/compress/zstd"
	"github.com/stripe/krl"
	"golang.org/x/crypto/ssh"

	"a.yandex-team.ru/library/go/certifi"
	"a.yandex-team.ru/library/go/core/log"
)

const (
	batchTick = 10 * time.Minute
)

type KRL struct {
	httpc     *resty.Client
	zstd      *zstd.Decoder
	krl       *krl.KRL
	mu        sync.RWMutex
	l         log.Logger
	ctx       context.Context
	cancelCtx context.CancelFunc
	closed    chan struct{}
}

func NewKRL(l log.Logger) (*KRL, error) {
	certPool, err := certifi.NewCertPool()
	if err != nil {
		return nil, fmt.Errorf("can't create ca pool: %w", err)
	}

	zstdDec, err := zstd.NewReader(nil, zstd.WithDecoderConcurrency(1))
	if err != nil {
		return nil, fmt.Errorf("can't create zstd decoder: %w", err)
	}

	httpc := resty.New().
		SetTLSClientConfig(&tls.Config{RootCAs: certPool}).
		SetJSONEscapeHTML(false).
		SetBaseURL("https://skotty.sec.yandex-team.ru").
		SetRetryCount(3).
		SetDoNotParseResponse(true).
		SetRetryWaitTime(1 * time.Second).
		SetRetryMaxWaitTime(10 * time.Second)

	ctx, cancelCtx := context.WithCancel(context.Background())

	krl := &KRL{
		httpc:     httpc,
		zstd:      zstdDec,
		ctx:       ctx,
		cancelCtx: cancelCtx,
		closed:    make(chan struct{}),
		l:         l.WithName("krl_sync"),
	}

	if err := krl.Sync(); err != nil {
		return nil, fmt.Errorf("sync fail: %w", err)
	}

	go krl.loop()
	return krl, nil
}

func (k *KRL) loop() {
	defer close(k.closed)

	t := time.NewTicker(batchTick)
	defer t.Stop()

	for {
		select {
		case <-k.ctx.Done():
			return
		case <-t.C:
		}

		if err := k.Sync(); err != nil {
			k.l.Error("sync fail", log.Error(err))
		}
	}
}

func (k *KRL) IsRevoked(key ssh.PublicKey) bool {
	k.mu.RLock()
	defer k.mu.RUnlock()

	if k.krl == nil {
		return false
	}
	return k.krl.IsRevoked(key)
}

func (k *KRL) Sync() error {
	rsp, err := k.httpc.R().Get("/api/v1/ca/krl/all.zst")
	if err != nil {
		return err
	}

	body := rsp.RawBody()
	defer func() {
		_, _ = io.CopyN(io.Discard, body, 128<<10)
		_ = body.Close()
	}()

	if !rsp.IsSuccess() {
		return fmt.Errorf("non-200 status code: %d", rsp.StatusCode())
	}

	if rsp.Header().Get("Content-Type") != "application/krl+zst" {
		return fmt.Errorf("unexpected content-type header: %s", rsp.Header().Get("Content-Type"))
	}

	expectedHash := rsp.Header().Get("Etag")
	if expectedHash == "" {
		return errors.New("no ETag header returned")
	}

	if expectedHash[0] == '"' {
		expectedHash, err = strconv.Unquote(expectedHash)
		if err != nil {
			return fmt.Errorf("invalid ETag header: %s: %w", rsp.Header().Get("Etag"), err)
		}
	}

	krlBytes, err := io.ReadAll(body)
	if err != nil {
		return fmt.Errorf("read: %w", err)
	}

	md5Hash := md5.Sum(krlBytes)
	actualHash := hex.EncodeToString(md5Hash[:])
	if expectedHash != actualHash {
		return fmt.Errorf("hash mismatch: %s (expected) != %s (actual)", expectedHash, actualHash)
	}

	krlBytes, err = k.zstd.DecodeAll(krlBytes, nil)
	if err != nil {
		return fmt.Errorf("decode: %w", err)
	}

	parsedKRL, err := krl.ParseKRL(krlBytes)
	if err != nil {
		return fmt.Errorf("parse: %w", err)
	}

	k.mu.Lock()
	defer k.mu.Unlock()
	k.krl = parsedKRL
	return nil
}

func (k *KRL) Shutdown(ctx context.Context) {
	k.cancelCtx()

	select {
	case <-k.closed:
	case <-ctx.Done():
	}
}
