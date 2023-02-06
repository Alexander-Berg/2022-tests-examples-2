package processor

import (
	"context"
	"testing"

	"github.com/stretchr/testify/require"
)

func TestProcessor_HandleEnums(t *testing.T) {
	provider := NewFakeProvider()
	processor, err := NewTestProcessor(provider)
	require.NoError(t, err)

	response, err := processor.HandleRouteEnums(context.Background())

	require.NoError(t, err)
	require.Equal(t, &EnumsResponse{
		Aliases: map[string][]string{
			"some gate101": {"some name101"},
			"some gate102": {"some name102"},
			"some gate103": {"some name103"},
		},
		AlphaNames: map[string][]string{
			"some name101": {"some gate101"},
			"some name102": {"some gate102"},
			"some name103": {"some gate103"},
		},
	}, response)
}
