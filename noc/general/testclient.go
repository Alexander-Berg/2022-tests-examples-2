package tvmhelper

import (
	"context"
	"errors"
	"fmt"
	"io/ioutil"
	"os"
	"strconv"
	"strings"
	"testing"

	"a.yandex-team.ru/library/go/core/log"
	"a.yandex-team.ru/library/go/core/log/zap"
	"a.yandex-team.ru/library/go/core/xerrors"
	"a.yandex-team.ru/library/go/yandex/tvm"
	"a.yandex-team.ru/library/go/yandex/tvm/tvmtool"
)

const (
	tvmToolPortFile      = "tvmtool.port"
	tvmToolAuthTokenFile = "tvmtool.authtoken" //#nosec
)

func NewTestClient(t *testing.T, src string) tvm.Client {
	t.Helper()

	if _, isYaMake := os.LookupEnv("YA_MAKE_TEST_RUN"); isYaMake {
		return newYaMakeTestClient(t, src)
	}
	return newGoBuildTestClient(t, src)
}

// newYaMakeTestClient возвращает клиент к тестовому tvmtool из аркадийного рецепта
// https://a.yandex-team.ru/arc/trunk/arcadia/library/recipes/tvmtool .
func newYaMakeTestClient(t *testing.T, src string) *tvmtool.Client {
	t.Helper()

	raw, err := ioutil.ReadFile(tvmToolPortFile)
	if err != nil {
		t.Fatalf(err.Error())
	}

	port, err := strconv.Atoi(string(raw))
	if err != nil {
		t.Fatalf(err.Error())
	}

	var auth string
	raw, err = ioutil.ReadFile(tvmToolAuthTokenFile)
	if err != nil {
		t.Fatalf(err.Error())
	}
	auth = string(raw)

	zlog, err := zap.New(zap.ConsoleConfig(log.DebugLevel))
	if err != nil {
		t.Fatalf(err.Error())
	}

	client, err := tvmtool.NewClient(
		fmt.Sprintf("http://localhost:%d", port),
		tvmtool.WithAuthToken(auth),
		tvmtool.WithCacheEnabled(false),
		tvmtool.WithSrc(src),
		tvmtool.WithLogger(zlog),
	)
	if err != nil {
		t.Fatalf(err.Error())
	}

	return client
}

// newGoBuildTestClient моковый клиент для тестов без ya make (чистый go).
func newGoBuildTestClient(t *testing.T, src string) *FakeTVMToolClient {
	t.Helper()

	// NOTE: лучше парсить tvmtool.conf, чтобы уменьшить не повторять маппинг alias->id
	aliases := map[string]tvm.ClientID{
		"testClient":                 42,
		"testClientOnlyMakeRequests": 43,
		"testServer":                 100500,
	}

	selfID, ok := aliases[src]
	if !ok {
		panic("alias not found")
	}

	return &FakeTVMToolClient{selfID: selfID, aliases: aliases}
}

type FakeTVMToolClient struct {
	selfID  tvm.ClientID
	aliases map[string]tvm.ClientID
}

var (
	errNotSupported  = errors.New("not supported")
	errAliasNotFound = errors.New("alias not found")
)

func (c *FakeTVMToolClient) GetServiceTicketForAlias(ctx context.Context, alias string) (string, error) {
	dstID, ok := c.aliases[alias]
	if !ok {
		return "", errAliasNotFound
	}
	return fmt.Sprintf("%v %v", c.selfID, dstID), nil
}

func (c *FakeTVMToolClient) GetServiceTicketForID(ctx context.Context, dstID tvm.ClientID) (string, error) {
	return fmt.Sprintf("%v %v", c.selfID, dstID), nil
}

func (c *FakeTVMToolClient) CheckServiceTicket(ctx context.Context, ticket string) (*tvm.CheckedServiceTicket, error) {
	parts := strings.Fields(ticket)
	if len(parts) != 2 {
		return nil, xerrors.Errorf("invalid service ticket: invalid parts: %v", ticket)
	}

	srcID, err := strconv.Atoi(parts[0])
	if err != nil {
		return nil, xerrors.Errorf("invalid service ticket: src int: %v", ticket)
	}

	dstID, err := strconv.Atoi(parts[1])
	if err != nil {
		return nil, xerrors.Errorf("invalid service ticket: dst int: %v", ticket)
	}

	if tvm.ClientID(dstID) != c.selfID {
		return nil, xerrors.Errorf("expected dstID %v, but found %v", c.selfID, dstID)
	}

	return &tvm.CheckedServiceTicket{SrcID: tvm.ClientID(srcID)}, nil
}

func (c *FakeTVMToolClient) CheckUserTicket(ctx context.Context, ticket string, opts ...tvm.CheckUserTicketOption) (*tvm.CheckedUserTicket, error) {
	return nil, errNotSupported
}

func (c *FakeTVMToolClient) GetRoles(ctx context.Context) (*tvm.Roles, error) {
	return nil, errNotSupported
}

func (c *FakeTVMToolClient) GetStatus(ctx context.Context) (tvm.ClientStatusInfo, error) {
	return tvm.ClientStatusInfo{}, errNotSupported
}
