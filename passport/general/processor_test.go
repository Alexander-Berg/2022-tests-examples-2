package processor

import (
	"context"
	"fmt"
	"strconv"
	"time"

	"a.yandex-team.ru/passport/infra/daemons/yasms_internal/internal/filter"
	"a.yandex-team.ru/passport/infra/daemons/yasms_internal/internal/model"
	"a.yandex-team.ru/passport/shared/golibs/juggler"
)

type FakeProvider struct {
	Gates          []*model.Gate
	GatesWithAudit []*model.GateWithAudit
	Routes         []*model.RouteFullInfo
	BlockedPhones  []*model.BlockedPhone
	Fallbacks      []*model.Fallback
	Regions        []*model.Region
	Templates      []*model.Template

	AuditBulkInfo    model.AuditBulkInfo
	AuditChangesInfo model.AuditChangesInfo
}

func NewFakeProvider() *FakeProvider {
	ff := &FakeProvider{}
	ff.Gates = []*model.Gate{
		{
			ID:         "101",
			Alias:      "some gate101",
			AlphaName:  "some name101",
			Consumer:   "some consumer101",
			Contractor: "some contractor101",
		},
		{
			ID:         "102",
			Alias:      "some gate102",
			AlphaName:  "some name102",
			Consumer:   "some consumer102",
			Contractor: "some contractor102",
		},
		{
			ID:         "103",
			Alias:      "some gate103",
			AlphaName:  "some name103",
			Consumer:   "some consumer103",
			Contractor: "some contractor103",
		},
	}

	ff.GatesWithAudit = make([]*model.GateWithAudit, 0, len(ff.Gates))
	for _, gate := range ff.Gates {
		ff.GatesWithAudit = append(ff.GatesWithAudit, &model.GateWithAudit{
			Gate: model.Gate{
				ID:         gate.ID,
				Alias:      gate.Alias,
				AlphaName:  gate.AlphaName,
				Consumer:   gate.Consumer,
				Contractor: gate.Contractor,
			},
			EntityCommon: model.EntityCommon{
				AuditModify: model.EventInfo{
					ChangeID: "",
					TS:       0,
				},
				AuditCreate: model.EventInfo{
					ChangeID: "",
					TS:       0,
				},
			},
		},
		)
	}

	ff.Routes = []*model.RouteFullInfo{
		{
			RouteInfo: &model.RouteInfo{
				ID: "1",
				Gates: []*model.Gate{
					ff.Gates[0],
				},
				PhonePrefix: "+1",
				Weight:      1.0,
			},
			Region: &model.Region{
				Name: "Other",
			},
		},
		{
			RouteInfo: &model.RouteInfo{
				ID: "2",
				Gates: []*model.Gate{
					ff.Gates[0],
					ff.Gates[1],
					ff.Gates[2],
				},
				PhonePrefix: "+12",
				Weight:      -1,
			},
			Region: &model.Region{
				Name: "Other",
			},
		},
		{
			RouteInfo: &model.RouteInfo{
				ID:          "3",
				Gates:       []*model.Gate{},
				PhonePrefix: "+123",
				Weight:      100,
			},
			Region: &model.Region{
				Name: "Other",
			},
		},
		{
			RouteInfo: &model.RouteInfo{
				ID: "4",
				Gates: []*model.Gate{
					ff.Gates[2],
				},
				PhonePrefix: "+1234",
				Weight:      -100,
			},
			Region: &model.Region{
				Name: "Other",
			},
		},
	}

	ff.BlockedPhones = []*model.BlockedPhone{
		{
			ID:          "54",
			PhoneNumber: "+79037177191",
			BlockType:   model.BlockTypePermanent,
			BlockUntil:  time.Date(2021, 12, 29, 16, 9, 48, 0, time.UTC),
		},
		{
			ID:          "55",
			PhoneNumber: "+79095856762",
			BlockType:   model.BlockTypePermanent,
			BlockUntil:  time.Date(2070, 12, 29, 16, 19, 31, 0, time.UTC),
		},
	}

	ff.Fallbacks = []*model.Fallback{
		{
			ID:      "33",
			SrcGate: "infobip",
			SrcName: "Yandex",
			DstGate: "gms",
			DstName: "Yandex",
			Order:   0,
		},
		{
			ID:      "42",
			SrcGate: "gms",
			SrcName: "Yandex",
			DstGate: "m1",
			DstName: "Yandex",
			Order:   0,
		},
	}

	ff.Regions = []*model.Region{
		{
			ID:     "1",
			Prefix: "+7",
			Name:   "Russia",
			EntityCommon: model.EntityCommon{
				AuditModify: model.EventInfo{
					ChangeID: "",
					TS:       0,
				},
				AuditCreate: model.EventInfo{
					ChangeID: "",
					TS:       0,
				},
			},
		},
		{
			ID:     "2",
			Prefix: "+374",
			Name:   "Armenia",
			EntityCommon: model.EntityCommon{
				AuditModify: model.EventInfo{
					ChangeID: "",
					TS:       0,
				},
				AuditCreate: model.EventInfo{
					ChangeID: "",
					TS:       0,
				},
			},
		},
		{
			ID:     "3",
			Prefix: "+",
			Name:   "Other",
			EntityCommon: model.EntityCommon{
				AuditModify: model.EventInfo{
					ChangeID: "",
					TS:       0,
				},
				AuditCreate: model.EventInfo{
					ChangeID: "",
					TS:       0,
				},
			},
		},
	}

	ff.Templates = []*model.Template{
		{
			ID:                "1",
			Text:              "I see a {{name}} and code {{code}}",
			AbcService:        "passport_infra",
			SenderMeta:        "{\"whatsapp\": {\"id\": 1111}}",
			FieldsDescription: "{\"code\": {\"privacy\": \"secret\"}}",
			AuditModify: model.EventInfo{
				ChangeID: "",
				TS:       0,
			},
			AuditCreate: model.EventInfo{
				ChangeID: "",
				TS:       0,
			},
		},
		{
			ID:         "2",
			Text:       "New {{service}} init",
			AbcService: "passport_infra",
			SenderMeta: "{\"whatsapp\": {\"id\": 2222}}",
			AuditModify: model.EventInfo{
				ChangeID: "",
				TS:       0,
			},
			AuditCreate: model.EventInfo{
				ChangeID: "",
				TS:       0,
			},
		},
	}

	ff.AuditBulkInfo = model.AuditBulkInfo{
		AuditBulkInfoBase: model.AuditBulkInfoBase{
			ID:        "1",
			Comment:   "comment",
			Issue:     "PASSP-1",
			Author:    "login",
			Timestamp: 1233456,
		},
		Changes: map[string]model.AuditRowChange{
			"1": {AuditRowChangeBase: model.AuditRowChangeBase{EntityID: "100", Action: "add"}, Payload: "payload"},
			"2": {AuditRowChangeBase: model.AuditRowChangeBase{EntityID: "200", Action: "update"}, Payload: "payload2"},
		},
	}

	ff.AuditChangesInfo = model.AuditChangesInfo{
		"1": model.AuditChangeInfo{
			AuditRowChangeBase: model.AuditRowChangeBase{EntityID: "100", Action: "add"},
			AuditBulkInfo: model.AuditBulkInfoBase{
				ID:        "1",
				Comment:   "comment",
				Issue:     "PASSP-1",
				Author:    "login",
				Timestamp: 1233456,
			},
		},
		"2": model.AuditChangeInfo{
			AuditRowChangeBase: model.AuditRowChangeBase{EntityID: "200", Action: "update"},
			AuditBulkInfo: model.AuditBulkInfoBase{
				ID:        "2",
				Comment:   "comment2",
				Issue:     "PASSP-2",
				Author:    "login",
				Timestamp: 5679000,
			},
		},
	}

	return ff
}

