package dbsynctest

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"net/url"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"gorm.io/plugin/dbresolver"

	"a.yandex-team.ru/library/go/core/log"
	"a.yandex-team.ru/library/go/core/log/zap"
	"a.yandex-team.ru/library/go/ptr"
	"a.yandex-team.ru/noc/cmdb/pkg/cmdbapi"
	"a.yandex-team.ru/noc/cmdb/pkg/cmdbapitest"
	"a.yandex-team.ru/noc/cmdb/pkg/cmdbclient"
	"a.yandex-team.ru/noc/cmdb/pkg/configuration"
	"a.yandex-team.ru/noc/cmdb/pkg/dbconn"
	"a.yandex-team.ru/noc/cmdb/pkg/dbsync"
	"a.yandex-team.ru/noc/cmdb/pkg/mur"
	"a.yandex-team.ru/noc/cmdb/pkg/rtmodel"
	"a.yandex-team.ru/noc/cmdb/pkg/types"
	"a.yandex-team.ru/strm/common/go/pkg/fn"
	"a.yandex-team.ru/strm/common/go/pkg/xtime"
)

func TestSync(t *testing.T) {

	data := &cmdbapitest.Data{Object: []cmdbapitest.Object{
		cmdbapitest.ObjectDante(),
	}}
	graphqlServer := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		_ = json.NewEncoder(w).Encode(cmdbapitest.GraphQLResponse{
			Data: *data,
		})
	}))

	peersReportServer := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		_ = json.NewEncoder(w).Encode(cmdbapitest.PeersReportResponse{{
			ID:             175,
			ObjectName:     "dante",
			AllocInterface: "ae8.862",
			IP:             "130.193.63.29",
			Name:           "Ya.Cloud 100GE@M9 %peer% %NOC-16295%",
		}})
	}))

	dbURI := cmdbapitest.DBURI()
	err := dbsync.Main(dbsync.Config{
		RT: dbsync.ConfigRTClient{
			Endpoint:   graphqlServer.URL,
			OAuthToken: "",
		},
		DatabaseURI:    dbURI,
		DiffPath:       "diff.json",
		PeerReportsURI: peersReportServer.URL,
		Logger:         dbsync.ConfigLogger{Verbose: true},
	})
	require.NoError(t, err)

	lg, _ := zap.New(zap.JSONConfig(log.DebugLevel))
	logger := fn.NewLogger(lg)
	db, err := dbconn.Database{
		URIRW:  dbURI,
		Logger: logger,
	}.Open()
	require.NoError(t, err)
	now := &xtime.TimeIncrement{TimeNow: time.Unix(1700000000, 0), Step: xtime.Seconds(1)}
	register := configuration.RegisterLoggerPlugin{
		LoggerPlugin: configuration.LoggerPlugin{
			Now:    now,
			RW:     db.Clauses(dbresolver.Write),
			Logger: logger,
		},
		RW: db.Clauses(dbresolver.Write),
	}
	require.NoError(t, register.RegisterLoggerPlugin())

	assert.NoError(t, db.Create(&rtmodel.Object{ID: 1010, Name: (*types.ObjectName)(ptr.String("dummy"))}).Error)

	server, client, cmdbServer := cmdbapitest.NewRouter(t, db, logger)
	ctx := context.TODO()

	location, err := client.Locations.Post(ctx, &cmdbapi.LocationIn{Name: "m9"})
	require.NoError(t, err)
	link1, err := client.Links.Post(ctx, cmdbapitest.NewLinkIn(&location.ID))
	require.NoError(t, err)

	net := cmdbServer.PostNets(t, link1)
	_ = cmdbServer.PostLinkObjects(t, link1)
	alloc, err := client.ObjectAllocations.Post(ctx, cmdbapi.ObjectAllocationIn{
		ObjectID:       23778,
		IP:             "130.193.63.29",
		Interface:      "ae8.862",
		Type:           "regular",
		NetCIDR:        net.CIDR,
		LinkInternalID: &link1.InternalID,
	})
	require.NoError(t, err)
	cmdbServer.GetObjects(t)
	cmdbServer.GetPorts(t)
	var port cmdbapi.PortExt
	server.Get(t, server.URL+"/api/ports/1125065", &port)
	assert.Equal(t, GetPort(), port)

	link1Ext, err := client.Links.Get(ctx, link1.InternalID)
	require.NoError(t, err)
	assert.Equal(t, link1, &link1Ext.LinkOut)

	linkWizard2, err := client.LinkWizard.Post(ctx, cmdbapitest.GetLinkWizard())
	require.NoError(t, err)
	linkWizard2Ext, err := client.LinkWizard.Get(ctx, linkWizard2.InternalID)
	require.NoError(t, err)
	assert.Equal(t, linkWizard2, &linkWizard2Ext.LinkOut)

	location2 := cmdbapitest.NewLocationIn(linkWizard2Ext.Location)
	linkWizard2Modified, err := client.LinkWizard.Put(ctx, linkWizard2.InternalID, cmdbapitest.GetLinkWizardModified(location2))
	require.NoError(t, err)
	linkWizard2ModifiedExt, err := client.LinkWizard.Get(ctx, linkWizard2Modified.InternalID)
	require.NoError(t, err)
	assert.Equal(t, linkWizard2Modified, &linkWizard2ModifiedExt.LinkOut)

	_, err = client.LinkWizard.Delete(ctx, linkWizard2Modified.InternalID)
	require.NoError(t, err)
	_, err = client.Links.Get(ctx, linkWizard2Modified.InternalID)
	cmdbapitest.RequireError(t, cmdbclient.Error{StatusCode: http.StatusNotFound, Err: mur.Error{
		Message: "record not found: table=links",
		Error:   "record not found",
	}}, err)

	contact := cmdbServer.Contacts.PostContact(t, GetContact())
	cmdbServer.Contacts.GetContacts(t, []*cmdbapi.ContactOut{contact})
	contactModified := cmdbServer.Contacts.PutContact(t, GetContactModified(contact.ID))
	cmdbServer.Contacts.GetContacts(t, []*cmdbapi.ContactOut{contactModified})

	operator := GetOperator(contact.ID)
	cmdbServer.Operators.PostOperator(t, operator)
	op, err := client.Operators.Get(ctx, *operator.ID)
	require.NoError(t, err)
	require.Equal(t, operator, op.OperatorExt.Operator)
	cmdbServer.Operators.GetOperatorRaise(t, cmdbapi.Operator{ID: (*types.OperatorID)(ptr.Int64(777))},
		http.StatusNotFound, mur.Error{
			Message: "record not found: table=operators",
			Error:   "record not found",
		})
	cmdbServer.Operators.GetOperators(t, []cmdbapi.Operator{operator})
	cmdbServer.Operators.PutOperator(t, GetOperatorModified(contact.ID))
	cmdbServer.Operators.GetOperators(t, []cmdbapi.Operator{GetOperatorModified(contact.ID)})

	contract1, err := client.Documents.Post(ctx, GetContract(operator, contact))
	require.NoError(t, err)
	contract1Ext, err := client.Documents.Get(ctx, *contract1.ID)
	require.NoError(t, err)
	require.Equal(t, contract1, contract1Ext.Document)
	contract1Modified, err := client.Documents.Put(ctx, *contract1.ID, GetContractModified(operator, contact, contract1.ID))
	require.NoError(t, err)
	contract1ModifiedExt, err := client.Documents.Get(ctx, *contract1Modified.ID)
	require.NoError(t, err)
	require.Equal(t, contract1Modified, contract1ModifiedExt.Document)

	orderForm1, err := client.Documents.Post(ctx, GetOrderForm(contract1, contact))
	require.NoError(t, err)
	orderForm1Ext, err := client.Documents.Get(ctx, *orderForm1.ID)
	require.NoError(t, err)
	require.Equal(t, orderForm1, orderForm1Ext.Document)
	orderForm1Modified, err := client.Documents.Put(ctx, *orderForm1.ID, GetOrderFormModified(contract1, contact, orderForm1.ID))
	require.NoError(t, err)
	orderForm1ModifiedExt, err := client.Documents.Get(ctx, *orderForm1.ID)
	require.NoError(t, err)
	require.Equal(t, orderForm1Modified, orderForm1ModifiedExt.Document)

	service1 := cmdbServer.Services.PostService(t, cmdbapi.ServiceIn{VisibleID: "id услуги", OperatorID: operator.ID})
	cmdbServer.Services.GetServices(t, []cmdbapi.ServiceExt{{ServiceOut: service1, OperatorName: operator.Name}})
	service1Modified := cmdbServer.Services.PutService(t, service1.ID, cmdbapi.ServiceIn{VisibleID: "id услуги edited", OperatorID: operator.ID})
	cmdbServer.Services.GetServices(t, []cmdbapi.ServiceExt{{ServiceOut: service1Modified, OperatorName: operator.Name}})

	sd1, err := client.ServiceDescriptions.Post(ctx, GetOrderFormRecord(operator, &orderForm1, link1, contact, &service1.ID, "name"))
	require.NoError(t, err)
	sd1Ext, err := client.ServiceDescriptions.Get(ctx, sd1.ID)
	require.NoError(t, err)
	require.Equal(t, sd1, ServiceDescriptionFlat(&sd1Ext.ServiceDescriptionNestedOut))
	sd1Modified, err := client.ServiceDescriptions.Put(ctx, sd1.ID, GetOrderFormRecordModified(sd1.ID, operator, &orderForm1, link1, contact, &service1.ID, "name"))
	require.NoError(t, err)
	sd1ModifiedExt, err := client.ServiceDescriptions.Get(ctx, sd1.ID)
	require.NoError(t, err)
	require.Equal(t, sd1Modified, ServiceDescriptionFlat(&sd1ModifiedExt.ServiceDescriptionNestedOut))

	linkWizard1Filled, err := client.LinkWizard.Get(ctx, link1.InternalID)
	require.NoError(t, err)
	require.Equal(t, cmdbapitest.GetLinkWizardExt(link1, alloc, net, link1Ext.Location), linkWizard1Filled)

	service1Ext, err := client.Services.Get(ctx, service1Modified.ID)
	require.NoError(t, err)
	require.Equal(t, GetServiceExt(service1Modified, operator, link1, contract1, orderForm1, sd1ModifiedExt), service1Ext)

	_, err = client.ServiceDescriptions.Delete(ctx, sd1.ID)
	require.NoError(t, err)

	cmdbServer.Services.DeleteService(t, service1.ID, service1Modified)
	cmdbServer.Services.GetServices(t, []cmdbapi.ServiceExt{})

	orderForm3, err := client.Documents.Delete(ctx, *orderForm1.ID)
	require.NoError(t, err)
	require.Equal(t, orderForm1Modified, orderForm3)

	contract3, err := client.Documents.Delete(ctx, *contract1.ID)
	require.NoError(t, err)
	require.Equal(t, contract1Modified, contract3)

	cmdbServer.Operators.DeleteOperator(t, GetOperatorModified(contact.ID))
	cmdbServer.Operators.GetOperators(t, []cmdbapi.Operator{})

	cmdbServer.Contacts.DeleteContact(t, GetContactModified(contact.ID))
	cmdbServer.Contacts.GetContacts(t, []*cmdbapi.ContactOut{})

	var logs []cmdbapi.LogExt
	uri := url.URL{Path: "/api/logs", RawQuery: url.Values{"after": {"1700000020"}, "before": {"1700000030"}}.Encode()}
	server.Get(t, server.URL+uri.String(), &logs)
	assert.Equal(t, 11, len(logs), logs)

	// check delete logic
	data.Object[0].Allocs = nil
	err = dbsync.Main(dbsync.Config{
		RT: dbsync.ConfigRTClient{
			Endpoint:   graphqlServer.URL,
			OAuthToken: "",
		},
		DatabaseURI:    dbURI,
		DiffPath:       "diff.json",
		PeerReportsURI: peersReportServer.URL,
	})
	require.NoError(t, err)
}

