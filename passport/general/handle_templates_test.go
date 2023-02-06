package processor

import (
	"context"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/passport/infra/daemons/yasms_internal/internal/model"
)

type TestCaseGetTemplates struct {
	request  GetTemplatesRequest
	response GetTemplatesResponse
}

func TestProcessor_HandleGetTemplates_All(t *testing.T) {
	provider := NewFakeProvider()
	processor, err := NewTestProcessor(provider)
	require.NoError(t, err)

	response, err := processor.HandleGetTemplates(context.Background(), GetTemplatesRequest{
		FromID: "0",
		Limit:  100,
		Path:   "/1/templates",
	})

	require.NoError(t, err)
	require.Equal(t, &GetTemplatesResponse{
		Templates:  provider.Templates,
		TotalCount: uint64(len(provider.Templates)),
		NextURL:    "",
	}, response)
}

func TestProcessor_HandleGetTemplates_Some(t *testing.T) {
	provider := NewFakeProvider()
	processor, err := NewTestProcessor(provider)
	require.NoError(t, err)

	tests := []TestCaseGetTemplates{
		{
			request: GetTemplatesRequest{
				FromID: "1",
				Limit:  1,
				Path:   "/1/templates",
			},
			response: GetTemplatesResponse{
				Templates:  provider.Templates[1:],
				TotalCount: uint64(len(provider.Templates)),
				NextURL:    "/1/templates?min=2&limit=1",
			},
		},
		{
			request: GetTemplatesRequest{
				FromID: "55",
				Limit:  1,
				Path:   "/1/templates",
			},
			response: GetTemplatesResponse{
				Templates:  []*model.Template{},
				TotalCount: uint64(len(provider.Templates)),
				NextURL:    "",
			},
		},
	}

	for _, test := range tests {
		response, err := processor.HandleGetTemplates(context.Background(), test.request)

		require.NoError(t, err)
		require.Equal(t, &test.response, response)
	}

}

func TestProcessor_HandleGetTemplates_Limits(t *testing.T) {
	provider := NewFakeProvider()
	processor, err := NewTestProcessor(provider)
	require.NoError(t, err)

	tests := []TestCaseGetTemplates{
		{
			request: GetTemplatesRequest{
				FromID: "0",
				Limit:  1,
				Path:   "/1/templates",
			},
			response: GetTemplatesResponse{
				Templates:  provider.Templates[:1],
				TotalCount: uint64(len(provider.Templates)),
				NextURL:    "/1/templates?min=1&limit=1",
			},
		},
		{
			request: GetTemplatesRequest{
				FromID: "0",
				Limit:  3,
				Path:   "/1/templates",
			},
			response: GetTemplatesResponse{
				Templates:  provider.Templates[:2],
				TotalCount: uint64(len(provider.Templates)),
				NextURL:    "",
			},
		},
	}

	for _, test := range tests {
		response, err := processor.HandleGetTemplates(context.Background(), test.request)

		require.NoError(t, err)
		require.Equal(t, &test.response, response)
	}
}
