package base

import (
	"io"
	"strings"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/portal/avocado/libs/utils/errors/v3"
	"a.yandex-team.ru/portal/avocado/libs/utils/log3"
	"a.yandex-team.ru/portal/avocado/libs/utils/time"
)

func makeWriterIntoWriteCloser(writer io.Writer) io.WriteCloser {
	return writeWriteCloser{
		Writer: writer,
	}
}

type writeWriteCloser struct {
	io.Writer
}

func (w writeWriteCloser) Close() error {
	return nil
}

func Test_delayedLogger(t *testing.T) {
	var testBuffer strings.Builder
	var controlBuffer strings.Builder

	var testLogger, controlLogger log3.LoggerAlterable
	var err error

	timeProvider := time.NewTimeProviderStub()

	testLogger, err = log3.NewLogger(
		log3.WithWriteCloser(makeWriterIntoWriteCloser(&testBuffer)),
		log3.WithCritHandler(nil),
		log3.WithTimeProvider(timeProvider),
	)
	require.NoError(t, err)

	controlLogger, err = log3.NewLogger(
		log3.WithWriteCloser(makeWriterIntoWriteCloser(&controlBuffer)),
		log3.WithCritHandler(nil),
		log3.WithTimeProvider(timeProvider),
	)
	require.NoError(t, err)

	err = errors.Errorf("some error")

	loggingRoutine := func(logger log3.LoggerAlterable) {
		logger.Error(err)
		logger = logger.Alter(log3.WithAddedExtraInfo(map[string]interface{}{
			"key": "value",
		}))
		logger.Warn(err)
	}

	alteringOptions := []log3.OptionAlter{
		log3.WithAddedExtraInfo(map[string]interface{}{
			"other key": "other value",
		}),
	}

	mutableTestLogger := newLoggerMutable(testLogger)
	mutableControlLogger := newLoggerMutable(controlLogger)

	delayedTestLogger := newDelayedLogger(mutableTestLogger)

	loggingRoutine(delayedTestLogger)
	mutableTestLogger.Clarify(alteringOptions...)
	mutableControlLogger.Clarify(alteringOptions...)
	loggingRoutine(mutableControlLogger)

	delayedTestLogger.Resolve()
	assert.Equal(t, controlBuffer.String(), testBuffer.String())
}
