package trigger_test

import (
	"context"
	"net/http"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/core/log"
	"a.yandex-team.ru/library/go/core/log/zap"
	"a.yandex-team.ru/noc/cmdb/pkg/cmdbapi"
	"a.yandex-team.ru/noc/cmdb/pkg/cmdbapitest"
	"a.yandex-team.ru/noc/cmdb/pkg/cmdbclient"
	"a.yandex-team.ru/noc/cmdb/pkg/dbconn"
	"a.yandex-team.ru/noc/cmdb/pkg/mur"
	"a.yandex-team.ru/strm/common/go/pkg/fn"
)

func TestTriggerUniqueServiceVisibleID(t *testing.T) {

	dbURI := cmdbapitest.DBURI()

	lg, _ := zap.New(zap.ConsoleConfig(log.DebugLevel))
	logger := fn.NewLogger(lg)
	db, err := dbconn.Database{
		URIRW:  dbURI,
		Logger: logger,
	}.Open()
	require.NoError(t, err)

	ctx := context.TODO()
	_, client, _ := cmdbapitest.NewRouter(t, db, logger)

	contactIn := &cmdbapi.ContactIn{
		ID:             nil,
		Name:           "Первая линия поддержки Ростелеком",
		Details:        "+7(999)111-22-33",
		EmailForRobots: "for_robots@rostelekom.ru",
	}
	contact, err := client.Contacts.Post(ctx, contactIn)
	require.NoError(t, err)

	operatorIn := &cmdbapi.Operator{
		ID:               nil,
		Name:             "Ростелеком",
		Details:          "test",
		DefaultContactID: &contact.ID,
	}
	operator, err := client.Operators.Post(ctx, operatorIn)
	require.NoError(t, err)

	service1 := cmdbapi.ServiceIn{
		VisibleID:  "id01",
		OperatorID: operator.ID,
	}
	_, err = client.Services.Post(ctx, service1)
	require.NoError(t, err)

	service2 := cmdbapi.ServiceIn{
		VisibleID:  "id01",
		OperatorID: operator.ID,
	}
	msg := "ERROR: duplicate key value violates unique constraint \"services_visible_id_operator_id_uniq\" (SQLSTATE 23505)"
	_, err = client.Services.Post(ctx, service2)
	require.Error(t, err)
	var cerr cmdbclient.Error
	require.ErrorAs(t, err, &cerr)
	assert.Equal(t, cmdbclient.Error{
		URL:        cerr.URL,
		StatusCode: http.StatusBadRequest,
		Err: mur.Error{
			Message: "Operator `Ростелеком` already has service id `id01`",
			Error:   msg,
		},
	}, cerr)
}
