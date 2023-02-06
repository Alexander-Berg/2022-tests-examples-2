package trigger_test

import (
	"context"
	"net/http"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/core/log"
	"a.yandex-team.ru/library/go/core/log/zap"
	"a.yandex-team.ru/library/go/ptr"
	"a.yandex-team.ru/noc/cmdb/pkg/cmdbapi"
	"a.yandex-team.ru/noc/cmdb/pkg/cmdbapitest"
	"a.yandex-team.ru/noc/cmdb/pkg/cmdbclient"
	"a.yandex-team.ru/noc/cmdb/pkg/dbconn"
	"a.yandex-team.ru/noc/cmdb/pkg/mur"
	"a.yandex-team.ru/noc/cmdb/pkg/types"
	"a.yandex-team.ru/strm/common/go/pkg/fn"
)

func TestCheckSingleActualServiceDescriptionPerService(t *testing.T) {

	dbURI := cmdbapitest.DBURI()

	lg, _ := zap.New(zap.ConsoleConfig(log.DebugLevel))
	logger := fn.NewLogger(lg)
	db, err := dbconn.Database{
		URIRW:  dbURI,
		Logger: logger,
	}.Open()
	require.NoError(t, err)

	ctx := context.TODO()
	_, client, cmdbServer := cmdbapitest.NewRouter(t, db, logger)

	contact := cmdbServer.Contacts.PostContact(t, GetContact())

	operator := GetOperator()
	cmdbServer.Operators.PostOperator(t, operator)

	contract, err := client.Documents.Post(ctx, GetContract(operator, contact))
	require.NoError(t, err)

	orderForm, err := client.Documents.Post(ctx, GetOrderForm(contract, contact))
	require.NoError(t, err)

	service := GetService(operator)
	cmdbServer.Services.PostService(t, service)

	location, err := client.Locations.Post(ctx, &cmdbapi.LocationIn{Name: "m9"})
	require.NoError(t, err)
	link, err := client.Links.Post(ctx, cmdbapitest.NewLinkIn(&location.ID))
	require.NoError(t, err)

	_, err = client.ServiceDescriptions.Post(ctx, &cmdbapi.ServiceDescriptionNestedIn{
		ID:                             nil,
		Details:                        "description 1",
		ContactID:                      contact.ID,
		OperatorID:                     operator.ID,
		ParentDocumentID:               orderForm.ID,
		Service:                        &cmdbapi.ServiceIn{ID: service.ID},
		LinkInternalID:                 &link.InternalID,
		CanceledByServiceDescriptionID: nil,
	})
	require.NoError(t, err)

	msg := "ERROR: duplicate key value violates unique constraint \"single_actual_service_description_per_service\" (SQLSTATE 23505)"
	_, err = client.ServiceDescriptions.Post(ctx, &cmdbapi.ServiceDescriptionNestedIn{
		ID:                             nil,
		Details:                        "description 2",
		ContactID:                      contact.ID,
		OperatorID:                     operator.ID,
		ParentDocumentID:               orderForm.ID,
		Service:                        &cmdbapi.ServiceIn{ID: service.ID},
		LinkInternalID:                 &link.InternalID,
		CanceledByServiceDescriptionID: nil,
	})
	cmdbapitest.RequireError(t, cmdbclient.Error{
		StatusCode: http.StatusInternalServerError,
		Err:        mur.NewError(msg, msg),
	}, err)

	orderForm2, err := client.Documents.Post(ctx, GetOrderForm2(contract, contact))
	require.NoError(t, err)

	msg2 := "ERROR: duplicate key value violates unique constraint \"single_actual_service_description_per_service\" (SQLSTATE 23505)"
	_, err = client.ServiceDescriptions.Post(ctx, &cmdbapi.ServiceDescriptionNestedIn{
		ID:                             nil,
		Details:                        "description 3",
		ContactID:                      contact.ID,
		OperatorID:                     operator.ID,
		ParentDocumentID:               orderForm2.ID,
		Service:                        &cmdbapi.ServiceIn{ID: service.ID},
		LinkInternalID:                 &link.InternalID,
		CanceledByServiceDescriptionID: nil,
	})
	cmdbapitest.RequireError(t, cmdbclient.Error{
		StatusCode: http.StatusInternalServerError,
		Err:        mur.NewError(msg2, msg2),
	}, err)
}

func GetContact() cmdbapi.ContactIn {
	return cmdbapi.ContactIn{
		ID:             (*types.ContactID)(ptr.Int64(15)),
		Name:           "Первая линия поддержки Ростелеком",
		Details:        "+7(999)111-22-33",
		EmailForRobots: "for_robots@rostelekom.ru",
	}
}

func GetOperator() cmdbapi.Operator {
	return cmdbapi.Operator{
		ID:               (*types.OperatorID)(ptr.Int64(7)),
		Name:             "Ростелеком",
		Details:          "test",
		DefaultContactID: (*types.ContactID)(ptr.Int64(15)),
	}
}

func GetContract(operator cmdbapi.Operator, contact *cmdbapi.ContactOut) cmdbapi.Document {
	return cmdbapi.Document{
		ID:               (*types.DocumentID)(ptr.Int64(15)),
		Name:             "Договор",
		Details:          "test",
		DefaultContactID: &contact.ID,
		DocumentType:     types.DocumentTypeContract,
		OperatorID:       *operator.ID,
		ParentDocumentID: nil,
	}
}

func GetOrderForm(contract cmdbapi.Document, contact *cmdbapi.ContactOut) cmdbapi.Document {
	return cmdbapi.Document{
		ID:               (*types.DocumentID)(ptr.Int64(29)),
		Name:             "Бланк заказа",
		Details:          "Список услуг 1",
		DefaultContactID: &contact.ID,
		DocumentType:     types.DocumentTypeOrderForm,
		OperatorID:       contract.OperatorID,
		ParentDocumentID: contract.ID,
	}
}

func GetService(o cmdbapi.Operator) cmdbapi.ServiceIn {
	return cmdbapi.ServiceIn{
		ID:         (*types.ServiceID)(ptr.Int64(41)),
		VisibleID:  "827366",
		OperatorID: o.ID,
	}
}

func GetOrderForm2(contract cmdbapi.Document, contact *cmdbapi.ContactOut) cmdbapi.Document {
	return cmdbapi.Document{
		ID:               (*types.DocumentID)(ptr.Int64(129)),
		Name:             "Бланк заказа 2",
		Details:          "Список услуг 2",
		DefaultContactID: &contact.ID,
		DocumentType:     types.DocumentTypeOrderForm,
		OperatorID:       contract.OperatorID,
		ParentDocumentID: contract.ID,
	}
}
