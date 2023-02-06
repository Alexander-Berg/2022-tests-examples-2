package utils

import (
	"encoding/json"
	"testing"
	"time"

	"github.com/stretchr/testify/require"
)

func TestDuration_MarshalJSON(t *testing.T) {
	d := Duration{
		Duration: 129 * time.Second,
	}
	res, err := json.Marshal(d)
	require.NoError(t, err)
	require.NoError(t, json.Unmarshal(res, &d))
	require.Equal(t, 129*time.Second, d.Duration)
}

func TestDuration_UnmarshalJSON(t *testing.T) {
	d := Duration{}
	require.NoError(t, json.Unmarshal([]byte(`"300s"`), &d))
	require.Equal(t, 300*time.Second, d.Duration)
	require.NoError(t, json.Unmarshal([]byte(`"200h"`), &d))
	require.Equal(t, 200*time.Hour, d.Duration)
	require.Error(t, json.Unmarshal([]byte(`5s`), &d))

	type K struct {
		D Duration
	}
	k := K{}
	require.NoError(t, json.Unmarshal([]byte(`{"d": "123ms"}`), &k))
	require.Equal(t, K{D: Duration{Duration: 123 * time.Millisecond}}, k)
}
