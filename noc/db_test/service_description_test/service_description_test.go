package trigger_test

import (
	"context"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/core/log"
	"a.yandex-team.ru/library/go/core/log/zap"
	"a.yandex-team.ru/noc/cmdb/pkg/cmdbapi"
	"a.yandex-team.ru/noc/cmdb/pkg/cmdbapitest"
	"a.yandex-team.ru/noc/cmdb/pkg/dbconn"
	"a.yandex-team.ru/noc/cmdb/pkg/types"
	"a.yandex-team.ru/strm/common/go/pkg/fn"
)

func TestDocumentWizard(t *testing.T) {

	dbURI := cmdbapitest.DBURI()

	lg, _ := zap.New(zap.ConsoleConfig(log.DebugLevel))
	logger := fn.NewLogger(lg)
	db, err := dbconn.Database{
		URIRW:  dbURI,
		Logger: logger,
	}.Open()
	require.NoError(t, err)

	server, client, cmdbServer := cmdbapitest.NewRouter(t, db, logger)
	ctx := context.TODO()
	contact, err := client.Contacts.Post(ctx, &cmdbapi.ContactIn{Name: "контакт"})
	require.NoError(t, err)
	operator, err := client.Operators.Post(ctx, &cmdbapi.Operator{Name: "оператор"})
	require.NoError(t, err)
	server.Post(t, server.URL+"/api/service_descriptions", cmdbapi.ServiceDescriptionNestedIn{
		ID:                             nil,
		Details:                        "детали описания услуги",
		ContactID:                      contact.ID,
		OperatorID:                     operator.ID,
		ParentDocumentID:               nil,
		Service:                        &cmdbapi.ServiceIn{VisibleID: "услуга"},
		CanceledByServiceDescriptionID: nil,
	})
	cmdbServer.ServiceDescriptions.GetServiceDescriptions(t, []cmdbapi.ServiceDescriptionNestedOut{{
		ID:                             1,
		Details:                        "детали описания услуги",
		Operator:                       cmdbapi.OperatorShortOut{ID: *operator.ID, Name: "оператор"},
		Contact:                        cmdbapi.ContactOut{ID: contact.ID, Name: "контакт"},
		Service:                        &cmdbapi.ServiceOut{ID: 1, VisibleID: "услуга", OperatorID: *operator.ID},
		LinkID:                         nil,
		Location:                       nil,
		CanceledByServiceDescriptionID: nil,
		OperatorID:                     *operator.ID,
		ParentDocumentID:               nil,
		LocationID:                     nil,
	}})
	serviceID := (types.ServiceID)(1)
	cmdbServer.Services.GetServices(t, []cmdbapi.ServiceExt{{
		ServiceOut: cmdbapi.ServiceOut{
			ID:         serviceID,
			VisibleID:  "услуга",
			OperatorID: *operator.ID,
		},
		OperatorName: "оператор",
		Details:      "детали описания услуги",
	}})
}
