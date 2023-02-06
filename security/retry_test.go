package retry_test

import (
	"context"
	"errors"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/security/libs/go/retry"
	"a.yandex-team.ru/security/libs/go/retry/backoff"
)

func TestDefaultRetryDefaults(t *testing.T) {
	t.Parallel()
	r := retry.New()
	tries := 0
	err := r.Try(context.Background(), func(ctx context.Context) error {
		tries++
		return errors.New("oops")
	})

	assert.Error(t, err, "expecting error")
	assert.Equal(t, retry.DefaultAttempts, tries, "invalid tries count")
}

func TestNoError(t *testing.T) {
	t.Parallel()
	r := retry.New(
		retry.WithAttempts(3),
		retry.WithBackOff(backoff.NewFixed(0)),
	)

	tries := 0
	err := r.Try(context.Background(), func(ctx context.Context) error {
		tries++
		return nil
	})

	assert.NoError(t, err, "expecting error")
	assert.Equal(t, 1, tries, "invalid tries count")
}

func TestRetryAttempts(t *testing.T) {
	t.Parallel()
	r := retry.New(
		retry.WithAttempts(2),
		retry.WithBackOff(backoff.NewFixed(0)),
	)
	tries := 0
	err := r.Try(context.Background(), func(ctx context.Context) error {
		tries++
		return errors.New("oops")
	})

	assert.Error(t, err, "expecting error")
	assert.Equal(t, 2, tries, "invalid tries count")
}

func TestNopRetry(t *testing.T) {
	t.Parallel()
	r := retry.New(
		retry.WithAttempts(1),
	)
	tries := 0
	err := r.Try(context.Background(), func(ctx context.Context) error {
		tries++
		return errors.New("oops")
	})

	assert.Error(t, err, "expecting error")
	assert.Equal(t, 1, tries, "invalid tries count")
}

type CountedBackOffStrategy struct {
	count  int
	errors []error
}

func (s *CountedBackOffStrategy) Delay(err error, attempt int) time.Duration {
	s.count++
	s.errors = append(s.errors, err)
	return 0
}

func TestCustomBackOff(t *testing.T) {
	t.Parallel()
	backOff := new(CountedBackOffStrategy)
	r := retry.New(
		retry.WithAttempts(3),
		retry.WithBackOff(backOff),
	)

	tries := 0
	expectedErr := errors.New("oops")
	err := r.Try(context.Background(), func(ctx context.Context) error {
		tries++
		return expectedErr
	})

	assert.Error(t, err, "expecting error")
	assert.Equal(t, 3, tries, "invalid tries count")
	assert.Equal(t, 2, backOff.count, "invalid backoff num called")
	for _, err := range backOff.errors {
		assert.Equal(t, expectedErr, err, "invalid error")
	}
}

func TestCondition(t *testing.T) {
	t.Parallel()
	stopped := false
	stopCount := 0
	var stopErr error
	r := retry.New(
		retry.WithAttempts(3),
		retry.WithBackOff(backoff.NewFixed(0)),
		retry.WithCondition(func(err error, attempt int) bool {
			stopCount++
			stopped = true
			stopErr = err
			return false
		}),
	)

	tries := 0
	expectedErr := errors.New("oops")
	err := r.Try(context.Background(), func(ctx context.Context) error {
		tries++
		return expectedErr
	})

	assert.Error(t, err, "expecting error")
	assert.True(t, stopped, "expect RepeatableFunc works!")
	assert.Equal(t, expectedErr, stopErr, "invalid error")
	assert.Equal(t, 1, tries, "invalid tries count")
	assert.Equal(t, 1, stopCount, "invalid stop num called")
}

func TestConditionSkipN(t *testing.T) {
	t.Parallel()
	stopped := false
	stopCount := 0
	var stopErr error
	r := retry.New(
		retry.WithAttempts(3),
		retry.WithBackOff(backoff.NewFixed(0)),
		retry.WithCondition(func(err error, attempt int) bool {
			stopCount++
			if attempt < 1 {
				return true
			}

			stopped = true
			stopErr = err
			return false
		}),
	)

	tries := 0
	expectedErr := errors.New("oops")
	err := r.Try(context.Background(), func(ctx context.Context) error {
		tries++
		return expectedErr
	})

	assert.Error(t, err, "expecting error")
	assert.True(t, stopped, "expect RepeatableFunc works!")
	assert.Equal(t, expectedErr, stopErr, "invalid error")
	assert.Equal(t, 2, tries, "invalid tries count")
	assert.Equal(t, 2, stopCount, "invalid stop num called")
}

func TestConditionError(t *testing.T) {
	t.Parallel()
	r := retry.New(
		retry.WithAttempts(10),
		retry.WithBackOff(backoff.NewFixed(0)),
		retry.WithCondition(func(err error, attempt int) bool {
			return false
		}),
	)

	tries := 0
	err := r.Try(context.Background(), func(ctx context.Context) error {
		tries++
		return errors.New("oops")
	})

	assert.Error(t, err, "expecting error")
	assert.Equal(t, 1, tries, "invalid tries count")
	assert.Equal(t, "oops", err.Error(), "invalid error")
}

func TestError(t *testing.T) {
	t.Parallel()
	r := retry.New(
		retry.WithAttempts(2),
		retry.WithBackOff(backoff.NewFixed(0)),
	)
	tries := 0
	err := r.Try(context.Background(), func(ctx context.Context) error {
		tries++
		return errors.New("oops")
	})

	assert.Error(t, err, "expecting error")
	assert.Equal(t, 2, tries, "invalid tries count")
	assert.Equal(t, "oops", err.Error(), "invalid error")
}

func TestCanceled(t *testing.T) {
	t.Parallel()
	r := retry.New(
		retry.WithAttempts(3000),
	)

	ctx, cancel := context.WithTimeout(context.Background(), 1*time.Second)
	defer cancel()
	tries := 0
	err := r.Try(ctx, func(ctx context.Context) error {
		tries++
		time.Sleep(time.Second)
		return errors.New("oops")
	})

	assert.Error(t, err, "expecting error")
	assert.NotEqual(t, 2000, tries, "invalid tries count")
	assert.Equal(t, context.DeadlineExceeded, err, "invalid error")
}

func TestRetryForever(t *testing.T) {
	t.Parallel()
	r := retry.New(
		retry.WithAttempts(retry.InfinityAttempts),
		retry.WithBackOff(backoff.NewFixed(0)),
	)

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	tries := 0
	err := r.Try(ctx, func(ctx context.Context) error {
		tries++
		return errors.New("oops")
	})

	assert.Error(t, err, "expecting error")
	assert.Greater(t, tries, retry.DefaultAttempts, "invalid tries count")
	assert.Equal(t, context.DeadlineExceeded, err, "invalid error")
}

func TestRetryForeverWithCondition(t *testing.T) {
	t.Parallel()
	r := retry.New(
		retry.WithAttempts(retry.InfinityAttempts),
		retry.WithBackOff(backoff.NewFixed(0)),
		retry.WithCondition(func(err error, attempt int) bool {
			return attempt < 9
		}),
	)

	ctx, cancel := context.WithTimeout(context.Background(), 50*time.Second)
	defer cancel()
	tries := 0
	err := r.Try(ctx, func(ctx context.Context) error {
		tries++
		return errors.New("oops")
	})

	assert.Error(t, err, "expecting error")
	assert.Equal(t, 10, tries, "invalid tries count")
	assert.EqualError(t, err, "oops", "invalid error")
}