func ServiceDescriptionFlat(sd *cmdbapi.ServiceDescriptionNestedOut) *cmdbapi.ServiceDescriptionFlatOut {
	var serviceID *types.ServiceID
	if service := sd.Service; service != nil {
		serviceID = &service.ID
	}
	return &cmdbapi.ServiceDescriptionFlatOut{
		ID:                             sd.ID,
		Details:                        sd.Details,
		OperatorID:                     sd.Operator.ID,
		ParentDocumentID:               sd.ParentDocumentID,
		ServiceID:                      serviceID,
		LinkInternalID:                 sd.LinkInternalID,
		CanceledByServiceDescriptionID: sd.CanceledByServiceDescriptionID,
		ContactID:                      sd.Contact.ID,
	}
}

func GetPort() cmdbapi.PortExt {
	return cmdbapi.PortExt{
		Port: cmdbapi.Port{
			ID:       1125065,
			Name:     (*types.PortName)(ptr.String("ae8")),
			ObjectID: (*types.ObjectID)(ptr.Int64(23778)),
		},
		ObjectName: "dante",
	}
}

func GetContact() cmdbapi.ContactIn {
	return cmdbapi.ContactIn{
		ID:             nil,
		Name:           "Первая линия поддержки Ростелеком",
		Details:        "+7(999)111-22-33",
		EmailForRobots: "for_robots@rostelekom.ru",
	}
}

