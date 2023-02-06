package cvs_test

import (
	"fmt"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/security/yadi/libs/cvs"
)

func TestToSeverity(t *testing.T) {
	var cases = []struct {
		score float32
		name  string
	}{
		{-1.0, "None"},
		{0.0, "None"},
		{0.9, "None"},
		{1.0, "Low"},
		{3.9, "Low"},
		{4.0, "Medium"},
		{6.9, "Medium"},
		{7.0, "High"},
		{8.9, "High"},
		{9.0, "Critical"},
		{10.0, "Critical"},
		{12.0, "Critical"},
	}

	for _, tc := range cases {
		t.Run(fmt.Sprint(tc.score), func(t *testing.T) {
			actualName := cvs.ToSeverity(tc.score)
			assert.Equal(t, tc.name, actualName)
		})
	}
}

func TestFromSeverity(t *testing.T) {
	var cases = []struct {
		severity string
		score    float32
	}{
		{"Low", 1.0},
		{"Medium", 4.0},
		{"High", 7.0},
		{"Critical", 9.0},
	}

	for _, tc := range cases {
		t.Run(tc.severity, func(t *testing.T) {
			actualScore, err := cvs.FromSeverity(tc.severity)
			require.NoError(t, err)
			assert.Equal(t, tc.score, actualScore)
		})
	}
}

func TestFromLevel(t *testing.T) {
	var cases = []struct {
		level int
		score float32
	}{
		{0, cvs.DefaultSeverity},
		{1, cvs.LowSeverity},
		{2, cvs.MediumSeverity},
		{3, cvs.HighSeverity},
		{4, cvs.CriticalSeverity},
	}

	for _, tc := range cases {
		t.Run(fmt.Sprint(tc.level), func(t *testing.T) {
			actualScore, err := cvs.FromLevel(tc.level)
			require.NoError(t, err)
			assert.Equal(t, tc.score, actualScore)
		})
	}
}
