package podresolver_test

import (
	"context"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/core/log/nop"
	"a.yandex-team.ru/security/gideon/fake-iss/isstest"
	"a.yandex-team.ru/security/gideon/gideon/internal/podresolver"
)

func TestListYpPods(t *testing.T) {
	expectedPods := []podresolver.PodInfo{
		{
			Kind:      podresolver.PodKindYp,
			ID:        "fn3utw2xamszrlbv",
			Container: "ISS-AGENT--fn3utw2xamszrlbv",
			PodSetID:  "cleanweb-synchronous-prod.rpc",
		},
		{
			Kind:           podresolver.PodKindNanny,
			ID:             "strm-trns-agent-testing-2",
			Container:      "ISS-AGENT--strm-trns-agent-testing-2",
			PodSetID:       "strm-trns-agent-testing",
			NannyServiceID: "strm_trns_agent_testing",
		},
	}

	issSrv := isstest.NewServer(&nop.Logger{})
	defer issSrv.Close()

	client, err := podresolver.NewResolver(podresolver.WithUpstream(issSrv.URL))
	require.NoError(t, err)

	issPods, err := client.ListYpPods(context.Background())
	require.NoError(t, err)

	require.ElementsMatch(t, expectedPods, issPods)
}

func TestListGenCfgInstances(t *testing.T) {
	expectedPods := []podresolver.PodInfo{
		{
			Kind:           podresolver.PodKindNanny,
			ID:             "25014",
			Container:      "ISS-AGENT--25014",
			NannyServiceID: "production_market_ir_ui_sas",
		},
	}

	issSrv := isstest.NewServer(&nop.Logger{})
	defer issSrv.Close()

	client, err := podresolver.NewResolver(podresolver.WithUpstream(issSrv.URL))
	require.NoError(t, err)

	issPods, err := client.ListNannyInstances(context.Background())
	require.NoError(t, err)

	require.ElementsMatch(t, expectedPods, issPods)
}

func TestSync(t *testing.T) {
	excludedPods := []podresolver.PodInfo{
		{
			Kind:      podresolver.PodKindYp,
			ID:        "fn3utw2xamszrlbv",
			Container: "ISS-AGENT--fn3utw2xamszrlbv",
			PodSetID:  "cleanweb-synchronous-prod.rpc",
		},
		{
			Kind:           podresolver.PodKindNanny,
			ID:             "25014",
			Container:      "ISS-AGENT--25014",
			NannyServiceID: "production_market_ir_ui_sas",
		},
	}

	expectedPods := []podresolver.PodInfo{
		{
			Kind:           podresolver.PodKindNanny,
			ID:             "strm-trns-agent-testing-2",
			Container:      "ISS-AGENT--strm-trns-agent-testing-2",
			PodSetID:       "strm-trns-agent-testing",
			NannyServiceID: "strm_trns_agent_testing",
		},
	}

	allPods := append(expectedPods, excludedPods...)

	issSrv := isstest.NewServer(&nop.Logger{})
	defer issSrv.Close()

	client, err := podresolver.NewResolver(podresolver.WithUpstream(issSrv.URL))
	require.NoError(t, err)

	client.Sync(context.Background())

	// check that all pods exists
	require.ElementsMatch(t, allPods, client.CachedPods())

	// now delete something
	issSrv.ExcludeSlotID("25014")
	issSrv.ExcludePodID("fn3utw2xamszrlbv")

	// and resync
	client.Sync(context.Background())
	require.ElementsMatch(t, expectedPods, client.CachedPods())
}

func TestSyncErrous(t *testing.T) {
	expectedPods := []podresolver.PodInfo{
		{
			Kind:      podresolver.PodKindYp,
			ID:        "fn3utw2xamszrlbv",
			Container: "ISS-AGENT--fn3utw2xamszrlbv",
			PodSetID:  "cleanweb-synchronous-prod.rpc",
		},
		{
			Kind:           podresolver.PodKindNanny,
			ID:             "strm-trns-agent-testing-2",
			Container:      "ISS-AGENT--strm-trns-agent-testing-2",
			PodSetID:       "strm-trns-agent-testing",
			NannyServiceID: "strm_trns_agent_testing",
		},
		{
			Kind:           podresolver.PodKindNanny,
			ID:             "25014",
			Container:      "ISS-AGENT--25014",
			NannyServiceID: "production_market_ir_ui_sas",
		},
	}

	issSrv := isstest.NewServer(&nop.Logger{})
	defer issSrv.Close()

	client, err := podresolver.NewResolver(podresolver.WithUpstream(issSrv.URL))
	require.NoError(t, err)

	client.Sync(context.Background())

	// check that all pods exists
	require.ElementsMatch(t, expectedPods, client.CachedPods())

	// stops ISS
	issSrv.Close()

	// and resync
	client.Sync(context.Background())
	require.ElementsMatch(t, expectedPods, client.CachedPods())
}

func TestSyncYpOnly(t *testing.T) {
	expectedPods := []podresolver.PodInfo{
		{
			Kind:      podresolver.PodKindYp,
			ID:        "fn3utw2xamszrlbv",
			Container: "ISS-AGENT--fn3utw2xamszrlbv",
			PodSetID:  "cleanweb-synchronous-prod.rpc",
		},
		{
			Kind:           podresolver.PodKindNanny,
			ID:             "strm-trns-agent-testing-2",
			Container:      "ISS-AGENT--strm-trns-agent-testing-2",
			PodSetID:       "strm-trns-agent-testing",
			NannyServiceID: "strm_trns_agent_testing",
		},
	}

	issSrv := isstest.NewServer(&nop.Logger{})
	defer issSrv.Close()

	client, err := podresolver.NewResolver(podresolver.WithUpstream(issSrv.URL))
	require.NoError(t, err)

	issSrv.ExcludeSlotID("25014")

	client.Sync(context.Background())

	require.ElementsMatch(t, expectedPods, client.CachedPods())
}

func TestSyncGenCfgOnly(t *testing.T) {
	expectedPods := []podresolver.PodInfo{
		{
			Kind:           podresolver.PodKindNanny,
			ID:             "25014",
			Container:      "ISS-AGENT--25014",
			NannyServiceID: "production_market_ir_ui_sas",
		},
	}

	issSrv := isstest.NewServer(&nop.Logger{})
	defer issSrv.Close()

	client, err := podresolver.NewResolver(podresolver.WithUpstream(issSrv.URL))
	require.NoError(t, err)

	issSrv.ExcludePodID("fn3utw2xamszrlbv")
	issSrv.ExcludePodID("strm-trns-agent-testing-2")

	client.Sync(context.Background())

	require.ElementsMatch(t, expectedPods, client.CachedPods())
}
