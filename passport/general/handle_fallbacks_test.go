package processor

import (
	"context"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/passport/infra/daemons/yasms_internal/internal/model"
)

type TestCaseGetFallbacks struct {
	request  GetFallbacksRequest
	response GetFallbacksResponse
}

func TestProcessor_HandleGetFallbacks_All(t *testing.T) {
	provider := NewFakeProvider()
	processor, err := NewTestProcessor(provider)
	require.NoError(t, err)

	response, err := processor.HandleGetFallbacks(context.Background(), GetFallbacksRequest{
		FromID: "0",
		Limit:  100,
		Path:   "/1/fallbacks",
	})

	require.NoError(t, err)
	require.Equal(t, &GetFallbacksResponse{
		Fallbacks:  provider.Fallbacks,
		TotalCount: uint64(len(provider.Fallbacks)),
		NextURL:    "",
	}, response)
}

func TestProcessor_HandleFallbacks_Some(t *testing.T) {
	provider := NewFakeProvider()
	processor, err := NewTestProcessor(provider)
	require.NoError(t, err)

	tests := []TestCaseGetFallbacks{
		{
			request: GetFallbacksRequest{
				FromID: "0",
				Limit:  1,
				Path:   "/1/fallbacks",
			},
			response: GetFallbacksResponse{
				Fallbacks:  provider.Fallbacks[:1],
				TotalCount: uint64(len(provider.Fallbacks)),
				NextURL:    "/1/fallbacks?min=33&limit=1",
			},
		},
		{
			request: GetFallbacksRequest{
				FromID: "33",
				Limit:  1,
				Path:   "/1/fallbacks",
			},
			response: GetFallbacksResponse{
				Fallbacks:  provider.Fallbacks[1:],
				TotalCount: uint64(len(provider.Fallbacks)),
				NextURL:    "/1/fallbacks?min=42&limit=1",
			},
		},
		{
			request: GetFallbacksRequest{
				FromID: "42",
				Limit:  1,
				Path:   "/1/fallbacks",
			},
			response: GetFallbacksResponse{
				Fallbacks:  []*model.Fallback{},
				TotalCount: uint64(len(provider.Fallbacks)),
				NextURL:    "",
			},
		},
	}

	for _, test := range tests {
		response, err := processor.HandleGetFallbacks(context.Background(), test.request)

		require.NoError(t, err)
		require.Equal(t, &test.response, response)
	}

}

func TestProcessor_HandleGetFallbacks_Limits(t *testing.T) {
	provider := NewFakeProvider()
	processor, err := NewTestProcessor(provider)
	require.NoError(t, err)

	tests := []TestCaseGetFallbacks{
		{
			request: GetFallbacksRequest{
				FromID: "0",
				Limit:  1,
				Path:   "/1/fallbacks",
			},
			response: GetFallbacksResponse{
				Fallbacks:  provider.Fallbacks[:1],
				TotalCount: uint64(len(provider.Fallbacks)),
				NextURL:    "/1/fallbacks?min=33&limit=1",
			},
		},
		{
			request: GetFallbacksRequest{
				FromID: "0",
				Limit:  2,
				Path:   "/1/fallbacks",
			},
			response: GetFallbacksResponse{
				Fallbacks:  provider.Fallbacks[:2],
				TotalCount: uint64(len(provider.Fallbacks)),
				NextURL:    "/1/fallbacks?min=42&limit=2",
			},
		},
		{
			request: GetFallbacksRequest{
				FromID: "0",
				Limit:  3,
				Path:   "/1/fallbacks",
			},
			response: GetFallbacksResponse{
				Fallbacks:  provider.Fallbacks[:2],
				TotalCount: uint64(len(provider.Fallbacks)),
				NextURL:    "",
			},
		},
	}

	for _, test := range tests {
		response, err := processor.HandleGetFallbacks(context.Background(), test.request)

		require.NoError(t, err)
		require.Equal(t, &test.response, response)
	}
}
