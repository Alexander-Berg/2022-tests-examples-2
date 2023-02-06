package backoff_test

import (
	"errors"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/security/libs/go/retry/backoff"
)

var _ backoff.Strategy = (*backoff.ExponentialStrategy)(nil)

func TestFixedBackOff(t *testing.T) {
	cases := []struct {
		delay  time.Duration
		i      int
		expect time.Duration
	}{
		{
			time.Second,
			0,
			time.Second,
		},
		{
			time.Second,
			1,
			time.Second,
		},
		{
			time.Second,
			2,
			time.Second,
		},
		{
			time.Second,
			3,
			time.Second,
		},
		{
			time.Second,
			30,
			time.Second,
		},
	}

	for _, tc := range cases {
		delay := backoff.NewFixed(tc.delay).Delay(errors.New(""), tc.i)
		assert.Equal(t, tc.expect, delay, "bad delay for attempt: %d", tc.i)
	}
}
