package tests

import (
	"flag"
	"net/url"
	"strings"

	"github.com/stretchr/testify/require"
	"github.com/stretchr/testify/suite"
)

var hostFlag = flag.String("host", "", "Host to run tests (required)")

type CommonSuite struct {
	suite.Suite
	host string
}

func (suite *CommonSuite) SetupSuite() {
	require.NotEmpty(suite.T(), *hostFlag)
	suite.host = *hostFlag
}

func (suite *CommonSuite) GetURL() URL {
	return NewURL(suite.host)
}

type URL struct {
	host string
	path string

	cgiArgs url.Values
}

func NewURL(host string) URL {
	return URL{
		host:    host,
		cgiArgs: make(url.Values),
	}
}

func (u *URL) WithTLD(tld string) *URL {
	var parts = strings.Split(u.host, ".")
	parts[len(parts)-1] = tld
	u.host = strings.Join(parts, ".")
	return u
}

func (u *URL) WithPath(path string) *URL {
	u.SetPath(path)
	return u
}

func (u *URL) SetPath(path string) {
	u.path = path
}

func (u *URL) SetCgiArgs(args url.Values) {
	u.cgiArgs = args
}

func (u *URL) WithCGIArg(k, v string) *URL {
	u.AddCGIArg(k, v)
	return u
}

func (u *URL) AddCGIArg(k, v string) {
	u.cgiArgs.Add(k, v)
}

func (u *URL) String() string {
	return u.NetURL().String()
}

func (u *URL) NetURL() *url.URL {
	var netURL url.URL
	netURL.Host = u.host
	netURL.Path = u.path
	netURL.Scheme = "https"

	netURL.RawQuery = u.cgiArgs.Encode()

	return &netURL
}
