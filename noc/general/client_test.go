package racktables

import (
	"context"
	"errors"
	"io"
	"net"
	"net/http"
	"net/http/httptest"
	"net/textproto"
	"net/url"
	"strings"
	"testing"

	"github.com/stretchr/testify/suite"
	"go.uber.org/zap/zaptest"

	"a.yandex-team.ru/library/go/core/log"
	"a.yandex-team.ru/library/go/core/log/zap"
)

var (
	canonicalAuthorizationHeader = textproto.CanonicalMIMEHeaderKey("Authorization")
)

type baseClientTestSuite struct {
	suite.Suite
}

func (suite *baseClientTestSuite) makeTestServer(handlerFunc http.HandlerFunc) *httptest.Server {
	return httptest.NewServer(handlerFunc)
}

func (suite *baseClientTestSuite) makeTestClient(url string) Client {
	logger := &zap.Logger{L: zaptest.NewLogger(suite.T())}
	client, err := NewClient(
		&Config{URL: url},
		logger,
	)
	suite.Require().NoError(err)
	logger.Debug("create client", log.String("url", url))
	return client
}

type ClientListObjectsTestSuite struct {
	baseClientTestSuite
}

func TestClientListObjectsTestSuite(t *testing.T) {
	suite.Run(t, new(ClientListObjectsTestSuite))
}

func (suite *ClientListObjectsTestSuite) TestRequestError() {
	ts := suite.makeTestServer(func(w http.ResponseWriter, r *http.Request) {})
	defer ts.Close()
	client := suite.makeTestClient(ts.URL)

	ctx, cancel := context.WithCancel(context.Background())
	cancel()

	hosts, err := client.ListObjects(ctx, nil)

	suite.Require().True(errors.Is(err, context.Canceled), err.Error())
	suite.Require().Nil(hosts)
}

func (suite *ClientListObjectsTestSuite) TestResponseBodyError() {
	ts := suite.makeTestServer(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Length", "1")
	})
	defer ts.Close()
	client := suite.makeTestClient(ts.URL)

	hosts, err := client.ListObjects(context.Background(), nil)

	suite.Require().True(errors.Is(err, io.ErrUnexpectedEOF), err.Error())
	suite.Require().Nil(hosts)
}

func (suite *ClientListObjectsTestSuite) TestBadResponseCodeError() {
	ts := suite.makeTestServer(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusInternalServerError)
	})
	defer ts.Close()
	client := suite.makeTestClient(ts.URL)

	hosts, err := client.ListObjects(context.Background(), nil)

	suite.Require().Error(err)
	suite.Require().Nil(hosts)
}

func (suite *ClientListObjectsTestSuite) TestSuccessEmpty() {
	ts := suite.makeTestServer(func(w http.ResponseWriter, r *http.Request) {
		suite.Assert().Equal(allObjectsPath, r.URL.Path)
		suite.Assert().NotContains(r.Header, canonicalAuthorizationHeader)
	})
	defer ts.Close()
	client := suite.makeTestClient(ts.URL)

	hosts, err := client.ListObjects(context.Background(), nil)

	suite.Require().NoError(err)
	suite.Require().Empty(hosts)
}

func (suite *ClientListObjectsTestSuite) TestSuccessMultipleHosts() {
	var multipleHostsListResult = []string{
		"iva-lb0.yndx.net",
		"myt-lb0.yndx.net",
	}
	ts := suite.makeTestServer(func(w http.ResponseWriter, r *http.Request) {
		_, _ = w.Write([]byte(strings.Join(multipleHostsListResult, "\n") + "\n"))
	})
	defer ts.Close()
	client := suite.makeTestClient(ts.URL)

	hosts, err := client.ListObjects(context.Background(), nil)

	suite.Require().NoError(err)
	suite.Require().EqualValues(multipleHostsListResult, hosts)
}

type ListNetworksPerDCAggTestSuite struct {
	baseClientTestSuite
}

func (suite *ListNetworksPerDCAggTestSuite) TestRequestError() {
	ts := suite.makeTestServer(func(w http.ResponseWriter, r *http.Request) {})
	defer ts.Close()
	client := suite.makeTestClient(ts.URL)

	ctx, cancel := context.WithCancel(context.Background())
	cancel()

	networks, err := client.ListNetworksPerDCAgg(ctx)

	suite.Require().True(errors.Is(err, context.Canceled), err.Error())
	suite.Require().Nil(networks)
}