func GetContactModified(contactID types.ContactID) cmdbapi.ContactIn {
	return cmdbapi.ContactIn{
		ID:             &contactID,
		Name:           "Первая линия поддержки Ростелеком",
		Details:        "+7(999)111-22-33",
		EmailForRobots: "for_robots@rostelekom.ru",
	}
}

func GetOperator(contactID types.ContactID) cmdbapi.Operator {
	return cmdbapi.Operator{
		ID:               (*types.OperatorID)(ptr.Int64(7)),
		Name:             "Ростелеком",
		Details:          "test",
		DefaultContactID: &contactID,
	}
}

func GetOperatorModified(contactID types.ContactID) cmdbapi.Operator {
	return cmdbapi.Operator{
		ID:               (*types.OperatorID)(ptr.Int64(7)),
		Name:             "Ростелеком",
		Details:          "test 2",
		DefaultContactID: &contactID,
	}
}

func GetContract(operator cmdbapi.Operator, contact *cmdbapi.ContactOut) cmdbapi.Document {
	return cmdbapi.Document{
		ID:               nil,
		Name:             "Договор",
		Details:          "details",
		DefaultContactID: &contact.ID,
		DocumentType:     types.DocumentTypeContract,
		OperatorID:       *operator.ID,
		ParentDocumentID: nil,
	}
}

