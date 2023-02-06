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
	"a.yandex-team.ru/strm/common/go/pkg/fn"
)

func TestDocumentWizardOnlyOperator(t *testing.T) {
	const suffix = " 4"

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
		Operator:  cmdbapi.Operator{Name: "оператор" + suffix},
		Documents: nil,
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
	require.Equal(t, []cmdbapi.Document{}, documents)
	require.Equal(t, cmdbapi.ServiceDescriptionFlatOut{
		ID:               serviceDescription.ID,
		Details:          "описание услуги" + suffix,
		ParentDocumentID: nil,
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

	op, err := client.Operators.Get(ctx, *operator.ID)
	require.NoError(t, err)
	require.Equal(t, cmdbapi.OperatorExt{
		Operator:           cmdbapi.Operator{ID: operator.ID, Name: "оператор" + suffix, DefaultContactID: &contact.ID},
		DefaultContactName: ptr.String("контакт" + suffix),
	}, op.OperatorExt)

	cmdbServer.Services.GetService(t, service.ID, cmdbapi.ServiceExt{
		ServiceOut:          *service,
		Details:             "описание услуги" + suffix,
		OperatorName:        "оператор" + suffix,
		ActualLinkID:        nil,
		ContractID:          nil,
		ContractName:        nil,
		ActualOrderFormID:   nil,
		ActualOrderFormName: nil,
		Documents:           nil,
	})
	sd, err := client.ServiceDescriptions.Get(ctx, serviceDescription.ID)
	require.NoError(t, err)
	require.Equal(t, cmdbapi.ServiceDescriptionNestedOut{
		ID:                             serviceDescription.ID,
		Details:                        "описание услуги" + suffix,
		Operator:                       cmdbapi.OperatorShortOut{ID: *operator.ID, Name: "оператор" + suffix},
		Contact:                        cmdbapi.ContactOut{ID: contact.ID, Name: "контакт" + suffix},
		Service:                        service,
		LinkID:                         nil,
		Location:                       nil,
		CanceledByServiceDescriptionID: nil,
		OperatorID:                     *operator.ID,
		ParentDocumentID:               nil,
		LocationID:                     nil,
	}, sd.ServiceDescriptionNestedOut)
}
