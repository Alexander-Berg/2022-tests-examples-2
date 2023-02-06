package sshutil_test

import (
	"testing"
	"time"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/security/skotty/robossh/internal/sshutil"
)

func TestDuration(t *testing.T) {
	cases := []struct {
		input    string
		expected time.Duration
		err      bool
	}{
		{
			input:    "",
			expected: 0,
		},
		{
			input:    "0",
			expected: 0,
		},
		{
			input:    "600",
			expected: 600 * time.Second,
		},
		{
			input:    "600s",
			expected: 600 * time.Second,
		},
		{
			input:    "600S",
			expected: 600 * time.Second,
		},
		{
			input:    "10m",
			expected: 10 * time.Minute,
		},
		{
			input:    "10M",
			expected: 10 * time.Minute,
		},
		{
			input:    "1h30m",
			expected: 90 * time.Minute,
		},
		{
			input:    "1H30m",
			expected: 90 * time.Minute,
		},
		{
			input:    "1w2h28m",
			expected: (7 * 24 * time.Hour) + 2*time.Hour + 28*time.Minute,
		},
		{
			input:    "1W2H28M",
			expected: (7 * 24 * time.Hour) + 2*time.Hour + 28*time.Minute,
		},
		{
			input: "1w2h28m12",
			err:   true,
		},
		{
			input: "1y",
			err:   true,
		},
		{
			input: "s",
			err:   true,
		},
		{
			input: "-1s",
			err:   true,
		},
		{
			input: "+1s",
			err:   true,
		},
	}

	for _, tc := range cases {
		t.Run(tc.input, func(t *testing.T) {
			actual, err := sshutil.ParseDuration(tc.input)
			if tc.err {
				require.Error(t, err)
				return
			}

			require.NoError(t, err)
			require.Equal(t, tc.expected, actual)
		})
	}
}
