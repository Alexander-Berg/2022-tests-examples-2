package desktop

import (
	"net/http"

	"github.com/stretchr/testify/require"
)

func (suite *DesktopSuite) TestExample() {
	t := suite.T()
	u := suite.GetURL()
	response, err := http.Get(u.String())
	require.NoError(t, err)
	defer response.Body.Close()

	require.Equal(t, http.StatusOK, response.StatusCode)
	// TODO: after apphost would be fixed
	//require.NotEmpty(t, response.Header.Get("X-Yandex-Req-Id"))
}

func (suite *DesktopSuite) TestNTP200() {
	t := suite.T()
	u := suite.GetURL()
	u.SetPath("portal/ntp/refresh_data/")

	response, err := http.Get(u.String())
	require.NoError(t, err)
	defer response.Body.Close()

	require.Equal(t, http.StatusOK, response.StatusCode)
}
