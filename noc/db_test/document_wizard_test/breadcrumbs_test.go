package trigger_test

import (
	"context"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/core/log"
	"a.yandex-team.ru/library/go/core/log/zap"
	"a.yandex-team.ru/library/go/ptr"
	"a.yandex-team.ru/noc/cmdb/pkg/cmdbapi"
	"a.yandex-team.ru/noc/cmdb/pkg/cmdbapitest"
	"a.yandex-team.ru/noc/cmdb/pkg/dbconn"
	"a.yandex-team.ru/noc/cmdb/pkg/types"
	"a.yandex-team.ru/strm/common/go/pkg/fn"
)

func TestBreadcrumbs(t *testing.T) {
	const suffix = " - breadcrumbs"

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

	wizardOut, err := client.DocumentWizard.Post(ctx, cmdbapi.DocumentWizardIn{
		Operator: cmdbapi.Operator{Name: "оператор" + suffix},
		Documents: []cmdbapi.Document{
			{DocumentType: "contract", Name: "договор" + suffix},
			{DocumentType: "order form", Name: "бланк заказа" + suffix},
		},
		ServiceDescription: cmdbapi.ServiceDescriptionTruncated{
			Details: "описание услуги" + suffix,
		},
		Contact: cmdbapi.ContactIn{Name: "контакт" + suffix},
		Service: &cmdbapi.ServiceIn{VisibleID: "услуга" + suffix},
	})
	require.NoError(t, err)

	operator := wizardOut.Operator
	documents := wizardOut.Documents
	service := wizardOut.Service
	serviceDescription := wizardOut.ServiceDescription
	contact := wizardOut.Contact

	require.Equal(t, cmdbapi.Operator{
		ID:               operator.ID,
		Name:             "оператор" + suffix,
		DefaultContactID: &contact.ID,
	}, operator)
	expectedDocument1 := cmdbapi.Document{
		ID:               documents[0].ID,
		Name:             "договор" + suffix,
		DocumentType:     "contract",
		DefaultContactID: &contact.ID,
		OperatorID:       *operator.ID,
	}
	expectedDocument2 := cmdbapi.Document{
		ID:               documents[1].ID,
		Name:             "бланк заказа" + suffix,
		DocumentType:     "order form",
		ParentDocumentID: documents[0].ID,
		DefaultContactID: &contact.ID,
		OperatorID:       *operator.ID,
	}
	require.Equal(t, []cmdbapi.Document{expectedDocument1, expectedDocument2}, documents)
	require.Equal(t, cmdbapi.ServiceDescriptionFlatOut{
		ID:               serviceDescription.ID,
		Details:          "описание услуги" + suffix,
		ParentDocumentID: documents[1].ID,
		OperatorID:       *operator.ID,
		ContactID:        contact.ID,
		ServiceID:        &service.ID,
	}, serviceDescription)
	require.Equal(t, cmdbapi.ContactOut{
		ID:   contact.ID,
		Name: "контакт" + suffix,
	}, contact)
	require.Equal(t, &cmdbapi.ServiceOut{
		ID:         service.ID,
		VisibleID:  "услуга" + suffix,
		OperatorID: *operator.ID,
	}, service)

	_ = cmdbServer.Contacts.GetContact(t, contact.ID,
		cmdbapi.ContactOut{ID: contact.ID, Name: "контакт" + suffix})

	operatorWithBreadcrumbs, err := client.Operators.Get(ctx, *operator.ID)
	require.NoError(t, err)
	require.Equal(t, cmdbapi.OperatorWithBreadcrumbs{
		OperatorExt: cmdbapi.OperatorExt{
			Operator: cmdbapi.Operator{
				ID:               operator.ID,
				Name:             "оператор" + suffix,
				DefaultContactID: &contact.ID,
			},
			DefaultContactName: ptr.String("контакт" + suffix),
		},
		Breadcrumbs: []cmdbapi.Breadcrumb{{
			ID:   types.BreadcrumbOperatorID(*operator.ID),
			Name: "оператор" + suffix,
			Type: types.BreadcrumbOperator,
		}},
	}, *operatorWithBreadcrumbs)

	document1, err := client.Documents.Get(ctx, *documents[0].ID)
	require.NoError(t, err)
	require.Equal(t, cmdbapi.DocumentWithBreadcrumbs{
		Document: expectedDocument1,
		Breadcrumbs: []cmdbapi.Breadcrumb{{
			ID:   types.BreadcrumbOperatorID(*operator.ID),
			Name: "оператор" + suffix,
			Type: types.BreadcrumbOperator,
		}, {
			ID:   types.BreadcrumbDocumentID(*document1.ID),
			Name: "договор" + suffix,
			Type: types.BreadcrumbDocument(document1.DocumentType),
		}},
		DefaultContactName: ptr.String("контакт" + suffix),
	}, document1)

	document2, err := client.Documents.Get(ctx, *documents[1].ID)
	require.NoError(t, err)
	require.Equal(t, cmdbapi.DocumentWithBreadcrumbs{
		Document: expectedDocument2,
		Breadcrumbs: []cmdbapi.Breadcrumb{{
			ID:   types.BreadcrumbOperatorID(*operator.ID),
			Name: "оператор" + suffix,
			Type: types.BreadcrumbOperator,
		}, {
			ID:   types.BreadcrumbDocumentID(*document1.ID),
			Name: "договор" + suffix,
			Type: types.BreadcrumbDocument(document1.DocumentType),
		}, {
			ID:   types.BreadcrumbDocumentID(*document2.ID),
			Name: "бланк заказа" + suffix,
			Type: types.BreadcrumbDocument(document2.DocumentType),
		}},
		DefaultContactName: ptr.String("контакт" + suffix),
	}, document2)

	cmdbServer.Services.GetService(t, service.ID, cmdbapi.ServiceExt{
		ServiceOut:          *service,
		Details:             "описание услуги" + suffix,
		OperatorName:        "оператор" + suffix,
		ActualLinkID:        nil,
		ContractID:          documents[0].ID,
		ContractName:        ptr.String("договор" + suffix),
		ActualOrderFormID:   documents[1].ID,
		ActualOrderFormName: ptr.String("бланк заказа" + suffix),
		Documents: []cmdbapi.DocumentShort{{
			ID:           *documents[0].ID,
			Name:         "договор" + suffix,
			DocumentType: "contract",
		}, {
			ID:           *documents[1].ID,
			Name:         "бланк заказа" + suffix,
			DocumentType: "order form",
		}},
	})
	cmdbServer.ServiceDescriptions.GetServiceDescription(t, serviceDescription.ID, cmdbapi.ServiceDescriptionNestedWithBreadcrumbs{
		ServiceDescriptionNestedOut: cmdbapi.ServiceDescriptionNestedOut{
			ID:                             serviceDescription.ID,
			Details:                        "описание услуги" + suffix,
			Operator:                       cmdbapi.OperatorShortOut{ID: *operator.ID, Name: "оператор" + suffix},
			Contact:                        cmdbapi.ContactOut{ID: contact.ID, Name: "контакт" + suffix},
			Service:                        service,
			LinkInternalID:                 nil,
			LinkID:                         nil,
			Location:                       nil,
			CanceledByServiceDescriptionID: nil,
			ParentDocumentID:               documents[1].ID,
			Link:                           nil,
			ParentDocument: &cmdbapi.DocumentShort{
				ID:           *documents[1].ID,
				Name:         "бланк заказа" + suffix,
				DocumentType: "order form",
			},
			OperatorID: *operator.ID,
			LocationID: nil,
		},
		Breadcrumbs: []cmdbapi.Breadcrumb{{
			ID:   types.BreadcrumbOperatorID(*operator.ID),
			Name: "оператор" + suffix,
			Type: types.BreadcrumbOperator,
		}, {
			ID:   types.BreadcrumbDocumentID(*document1.ID),
			Name: "договор" + suffix,
			Type: types.BreadcrumbDocument(document1.DocumentType),
		}, {
			ID:   types.BreadcrumbDocumentID(*document2.ID),
			Name: "бланк заказа" + suffix,
			Type: types.BreadcrumbDocument(document2.DocumentType),
		}, {
			ID:   types.BreadcrumbServiceDescriptionID(serviceDescription.ID),
			Name: "услуга" + suffix,
			Type: types.BreadcrumbServiceDescription,
		}},
	})
}
