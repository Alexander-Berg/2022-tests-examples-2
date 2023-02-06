package snapshot

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/core/log/nop"
	"a.yandex-team.ru/noc/go/metrics"
	"a.yandex-team.ru/noc/topka/pkg/internal/topka/juggler"
)

func TestJuggler(t *testing.T) {
	jugglerCfg := &juggler.PushClientConfig{}
	jugglerCfg.EventHost = "abacaba"
	metric, err := metrics.New(&metrics.Config{}, &nop.Logger{})
	require.NoError(t, err)
	juggler := juggler.NewPushClient(jugglerCfg, metric, &nop.Logger{})

	alerts := makeAlerts(juggler)

	assert.Equal(t, "valve_verdict", alerts.PerFW[TypeHBF].ValveVerdictPresent.Service())
	assert.Equal(t, []string{"hbf", "rules_generation", "mondata_help_topka_valve_verdict"}, alerts.PerFW[TypeHBF].ValveVerdictPresent.Tags())
	assert.Equal(t, "valve_verdict_slb", alerts.PerFW[TypeSLB].ValveVerdictPresent.Service())
	assert.Equal(t, []string{"slb", "rules_generation", "mondata_help_topka_valve_verdict"}, alerts.PerFW[TypeSLB].ValveVerdictPresent.Tags())

	assert.Equal(t, "snapshot_diff_hbf", alerts.PerFW[TypeHBF].FWDiff.Service())
	assert.Equal(t, []string{"hbf", "rules_generation", "mondata_help_topka_diff"}, alerts.PerFW[TypeHBF].FWDiff.Tags())
	assert.Equal(t, "snapshot_diff_slb", alerts.PerFW[TypeSLB].FWDiff.Service())
	assert.Equal(t, []string{"slb", "rules_generation", "mondata_help_topka_diff"}, alerts.PerFW[TypeSLB].FWDiff.Tags())
}
