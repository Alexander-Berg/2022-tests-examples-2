package actions

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/noc/nalivkin/internal/client/racktables"
)

type mockPnsGetter []racktables.PnsLog

func (m mockPnsGetter) GetPnsLogs(_ctx context.Context, _objectID int, limit int, _timeLimitSecs int) ([]racktables.PnsLog, error) {
	return m, nil
}

func TestPnsPollerEmpty(t *testing.T) {
	ctx := context.Background()
	poller := newPnsLogPoller()
	var toLog []string
	toLog, _ = poller.Poll(ctx, 0, mockPnsGetter{
		racktables.PnsLog{},
	})
	assert.False(t, poller.Finished())
	assert.Equal(t, []string{}, toLog)
}

func TestPnsPollerTwoLinesSameID(t *testing.T) {
	ctx := context.Background()
	poller := newPnsLogPoller()
	var toLog []string
	toLog, _ = poller.Poll(ctx, 0, mockPnsGetter{
		racktables.PnsLog{
			ID:   1,
			Text: "First line\n",
		},
	})
	assert.False(t, poller.Finished())
	assert.Equal(t, []string{"First line\n"}, toLog)

	toLog, _ = poller.Poll(ctx, 0, mockPnsGetter{
		racktables.PnsLog{
			ID:   1,
			Text: "First line\nSecond line\n",
		},
	})
	assert.False(t, poller.Finished())
	assert.Equal(t, []string{"Second line\n"}, toLog)
}

func TestPnsPollerTwoIDs(t *testing.T) {
	ctx := context.Background()
	poller := newPnsLogPoller()
	var toLog []string
	toLog, _ = poller.Poll(ctx, 0, mockPnsGetter{
		racktables.PnsLog{
			ID:   1,
			Text: "First line of first entry\n",
		},
	})
	assert.False(t, poller.Finished())
	assert.Equal(t, []string{"First line of first entry\n"}, toLog)

	toLog, _ = poller.Poll(ctx, 0, mockPnsGetter{
		racktables.PnsLog{
			ID:   2,
			Text: "First line of second entry\n",
		},
		racktables.PnsLog{
			ID:   1,
			Text: "First line of first entry\nSecond line of first entry\n",
		},
	})
	assert.False(t, poller.Finished())
	assert.Equal(t, []string{"Second line of first entry\n", "First line of second entry\n"}, toLog)
}

func TestPnsPollerFinished(t *testing.T) {
	ctx := context.Background()
	poller := newPnsLogPoller()
	var toLog []string
	toLog, _ = poller.Poll(ctx, 0, mockPnsGetter{
		racktables.PnsLog{
			ID:   1,
			Text: "First and last entry\n",
			Type: racktables.PnsLogType("успешная наливка"),
		},
	})
	assert.True(t, poller.Finished(), "Success not detected")
	assert.Equal(t, []string{"First and last entry\n"}, toLog)
}
