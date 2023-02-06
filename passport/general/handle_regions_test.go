package processor

import (
	"context"
	"testing"

	"github.com/stretchr/testify/require"
)

func TestProcessor_HandleGetRegions(t *testing.T) {
	provider := NewFakeProvider()
	processor, err := NewTestProcessor(provider)
	require.NoError(t, err)

	response, err := processor.HandleGetRegions(context.Background(), GetRegionsRequest{})
	require.NoError(t, err)
	require.Equal(t, provider.Regions, response.Regions)
}
