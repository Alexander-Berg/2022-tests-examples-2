package ytc

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestTableTtlConfig(t *testing.T) {
	secondsInMonth := uint64(30 * 24 * 60 * 60)
	now := uint64(1656622800)

	cfg := TablesTTLConfig{
		UsersHistory:     6 * secondsInMonth,
		CorpUsersHistory: 3 * secondsInMonth,
		Push:             secondsInMonth,
		Auths:            secondsInMonth,
		FutureFrontier:   secondsInMonth,
	}

	require.Equal(t, 6*secondsInMonth, cfg.chooseUsersHistoryTTL(false))
	require.Equal(t, 3*secondsInMonth, cfg.chooseUsersHistoryTTL(true))

	require.Equal(t, now-secondsInMonth, cfg.getFromTS(0, cfg.Push, now))
	require.Equal(t, now, cfg.getFromTS(now, cfg.Push, now))

	require.Equal(t, now+secondsInMonth, cfg.getToTS(now+2*secondsInMonth, now))
	require.Equal(t, now, cfg.getToTS(now, now))
}
