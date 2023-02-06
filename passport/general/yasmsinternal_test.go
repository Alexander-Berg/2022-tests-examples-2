package yasmsinternal

import (
	"net/http/httptest"
	"testing"

	"github.com/labstack/echo/v4"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/passport/infra/daemons/yasms_internal/internal/model"
)

type getRequestWithMulti struct {
	ChangeIDs []model.EntityID `query:"change_id" query_multi:"true"`

	Simple                 string           `query:"simple"`
	SimpleWithMulti        string           `query:"simple_with_multi" query_multi:"true"`
	ArrayWithoutMulti      []model.EntityID `query:"array_without_multi" query_multi:"false"`
	ArrayWithoutMultiNoTag []model.EntityID `query:"array_without_multi_no_tag"`
}

func TestValidate_TestCustomBinder(t *testing.T) {
	server := echo.New()
	server.Binder = &BinderWithMultiQueryParam{}

	ctx := server.AcquireContext()

	query := "https://localhost?change_id=1,2&change_id=3&change_id=4,5&simple=1,2&simple_with_multi=1,2&array_without_multi=1,2&array_without_multi=3&array_without_multi_no_tag=1,2"
	ctx.SetRequest(httptest.NewRequest("GET", query, nil))
	params := getRequestWithMulti{}
	err := ctx.Bind(&params)
	require.NoError(t, err)
	require.Equal(t, []model.EntityID{"1", "2", "3", "4", "5"}, params.ChangeIDs)
	require.Equal(t, "1,2", params.Simple)
	require.Equal(t, "1,2", params.SimpleWithMulti)
	require.Equal(t, []model.EntityID{"1,2", "3"}, params.ArrayWithoutMulti)
	require.Equal(t, []model.EntityID{"1,2"}, params.ArrayWithoutMultiNoTag)

	server.ReleaseContext(ctx)
}
