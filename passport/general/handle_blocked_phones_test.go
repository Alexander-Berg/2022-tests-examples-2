package processor

import (
	"context"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/passport/infra/daemons/yasms_internal/internal/model"
)

type TestCaseGetBlockedPhones struct {
	request  GetBlockedPhonesRequest
	response GetBlockedPhonesResponse
}

func TestProcessor_HandleGetBlockedPhones_All(t *testing.T) {
	provider := NewFakeProvider()
	processor, err := NewTestProcessor(provider)
	require.NoError(t, err)

	response, err := processor.HandleGetBlockedPhones(context.Background(), GetBlockedPhonesRequest{
		FromID: "0",
		Limit:  100,
		Path:   "/1/blockedphones",
	})

	require.NoError(t, err)
	require.Equal(t, &GetBlockedPhonesResponse{
		BlockedPhones: provider.BlockedPhones,
		TotalCount:    uint64(len(provider.BlockedPhones)),
		NextURL:       "",
	}, response)
}

func TestProcessor_HandleBlockedPhones_Some(t *testing.T) {
	provider := NewFakeProvider()
	processor, err := NewTestProcessor(provider)
	require.NoError(t, err)

	tests := []TestCaseGetBlockedPhones{
		{
			request: GetBlockedPhonesRequest{
				FromID: "0",
				Limit:  1,
				Path:   "/1/blockedphones",
			},
			response: GetBlockedPhonesResponse{
				BlockedPhones: provider.BlockedPhones[:1],
				TotalCount:    uint64(len(provider.BlockedPhones)),
				NextURL:       "/1/blockedphones?min=54&limit=1",
			},
		},
		{
			request: GetBlockedPhonesRequest{
				FromID: "54",
				Limit:  1,
				Path:   "/1/blockedphones",
			},
			response: GetBlockedPhonesResponse{
				BlockedPhones: provider.BlockedPhones[1:],
				TotalCount:    uint64(len(provider.BlockedPhones)),
				NextURL:       "/1/blockedphones?min=55&limit=1",
			},
		},
		{
			request: GetBlockedPhonesRequest{
				FromID: "55",
				Limit:  1,
				Path:   "/1/blockedphones",
			},
			response: GetBlockedPhonesResponse{
				BlockedPhones: []*model.BlockedPhone{},
				TotalCount:    uint64(len(provider.BlockedPhones)),
				NextURL:       "",
			},
		},
	}

	for _, test := range tests {
		response, err := processor.HandleGetBlockedPhones(context.Background(), test.request)

		require.NoError(t, err)
		require.Equal(t, &test.response, response)
	}

}

func TestProcessor_HandleGetBlockedPhones_Limits(t *testing.T) {
	provider := NewFakeProvider()
	processor, err := NewTestProcessor(provider)
	require.NoError(t, err)

	tests := []TestCaseGetBlockedPhones{
		{
			request: GetBlockedPhonesRequest{
				FromID: "0",
				Limit:  1,
				Path:   "/1/blockedphones",
			},
			response: GetBlockedPhonesResponse{
				BlockedPhones: provider.BlockedPhones[:1],
				TotalCount:    uint64(len(provider.BlockedPhones)),
				NextURL:       "/1/blockedphones?min=54&limit=1",
			},
		},
		{
			request: GetBlockedPhonesRequest{
				FromID: "0",
				Limit:  2,
				Path:   "/1/blockedphones",
			},
			response: GetBlockedPhonesResponse{
				BlockedPhones: provider.BlockedPhones[:2],
				TotalCount:    uint64(len(provider.BlockedPhones)),
				NextURL:       "/1/blockedphones?min=55&limit=2",
			},
		},
		{
			request: GetBlockedPhonesRequest{
				FromID: "0",
				Limit:  3,
				Path:   "/1/blockedphones",
			},
			response: GetBlockedPhonesResponse{
				BlockedPhones: provider.BlockedPhones[:2],
				TotalCount:    uint64(len(provider.BlockedPhones)),
				NextURL:       "",
			},
		},
	}

	for _, test := range tests {
		response, err := processor.HandleGetBlockedPhones(context.Background(), test.request)

		require.NoError(t, err)
		require.Equal(t, &test.response, response)
	}
}
