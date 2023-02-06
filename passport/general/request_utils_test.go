package pushsubscription

import (
	"net/http"
	"net/url"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/passport/infra/daemons/push_subscription/internal/errs"
)

func TestGetRequiredStringParam(t *testing.T) {
	_, err := getRequiredStringParam(url.Values{}, "somekey")
	require.EqualValues(t,
		&errs.InvalidParamError{
			Key:     "somekey",
			Type:    "empty",
			Message: "missing param: 'somekey'",
		},
		err,
	)

	_, err = getRequiredStringParam(url.Values{"somekey": []string{""}}, "somekey")
	require.EqualValues(t,
		&errs.InvalidParamError{
			Key:     "somekey",
			Type:    "empty",
			Message: "missing param: 'somekey'",
		},
		err,
	)

	val, err := getRequiredStringParam(url.Values{"somekey": []string{"somevalue"}}, "somekey")
	require.NoError(t, err)
	require.EqualValues(t, "somevalue", val)
}

func TestGetRequiredUIntParam(t *testing.T) {
	_, err := getRequiredUIntParam(url.Values{}, "somekey")
	require.EqualValues(t,
		&errs.InvalidParamError{
			Key:     "somekey",
			Type:    "empty",
			Message: "invalid param: 'somekey' must be unsigned int, got ''",
		},
		err,
	)

	_, err = getRequiredUIntParam(url.Values{"somekey": []string{"somevalue"}}, "somekey")
	require.EqualValues(t,
		&errs.InvalidParamError{
			Key:     "somekey",
			Type:    "invalid",
			Message: "invalid param: 'somekey' must be unsigned int, got 'somevalue'",
		},
		err,
	)

	val, err := getRequiredUIntParam(url.Values{"somekey": []string{"143"}}, "somekey")
	require.NoError(t, err)
	require.EqualValues(t, uint64(143), val)
}

func TestGetOptionalBoolParam(t *testing.T) {
	val, err := getOptionalBoolParam(url.Values{}, "somekey")
	require.NoError(t, err)
	require.Nil(t, val)

	val, err = getOptionalBoolParam(url.Values{"somekey": []string{"kek"}}, "somekey")
	require.EqualValues(t,
		&errs.InvalidParamError{
			Key:     "somekey",
			Type:    "invalid",
			Message: "invalid param: 'somekey' must be boolean, got 'kek'",
		},
		err,
	)
	require.Nil(t, val)

	val, err = getOptionalBoolParam(url.Values{"somekey": []string{"False"}}, "somekey")
	require.NoError(t, err)
	require.False(t, *val)

	val, err = getOptionalBoolParam(url.Values{"somekey": []string{"true"}}, "somekey")
	require.NoError(t, err)
	require.True(t, *val)
}

func TestGetDefaultBoolParam(t *testing.T) {
	val, err := getDefaultBoolParam(url.Values{}, "somekey", true)
	require.NoError(t, err)
	require.True(t, val)

	val, err = getDefaultBoolParam(url.Values{}, "somekey", false)
	require.NoError(t, err)
	require.False(t, val)

	val, err = getDefaultBoolParam(url.Values{"somekey": []string{"kek"}}, "somekey", false)
	require.EqualValues(t,
		&errs.InvalidParamError{
			Key:     "somekey",
			Type:    "invalid",
			Message: "invalid param: 'somekey' must be boolean, got 'kek'",
		},
		err,
	)
	require.False(t, val)

	val, err = getDefaultBoolParam(url.Values{"somekey": []string{"true"}}, "somekey", false)
	require.NoError(t, err)
	require.True(t, val)
	val, err = getDefaultBoolParam(url.Values{"somekey": []string{"false"}}, "somekey", false)
	require.NoError(t, err)
	require.False(t, val)
	val, err = getDefaultBoolParam(url.Values{"somekey": []string{"true"}}, "somekey", true)
	require.NoError(t, err)
	require.True(t, val)
	val, err = getDefaultBoolParam(url.Values{"somekey": []string{"false"}}, "somekey", true)
	require.NoError(t, err)
	require.False(t, val)
}

func TestGetRequiredHeader(t *testing.T) {
	_, err := getRequiredHeader(
		http.Header{},
		"Ya-Consumer-Client-Ip",
		"displayablekey",
	)
	require.EqualValues(t,
		&errs.InvalidParamError{
			Key:     "displayablekey",
			Type:    "empty",
			Message: "missing header: 'Ya-Consumer-Client-Ip'",
		},
		err,
	)

	val, err := getRequiredHeader(
		http.Header{"Ya-Consumer-Client-Ip": []string{"kek"}},
		"Ya-Consumer-Client-Ip",
		"displayablekey",
	)
	require.NoError(t, err)
	require.EqualValues(t, "kek", val)
}
