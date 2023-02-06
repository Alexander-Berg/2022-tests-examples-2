package backoff_test

import (
	"errors"
	"math/rand"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/security/libs/go/retry/backoff"
)

var _ backoff.Strategy = (*backoff.ExponentialStrategy)(nil)

func TestExponential(t *testing.T) {
	cases := []struct {
		min    time.Duration
		max    time.Duration
		i      int
		expect time.Duration
	}{
		{
			time.Second,
			time.Minute,
			0,
			time.Second,
		},
		{
			time.Second,
			time.Minute,
			1,
			1682392666,
		},
		{
			time.Second,
			time.Minute,
			2,
			2691828267,
		},
		{
			time.Second,
			time.Minute,
			3,
			4306925227,
		},
		{
			time.Second,
			time.Minute,
			63,
			63089725011,
		},
		{
			time.Second,
			time.Minute,
			128,
			63089725011,
		},
	}

	for _, tc := range cases {
		strategy := backoff.NewExponential(
			tc.min,
			tc.max,
			backoff.WithExponentialRand(rand.New(rand.NewSource(1337))),
		)

		delay := strategy.Delay(errors.New(""), tc.i)
		assert.Equal(t, tc.expect, delay, "bad delay: %#v -> %s", tc, delay)
	}
}