func (provider *FakeProvider) GetName() string {
	return "provider:fake"
}

func (provider *FakeProvider) GetJugglerStatus() *juggler.Status {
	return juggler.NewStatusOk()
}

func (provider *FakeProvider) GetRoutesInfo(ctx context.Context, fromID model.EntityID, limit uint64, routesFilter filter.Filter) ([]*model.RouteInfo, error) {
	routes := make([]*model.RouteInfo, 0, limit)

	for _, route := range provider.Routes {
		if route.ID > fromID {
			routes = append(routes, route.RouteInfo)
		}

		if len(routes) >= int(limit) {
			break
		}
	}

	return routes, nil
}

func (provider *FakeProvider) GetRouteEnums(ctx context.Context) (*model.Enums, error) {
	enums := &model.Enums{
		Aliases:    map[string][]string{},
		AlphaNames: map[string][]string{},
	}
	aliases := map[string]map[string]bool{}
	alphas := map[string]map[string]bool{}
	for _, gate := range provider.Gates {
		if _, ok := aliases[gate.Alias]; !ok {
			aliases[gate.Alias] = map[string]bool{}
		}
		if _, ok := alphas[gate.AlphaName]; !ok {
			alphas[gate.AlphaName] = map[string]bool{}
		}
		if !aliases[gate.Alias][gate.AlphaName] {
			aliases[gate.Alias][gate.AlphaName] = true
			enums.Aliases[gate.Alias] = append(enums.Aliases[gate.Alias], gate.AlphaName)
		}

		if !alphas[gate.AlphaName][gate.Alias] {
			alphas[gate.AlphaName][gate.Alias] = true
			enums.AlphaNames[gate.AlphaName] = append(enums.AlphaNames[gate.AlphaName], gate.Alias)
		}
	}

	return enums, nil
}

