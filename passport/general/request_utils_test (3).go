package handlers

import (
	"net/url"
	"testing"

	"github.com/stretchr/testify/require"
)

func TestGetRequiredStringParam(t *testing.T) {
	_, err := getRequiredStringParam(url.Values{}, "foo")
	require.EqualError(t, err, "missing parameter 'foo'")

	_, err = getRequiredStringParam(
		url.Values{
			"foo": []string{},
		},
		"foo",
	)
	require.EqualError(t, err, "missing parameter 'foo'")

	val, err := getRequiredStringParam(
		url.Values{
			"foo": []string{"bar"},
		},
		"foo",
	)
	require.NoError(t, err)
	require.EqualValues(t, "bar", val)
}
