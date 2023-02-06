package hbaseapi

import (
	"os"
	"testing"

	"github.com/jarcoal/httpmock"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/passport/infra/daemons/historydb_api2/internal/reqs"
)

var testClient *Client

func TestMain(m *testing.M) {
	testClient = newTestClient()

	httpmock.ActivateNonDefault(testClient.http.GetClient())
	defer httpmock.DeactivateAndReset()

	os.Exit(m.Run())
}

func TestClient_getEventsOrderBy(t *testing.T) {
	res, err := getOrderByParam(reqs.OrderByDesc)
	require.NoError(t, err)
	require.Equal(t, "desc", res)

	res, err = getOrderByParam(reqs.OrderByAsc)
	require.NoError(t, err)
	require.Equal(t, "asc", res)

	_, err = getOrderByParam(-1)
	require.Error(t, err)
}
