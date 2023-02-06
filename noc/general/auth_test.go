package dependencies

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestUnauthorizedError(t *testing.T) {
	description := "Error description"
	var err error = &UnauthorizedError{Description: description}
	require.Equal(t, description, err.Error())
}