func (provider *FakeProvider) GetRoutesCount(ctx context.Context, routesFilter filter.Filter) (uint64, error) {
	return uint64(len(provider.Routes)), nil
}

func (provider *FakeProvider) GetGates(ctx context.Context, fromID model.EntityID, limit uint64, gatesFilter filter.Filter) ([]*model.GateWithAudit, error) {
	gates := make([]*model.GateWithAudit, 0, len(provider.Gates))

	for _, gate := range provider.GatesWithAudit {
		if gate.ID > fromID {
			gates = append(gates, gate)
		}

		if len(gates) >= int(limit) {
			break
		}
	}

	return gates, nil
}

func (provider *FakeProvider) GetAllGates(ctx context.Context) ([]*model.GateWithAudit, error) {
	return provider.GatesWithAudit, nil
}

func (provider *FakeProvider) GetGatesCount(ctx context.Context, gatesFilter filter.Filter) (uint64, error) {
	return uint64(len(provider.Gates)), nil
}

func (provider *FakeProvider) GetBlockedPhones(ctx context.Context, fromID model.EntityID, limit uint64, fallbacksFilter filter.Filter) ([]*model.BlockedPhone, error) {
	blockedPhones := make([]*model.BlockedPhone, 0, len(provider.BlockedPhones))

	for _, blockedPhone := range provider.BlockedPhones {
		if blockedPhone.ID > fromID {
			blockedPhones = append(blockedPhones, blockedPhone)
		}

		if len(blockedPhones) >= int(limit) {
			break
		}
	}

	return blockedPhones, nil
}

func (provider *FakeProvider) GetBlockedPhonesCount(ctx context.Context, blockedPhonesFilter filter.Filter) (uint64, error) {
	return uint64(len(provider.BlockedPhones)), nil
}

func (provider *FakeProvider) GetFallbacks(ctx context.Context, fromID model.EntityID, limit uint64, fallbacksFilter filter.Filter) ([]*model.Fallback, error) {
	fallbacks := make([]*model.Fallback, 0, len(provider.Fallbacks))

	for _, fallback := range provider.Fallbacks {
		if fallback.ID > fromID {
			fallbacks = append(fallbacks, fallback)
		}

		if len(fallbacks) >= int(limit) {
			break
		}
	}

	return fallbacks, nil
}

func (provider *FakeProvider) GetFallbacksCount(ctx context.Context, fallbacksFilter filter.Filter) (uint64, error) {
	return uint64(len(provider.Fallbacks)), nil
}

func (provider *FakeProvider) GetRegions(ctx context.Context, regionsFilter filter.Filter) ([]*model.Region, error) {
	return provider.Regions, nil
}

