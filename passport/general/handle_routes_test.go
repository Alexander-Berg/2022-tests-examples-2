package processor

import (
	"context"
	"encoding/json"
	"fmt"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/passport/infra/daemons/yasms_internal/internal/model"
)

type TestCaseGetRoutes struct {
	request  GetRoutesRequest
	response GetRoutesResponse
}

func TestProcessor_HandleGetRoutes_All(t *testing.T) {
	provider := NewFakeProvider()
	processor, err := NewTestProcessor(provider)
	require.NoError(t, err)

	response, err := processor.HandleGetRoutes(context.Background(), GetRoutesRequest{
		FromID: "0",
		Limit:  100,
		Path:   "/1/route",
	})

	require.NoError(t, err)
	require.Equal(t, &GetRoutesResponse{
		Routes:     provider.Routes,
		TotalCount: uint64(len(provider.Routes)),
		NextURL:    "",
	}, response)
}

func TestProcessor_HandleGetRoutes_Some1(t *testing.T) {
	provider := NewFakeProvider()
	processor, err := NewTestProcessor(provider)
	require.NoError(t, err)

	response, err := processor.HandleGetRoutes(context.Background(), GetRoutesRequest{
		FromID: "2",
		Limit:  10,
		Path:   "/1/route",
	})

	require.NoError(t, err)
	require.Equal(t, &GetRoutesResponse{
		Routes:     provider.Routes[2:],
		TotalCount: uint64(len(provider.Routes)),
		NextURL:    "",
	}, response)
}

func TestProcessor_HandleGetRoutes_Some2(t *testing.T) {
	provider := NewFakeProvider()
	processor, err := NewTestProcessor(provider)
	require.NoError(t, err)

	tests := []TestCaseGetRoutes{
		{
			request: GetRoutesRequest{
				FromID: "0",
				Limit:  1,
				Path:   "/1/route",
			},
			response: GetRoutesResponse{
				Routes:     provider.Routes[:1],
				TotalCount: uint64(len(provider.Routes)),
				NextURL:    "/1/route?min=1&limit=1",
			},
		},
		{
			request: GetRoutesRequest{
				FromID: "1",
				Limit:  1,
				Path:   "/1/route",
			},
			response: GetRoutesResponse{
				Routes:     provider.Routes[1:2],
				TotalCount: uint64(len(provider.Routes)),
				NextURL:    "/1/route?min=2&limit=1",
			},
		},
		{
			request: GetRoutesRequest{
				FromID: "2",
				Limit:  1,
				Path:   "/1/route",
			},
			response: GetRoutesResponse{
				Routes:     provider.Routes[2:3],
				TotalCount: uint64(len(provider.Routes)),
				NextURL:    "/1/route?min=3&limit=1",
			},
		},
		{
			request: GetRoutesRequest{
				FromID: "3",
				Limit:  1,
				Path:   "/1/route",
			},
			response: GetRoutesResponse{
				Routes:     provider.Routes[3:4],
				TotalCount: uint64(len(provider.Routes)),
				NextURL:    "/1/route?min=4&limit=1",
			},
		},
		{
			request: GetRoutesRequest{
				FromID: "4",
				Limit:  1,
				Path:   "/1/route",
			},
			response: GetRoutesResponse{
				Routes:     []*model.RouteFullInfo{},
				TotalCount: uint64(len(provider.Routes)),
				NextURL:    "",
			},
		},
	}

	for _, test := range tests {
		response, err := processor.HandleGetRoutes(context.Background(), test.request)

		require.NoError(t, err)
		require.Equal(t, &test.response, response)
	}

}

func TestProcessor_HandleGetRoutes_Limits(t *testing.T) {
	provider := NewFakeProvider()
	processor, err := NewTestProcessor(provider)
	require.NoError(t, err)

	tests := []TestCaseGetRoutes{
		{
			request: GetRoutesRequest{
				FromID: "0",
				Limit:  1,
				Path:   "/1/route",
			},
			response: GetRoutesResponse{
				Routes:     provider.Routes[:1],
				TotalCount: uint64(len(provider.Routes)),
				NextURL:    "/1/route?min=1&limit=1",
			},
		},
		{
			request: GetRoutesRequest{
				FromID: "0",
				Limit:  2,
				Path:   "/1/route",
			},
			response: GetRoutesResponse{
				Routes:     provider.Routes[:2],
				TotalCount: uint64(len(provider.Routes)),
				NextURL:    "/1/route?min=2&limit=2",
			},
		},
		{
			request: GetRoutesRequest{
				FromID: "0",
				Limit:  3,
				Path:   "/1/route",
			},
			response: GetRoutesResponse{
				Routes:     provider.Routes[:3],
				TotalCount: uint64(len(provider.Routes)),
				NextURL:    "/1/route?min=3&limit=3",
			},
		},
		{
			request: GetRoutesRequest{
				FromID: "0",
				Limit:  4,
				Path:   "/1/route",
			},
			response: GetRoutesResponse{
				Routes:     provider.Routes[:4],
				TotalCount: uint64(len(provider.Routes)),
				NextURL:    "/1/route?min=4&limit=4",
			},
		},
		{
			request: GetRoutesRequest{
				FromID: "0",
				Limit:  100,
				Path:   "/1/route",
			},
			response: GetRoutesResponse{
				Routes:     provider.Routes[:4],
				TotalCount: uint64(len(provider.Routes)),
				NextURL:    "",
			},
		},
	}

	for _, test := range tests {
		response, err := processor.HandleGetRoutes(context.Background(), test.request)

		require.NoError(t, err)
		require.Equal(t, &test.response, response)
	}
}

func TestProcessor_MarshalRoutes(t *testing.T) {
	route := model.RouteFullInfo{
		RouteInfo: &model.RouteInfo{
			ID: "1",
			Gates: []*model.Gate{{
				ID:         "101",
				Alias:      "some gate101",
				AlphaName:  "some name101",
				Consumer:   "some consumer101",
				Contractor: "some contractor101",
			},
			},
			PhonePrefix: "+1",
			Weight:      1.0,
			AuditModify: model.EventInfo{
				ChangeID: "1",
				TS:       150,
			},
			AuditCreate: model.EventInfo{
				ChangeID: "4",
				TS:       200,
			},
		},
		Region: &model.Region{
			ID:     "456",
			Name:   "name",
			Prefix: "+7689",
			EntityCommon: model.EntityCommon{
				AuditModify: model.EventInfo{
					ChangeID: "2",
					TS:       160,
				},
				AuditCreate: model.EventInfo{
					ChangeID: "3",
					TS:       100,
				},
			},
		},
	}
	m, _ := json.Marshal(route)
	require.Equal(t, `{"rule_id":"1","destination":"+1","gates":[{"gateid":"101","aliase":"some gate101","fromname":"some name101","consumer":"some consumer101","contractor":"some contractor101"}],"weight":1,"mode":"","audit_create":{"change_id":"4","ts":200},"audit_modify":{"change_id":"1","ts":150},"region":{"name":"name"}}`, fmt.Sprint(string(m)))
}