func GetContractModified(operator cmdbapi.Operator, contact *cmdbapi.ContactOut, contractID *types.DocumentID) cmdbapi.Document {
	return cmdbapi.Document{
		ID:               contractID,
		Name:             "Договор",
		Details:          "details modified",
		DefaultContactID: &contact.ID,
		DocumentType:     types.DocumentTypeContract,
		OperatorID:       *operator.ID,
		ParentDocumentID: nil,
	}
}

func GetService(o cmdbapi.Operator) cmdbapi.ServiceOut {
	return cmdbapi.ServiceOut{
		ID:         41,
		VisibleID:  "827366",
		OperatorID: *o.ID,
	}
}

func GetServiceExt(
	service cmdbapi.ServiceOut,
	o cmdbapi.Operator,
	link *cmdbapi.LinkOut,
	contract cmdbapi.Document,
	orderForm cmdbapi.Document,
	record1 *cmdbapi.ServiceDescriptionNestedWithBreadcrumbs,
) cmdbapi.ServiceExt {
	return cmdbapi.ServiceExt{
		ServiceOut:     service,
		Details:        record1.Details,
		OperatorName:   o.Name,
		LinkInternalID: &link.InternalID,
		LinkID:         link.LinkID,
		Documents: []cmdbapi.DocumentShort{{
			ID:           *contract.ID,
			Name:         "Договор",
			DocumentType: "contract",
		}, {
			ID:           *orderForm.ID,
			Name:         "Бланк заказа",
			DocumentType: "order form",
		}},
		ContractID:          contract.ID,
		ContractName:        ptr.String("Договор"),
		ActualOrderFormID:   orderForm.ID,
		ActualOrderFormName: ptr.String("Бланк заказа"),
		ActualLinkID:        link.LinkID,
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

func GetOrderFormModified(contract cmdbapi.Document, contact *cmdbapi.ContactOut, orderFormID *types.DocumentID) cmdbapi.Document {
	return cmdbapi.Document{
		ID:               orderFormID,
		Name:             "Бланк заказа",
		Details:          "Список услуг 2",
		DefaultContactID: &contact.ID,
		DocumentType:     types.DocumentTypeOrderForm,
		OperatorID:       contract.OperatorID,
		ParentDocumentID: contract.ID,
	}
}

func GetOrderFormRecord(operator cmdbapi.Operator, form *cmdbapi.Document, link *cmdbapi.LinkOut, contact *cmdbapi.ContactOut, serviceID *types.ServiceID, _ string) *cmdbapi.ServiceDescriptionNestedIn {
	return &cmdbapi.ServiceDescriptionNestedIn{
		ID:               nil,
		Details:          "Относится к услуге",
		ParentDocumentID: form.ID,
		Service:          &cmdbapi.ServiceIn{ID: serviceID},
		ContactID:        contact.ID,
		LinkInternalID:   &link.InternalID,
		OperatorID:       operator.ID,
	}
}

func GetOrderFormRecordModified(id types.ServiceDescriptionID, operator cmdbapi.Operator, form *cmdbapi.Document, link *cmdbapi.LinkOut, contact *cmdbapi.ContactOut, serviceID *types.ServiceID, _ string) *cmdbapi.ServiceDescriptionNestedIn {
	return &cmdbapi.ServiceDescriptionNestedIn{
		ID:               &id,
		Details:          "Относится к услуге 2",
		ParentDocumentID: form.ID,
		Service:          &cmdbapi.ServiceIn{ID: serviceID},
		ContactID:        contact.ID,
		LinkInternalID:   &link.InternalID,
		OperatorID:       operator.ID,
	}
}