func (suite *ListNetworksPerDCAggTestSuite) TestResponseBodyError() {
	ts := suite.makeTestServer(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Length", "1")
	})
	defer ts.Close()
	client := suite.makeTestClient(ts.URL)

	networks, err := client.ListNetworksPerDCAgg(context.Background())

	suite.Require().True(errors.Is(err, io.ErrUnexpectedEOF), err.Error())
	suite.Require().Nil(networks)
}

func (suite *ListNetworksPerDCAggTestSuite) TestBadResponseCodeError() {
	ts := suite.makeTestServer(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusInternalServerError)
	})
	defer ts.Close()
	client := suite.makeTestClient(ts.URL)

	networks, err := client.ListNetworksPerDCAgg(context.Background())

	suite.Require().Error(err)
	suite.Require().Nil(networks)
}

func (suite *ListNetworksPerDCAggTestSuite) TestSuccessEmpty() {
	ts := suite.makeTestServer(func(w http.ResponseWriter, r *http.Request) {
		suite.Assert().Equal(networkListPath, r.URL.Path)
		suite.Assert().NotContains(r.Header, canonicalAuthorizationHeader)
		_, err := w.Write([]byte("[]"))
		suite.Assert().NoError(err)
	})
	defer ts.Close()
	client := suite.makeTestClient(ts.URL)

	networks, err := client.ListNetworksPerDCAgg(context.Background())

	suite.Require().NoError(err)
	suite.Require().Empty(networks)
}

func (suite *ListNetworksPerDCAggTestSuite) TestSuccessMultipleHosts() {
	_, net1, err := net.ParseCIDR("1.2.3.4/24")
	suite.Require().NoError(err)

	_, net2, err := net.ParseCIDR("5.6.7.8/24")
	suite.Require().NoError(err)
	expectedNetworks := []PerDCAggNetwork{
		{
			Network:  net1,
			Location: "Сасово",
			Scope:    NetworkScopeBackbone,
		},
		{
			Network:  net2,
			Location: "Мытищи",
			Scope:    NetworkScopeFastbone,
		},
	}
	ts := suite.makeTestServer(func(w http.ResponseWriter, r *http.Request) {
		jsonData := []byte(`
[
	{
		"network": "1.2.3.4/24",
		"location": "Сасово",
		"scope": "backbone"
	},
	{
		"network": "5.6.7.8/24",
		"location": "Мытищи",
		"scope": "fastbone"
	}
]
`)
		_, err := w.Write(jsonData)
		suite.Assert().NoError(err)
	})
	defer ts.Close()
	client := suite.makeTestClient(ts.URL)

	networks, err := client.ListNetworksPerDCAgg(context.Background())

	suite.Require().NoError(err)
	suite.Require().EqualValues(expectedNetworks, networks)
}

func (suite *ListNetworksPerDCAggTestSuite) TestInvalidIPNet() {
	ts := suite.makeTestServer(func(w http.ResponseWriter, r *http.Request) {
		jsonData := []byte(`
[
	{
		"network": "1.2.3.4",
		"location": "Сасово",
		"scope": "backbone"
	}
]
`)
		_, err := w.Write(jsonData)
		suite.Assert().NoError(err)
	})
	defer ts.Close()
	client := suite.makeTestClient(ts.URL)

	networks, err := client.ListNetworksPerDCAgg(context.Background())

	var expectedErr *net.ParseError
	suite.Require().True(errors.As(err, &expectedErr))
	suite.Require().Empty(networks)
}

func TestListNetworksPerDCAgg(t *testing.T) {
	suite.Run(t, new(ListNetworksPerDCAggTestSuite))
}

type NewClientValidationTestSuite struct {
	suite.Suite
}

func TestNewClientValidationTestSuite(t *testing.T) {
	suite.Run(t, new(NewClientValidationTestSuite))
}

func (suite *NewClientValidationTestSuite) TestInvalidURL() {
	client, err := NewClient(
		&Config{
			URL: "://badurl/",
		},
		&zap.Logger{L: zaptest.NewLogger(suite.T())},
	)
	var urlError *url.Error
	suite.Require().True(errors.As(err, &urlError))
	suite.Require().Nil(client)
}
