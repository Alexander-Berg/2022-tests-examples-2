package processor

import (
	"context"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/passport/infra/daemons/yasms_internal/internal/model"
)

type TestCaseGetGates struct {
	request  GetGatesRequest
	response GetGatesResponse
}

func TestProcessor_HandleGetGates_All(t *testing.T) {
	provider := NewFakeProvider()
	processor, err := NewTestProcessor(provider)
	require.NoError(t, err)

	response, err := processor.HandleGetGates(context.Background(), GetGatesRequest{
		FromID: "0",
		Limit:  100,
		Path:   "/1/gate",
	})

	require.NoError(t, err)
	require.Equal(t, &GetGatesResponse{
		Gates:      provider.GatesWithAudit,
		TotalCount: uint64(len(provider.Gates)),
		NextURL:    "",
	}, response)
}

func TestProcessor_HandleGetGates_Some1(t *testing.T) {
	provider := NewFakeProvider()
	processor, err := NewTestProcessor(provider)
	require.NoError(t, err)

	response, err := processor.HandleGetGates(context.Background(), GetGatesRequest{
		FromID: "102",
		Limit:  10,
		Path:   "/1/gate",
	})

	require.NoError(t, err)
	require.Equal(t, &GetGatesResponse{
		Gates:      provider.GatesWithAudit[2:],
		TotalCount: uint64(len(provider.Gates)),
		NextURL:    "",
	}, response)
}

func TestProcessor_HandleGetGates_Some2(t *testing.T) {
	provider := NewFakeProvider()
	processor, err := NewTestProcessor(provider)
	require.NoError(t, err)

	tests := []TestCaseGetGates{
		{
			request: GetGatesRequest{
				FromID: "0",
				Limit:  1,
				Path:   "/1/gate",
			},
			response: GetGatesResponse{
				Gates:      provider.GatesWithAudit[:1],
				TotalCount: uint64(len(provider.Gates)),
				NextURL:    "/1/gate?min=101&limit=1",
			},
		},
		{
			request: GetGatesRequest{
				FromID: "101",
				Limit:  1,
				Path:   "/1/gate",
			},
			response: GetGatesResponse{
				Gates:      provider.GatesWithAudit[1:2],
				TotalCount: uint64(len(provider.Gates)),
				NextURL:    "/1/gate?min=102&limit=1",
			},
		},
		{
			request: GetGatesRequest{
				FromID: "102",
				Limit:  1,
				Path:   "/1/gate",
			},
			response: GetGatesResponse{
				Gates:      provider.GatesWithAudit[2:3],
				TotalCount: uint64(len(provider.Gates)),
				NextURL:    "/1/gate?min=103&limit=1",
			},
		},
		{
			request: GetGatesRequest{
				FromID: "103",
				Limit:  1,
				Path:   "/1/gate",
			},
			response: GetGatesResponse{
				Gates:      []*model.GateWithAudit{},
				TotalCount: uint64(len(provider.Gates)),
				NextURL:    "",
			},
		},
	}

	for _, test := range tests {
		response, err := processor.HandleGetGates(context.Background(), test.request)

		require.NoError(t, err)
		require.Equal(t, &test.response, response)
	}

}

func TestProcessor_HandleGetGates_Limits(t *testing.T) {
	provider := NewFakeProvider()
	processor, err := NewTestProcessor(provider)
	require.NoError(t, err)

	tests := []TestCaseGetGates{
		{
			request: GetGatesRequest{
				FromID: "0",
				Limit:  1,
				Path:   "/1/gate",
			},
			response: GetGatesResponse{
				Gates:      provider.GatesWithAudit[:1],
				TotalCount: uint64(len(provider.Gates)),
				NextURL:    "/1/gate?min=101&limit=1",
			},
		},
		{
			request: GetGatesRequest{
				FromID: "0",
				Limit:  2,
				Path:   "/1/gate",
			},
			response: GetGatesResponse{
				Gates:      provider.GatesWithAudit[:2],
				TotalCount: uint64(len(provider.Gates)),
				NextURL:    "/1/gate?min=102&limit=2",
			},
		},
		{
			request: GetGatesRequest{
				FromID: "0",
				Limit:  3,
				Path:   "/1/gate",
			},
			response: GetGatesResponse{
				Gates:      provider.GatesWithAudit[:3],
				TotalCount: uint64(len(provider.Gates)),
				NextURL:    "/1/gate?min=103&limit=3",
			},
		},
		{
			request: GetGatesRequest{
				FromID: "0",
				Limit:  100,
				Path:   "/1/gate",
			},
			response: GetGatesResponse{
				Gates:      provider.GatesWithAudit[:3],
				TotalCount: uint64(len(provider.Gates)),
				NextURL:    "",
			},
		},
	}

	for _, test := range tests {
		response, err := processor.HandleGetGates(context.Background(), test.request)

		require.NoError(t, err)
		require.Equal(t, &test.response, response)
	}
}