func (provider *FakeProvider) SetRoutes(ctx context.Context, delete []model.EntityID, create []*model.Route, update []*model.Route, auditLogBulkParams *model.AuditLogBulkParams) error {
	routes := make([]*model.RouteFullInfo, 0, len(provider.Routes))
	exists := func(a []model.EntityID, id model.EntityID) bool {
		for _, e := range a {
			if e == id {
				return true
			}
		}
		return false
	}

	findGate := func(a []*model.Gate, id model.EntityID) *model.Gate {
		for _, e := range a {
			if e.ID == id {
				return e
			}
		}
		return nil
	}

	findRoute := func(a []*model.Route, id model.EntityID) *model.Route {
		for _, e := range a {
			if e.ID == id {
				return e
			}
		}
		return nil
	}

	makeRouteInfo := func(route *model.Route) *model.RouteInfo {
		gates := make([]*model.Gate, 0, len(route.Gates))
		for _, gateID := range route.Gates {
			gates = append(gates, findGate(provider.Gates, gateID))
		}
		return &model.RouteInfo{
			ID:          route.ID,
			PhonePrefix: route.PhonePrefix,
			Gates:       gates,
			Weight:      route.Weight,
			Mode:        route.Mode,
		}
	}

	for _, route := range provider.Routes {
		if !exists(delete, route.ID) {
			routes = append(routes, route)
		}
	}

	for i := range routes {
		route := findRoute(update, routes[i].ID)
		if route != nil {
			routes[i].RouteInfo = makeRouteInfo(route)
		}
	}

	for _, route := range create {
		id, _ := strconv.ParseUint(provider.Routes[len(provider.Routes)-1].ID, 10, 64)
		route.ID = strconv.FormatUint(id+uint64(1), 10)
		routes = append(routes, &model.RouteFullInfo{
			RouteInfo: makeRouteInfo(route),
			Region: &model.Region{
				Name: "Other",
			},
		})
	}

	provider.Routes = routes
	return nil
}

func (provider *FakeProvider) SetGates(ctx context.Context, delete []model.EntityID, create []*model.Gate, update []*model.Gate, auditLogBulkParams *model.AuditLogBulkParams) error {
	fmt.Println(delete, create, update)
	return nil
}

func (provider *FakeProvider) SetBlockedPhones(ctx context.Context, delete []model.EntityID, create []*model.BlockedPhone, update []*model.BlockedPhone, auditLogBulkParams *model.AuditLogBulkParams) error {
	fmt.Println(delete, create, update)
	return nil
}

func (provider *FakeProvider) SetFallbacks(ctx context.Context, delete []model.EntityID, create []*model.Fallback, update []*model.Fallback, auditLogBulkParams *model.AuditLogBulkParams) error {
	fmt.Println(delete, create, update)
	return nil
}

func (provider *FakeProvider) SetRegions(ctx context.Context, delete []model.EntityID, create []*model.Region, update []*model.Region, auditLogBulkParams *model.AuditLogBulkParams) error {
	fmt.Println(delete, create, update)
	return nil
}

func (provider *FakeProvider) GetAuditBulkInfo(ctx context.Context, id model.EntityID) (*model.AuditBulkInfo, error) {
	return &provider.AuditBulkInfo, nil
}

func (provider *FakeProvider) GetAuditChangeInfo(ctx context.Context, changeIds []model.EntityID) (*model.AuditChangesInfo, error) {
	return &provider.AuditChangesInfo, nil
}

func (provider *FakeProvider) GetTemplates(ctx context.Context, fromID model.EntityID, limit uint64, templatesFilter filter.Filter) ([]*model.Template, error) {
	templates := make([]*model.Template, 0, len(provider.Templates))

	for _, template := range provider.Templates {
		if template.ID > fromID {
			templates = append(templates, template)
		}

		if len(templates) >= int(limit) {
			break
		}
	}

	return templates, nil
}

func (provider *FakeProvider) GetTemplatesCount(ctx context.Context, templatesFilter filter.Filter) (uint64, error) {
	return uint64(len(provider.Templates)), nil
}

func (provider *FakeProvider) SetTemplates(ctx context.Context, create []*model.Template, update []*model.Template, auditLogBulkParams *model.AuditLogBulkParams) error {
	fmt.Println(create, update)
	return nil
}

func NewTestProcessor(provider *FakeProvider) (*Processor, error) {
	return &Processor{
		fetcher: provider,
		writer:  provider,
	}, nil
}
