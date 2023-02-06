package staff

import (
	"context"
	"crypto/tls"
	"fmt"
	"net/http"
	"time"

	"github.com/go-resty/resty/v2"

	"a.yandex-team.ru/library/go/certifi"
)

const (
	DefaultUpstream = "https://staff-api.yandex-team.ru"
)

type Client struct {
	httpc *resty.Client
}

func NewClient(opts ...Option) (*Client, error) {
	certPool, err := certifi.NewCertPool()
	if err != nil {
		return nil, fmt.Errorf("can't create ca pool: %w", err)
	}

	httpc := resty.New().
		SetTLSClientConfig(&tls.Config{RootCAs: certPool}).
		SetJSONEscapeHTML(false).
		SetHeader("Content-Type", "application/json").
		SetBaseURL(DefaultUpstream).
		SetRetryCount(3).
		SetRetryWaitTime(100 * time.Millisecond).
		SetRetryMaxWaitTime(3 * time.Second).
		AddRetryCondition(func(rsp *resty.Response, err error) bool {
			return err != nil || rsp.StatusCode() == http.StatusInternalServerError
		})

	c := &Client{httpc: httpc}
	for _, o := range opts {
		o(c)
	}

	return c, nil
}

func (c *Client) UserKeys(ctx context.Context, login string) ([]Key, error) {
	var result struct {
		Login string
		Keys  []Key
	}

	var errResult staffErrResult
	rsp, err := c.httpc.R().
		SetContext(ctx).
		SetResult(&result).
		SetError(&errResult).
		ForceContentType("application/json").
		SetQueryParams(map[string]string{
			"login":   login,
			"_one":    "1",
			"_fields": "login,keys.fingerprint_sha256",
		}).
		Get("/v3/persons")

	if err != nil {
		return nil, fmt.Errorf("request failed: %w", err)
	}

	if errResult.Msg != "" {
		return nil, fmt.Errorf("remote error: %s", errResult.Msg)
	}

	if !rsp.IsSuccess() {
		return nil, fmt.Errorf("request failed: non-200 status code: %s", rsp.Status())
	}

	if result.Login != login {
		return nil, fmt.Errorf("unexpected login received %s (expectd:%s)", result.Login, login)
	}

	return result.Keys, nil
}
