package pushsubscription

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestGetTokenFromAuthHeader(t *testing.T) {
	_, err := getTokenFromAuthHeader("sometoken")
	require.ErrorContains(t, err, "header has incorrect parts count: expected=2, actual=1")
	_, err = getTokenFromAuthHeader("ekek sometoken lol")
	require.ErrorContains(t, err, "header has incorrect parts count: expected=2, actual=3")

	_, err = getTokenFromAuthHeader("kek sometoken")
	require.ErrorContains(t, err, "got unsupported auth type: 'kek'")

	res, err := getTokenFromAuthHeader("oauth sometoken")
	require.NoError(t, err)
	require.EqualValues(t, "sometoken", res)

	res, err = getTokenFromAuthHeader("OAuth sometoken")
	require.NoError(t, err)
	require.EqualValues(t, "sometoken", res)
}
