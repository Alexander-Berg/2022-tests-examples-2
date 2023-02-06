package macros

import (
	"net"
	"testing"

	"github.com/stretchr/testify/require"
)

func TestExtractProjectID(t *testing.T) {
	ipStr := "2a02:6b8:c03:500:0:f803:0:212"
	ip := net.ParseIP(ipStr)
	require.NotNil(t, ip)

	projectID, err := ExtractProjectID(ip)
	require.Nil(t, err)

	require.Equal(t, ProjectID(0xf803), *projectID)
}
