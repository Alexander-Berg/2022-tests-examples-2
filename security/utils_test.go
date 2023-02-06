package utils

import (
	"net"
	"strings"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/security/debby/targets/internal/models"
)

func TestExtractProjectID(t *testing.T) {
	ip := "2a02:06b8:0c12:5499:0000:47a2:9191:5294"
	expectedProjectID := "47a2"
	actualProjectID := extractProjectID(net.ParseIP(ip))
	require.Equal(t, expectedProjectID, actualProjectID)
}

func TestIsIPv6(t *testing.T) {
	res := IsIPv6(net.ParseIP("2a02:06b8:0c12:5499:0000:47a2:9191:5294"))
	require.True(t, res, "IPv6 parsing fail")
	res = IsIPv6(net.ParseIP("192.168.0.1"))
	require.False(t, res, "IPv6 parsing fail")
}

func TestRemainOnlyKnownIPV6Targets(t *testing.T) {
	knownTargets := []models.Target{
		models.Parse("2a02:06b8:0c12:5499:0000:47a2:9191:5294"),
		models.Parse("2a02:06b8:0c12:5499:0000:47a1:9191:5294"),
	}
	allTargets := []models.Target{
		models.Parse("47a2@2a02:6b8:c00::/40"),
		models.Parse("47a3@2a02:6b8:c00::/40"),
	}
	res := RemainOnlyKnownIPV6Targets(knownTargets, allTargets)
	require.Equal(t, 1, len(res))
}

func TestDumpsTargets(t *testing.T) {
	inputs := []string{
		"192.168.0.1",
		"2a02:6b8:a::a",
		"192.168.0.1/24",
		"2a02:6b8:a::a/48",
		"47a2@2a02:6b8:c00::/40",
		"debby.sec.yandex-team.ru",
	}
	expectedOutputs := []string{
		"192.168.0.1",
		"2a02:6b8:a::a",
		"192.168.0.0/24",
		"2a02:6b8:a::/48",
		"47a2@2a02:6b8:c00::/40",
		"debby.sec.yandex-team.ru",
	}
	targets := make([]models.Target, len(inputs))
	for i, input := range inputs {
		targets[i] = models.Parse(input)
	}
	res := DumpsTargets(targets)
	actualOutputs := strings.Split(res, ",")
	for _, expected := range expectedOutputs {
		found := false
		for _, actual := range actualOutputs {
			if strings.Compare(expected, actual) == 0 {
				found = true
				break
			}
		}
		if !found {
			t.Errorf("DumpsTargets failed. got '%s', want '%s'.", expectedOutputs, actualOutputs)
		}
	}
}

func TestIsMacroAcceptable(t *testing.T) {
	tables := []struct {
		macro      string
		acceptable []string
		result     bool
	}{
		{"1", []string{"2", "3"}, false},
		{"1", []string{"1", "3"}, true},
		{"1", []string{"1"}, true},
		{"1", []string{"3"}, false},
	}

	for _, table := range tables {
		require.Equal(t, table.result, IsMacroAcceptable(table.macro, table.acceptable))
	}
}

func TestRemainUniqueTargets(t *testing.T) {
	targets := []models.Target{
		models.Parse("192.168.0.1"),
		models.Parse("192.168.0.2"),
		models.Parse("192.168.0.3"),
		models.Parse("192.168.0.1"),
	}
	expectedOutputs := []string{
		"192.168.0.1",
		"192.168.0.2",
		"192.168.0.3",
	}
	unique := RemainUniqueTargets(targets)
	res := DumpsTargets(unique)
	actualOutputs := strings.Split(res, ",")

	for _, expected := range expectedOutputs {
		found := false
		for _, actual := range actualOutputs {
			if strings.Compare(expected, actual) == 0 {
				found = true
				break
			}
		}
		if !found {
			t.Errorf("DumpsTargets failed. got '%s', want '%s'.", expectedOutputs, actualOutputs)
		}
	}
}
