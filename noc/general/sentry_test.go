package errorbooster

import (
	"context"
	"encoding/json"
	"testing"
	"time"

	"github.com/getsentry/sentry-go"
	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/require"
	"github.com/stretchr/testify/suite"

	"a.yandex-team.ru/kikimr/public/sdk/go/persqueue"
	"a.yandex-team.ru/library/go/core/log"
	"a.yandex-team.ru/library/go/core/log/nop"
	"a.yandex-team.ru/library/go/core/xerrors"
)

func TestSentryTransportImplements(t *testing.T) {
	require.Implements(t, (*sentry.Transport)(nil), (*SentryTransport)(nil))
}

type sentryTransportSuite struct {
	suite.Suite

	ctx    context.Context
	logger log.Logger

	responseChan chan persqueue.WriteResponse
	mock         *writerMock
	transport    *SentryTransport
}

func TestTransportSuite(t *testing.T) {
	suite.Run(t, new(sentryTransportSuite))
}

func (suite *sentryTransportSuite) SetupSuite() {
	suite.ctx = context.TODO()
	suite.logger = &nop.Logger{}

	persqueueNewWriter = func(_ persqueue.WriterOptions) persqueue.Writer {
		return suite.mock
	}
}

func (suite *sentryTransportSuite) TearDownSuite() {
	persqueueNewWriter = persqueue.NewWriter
}

func (suite *sentryTransportSuite) SetupTest() {
	suite.mock = &writerMock{}
	suite.mock.setup()
	suite.transport = NewSentryTransport(suite.ctx, suite.logger, "TestProject", persqueue.WriterOptions{})

	suite.mock.On("Init", suite.ctx).Return(
		&persqueue.WriterInit{},
		error(nil),
	)

	err := sentry.Init(
		sentry.ClientOptions{
			Transport:   suite.transport,
			Environment: EnvironmentTesting,
			Release:     "test@0.0.1",
			ServerName:  "test-host.yandex.net",
		},
	)
	suite.Require().NoError(err)
}

func (suite *sentryTransportSuite) TearDownTest() {
	suite.transport.Flush(time.Second)

	suite.mock.On("Close").Run(
		func(_ mock.Arguments) {
			suite.mock.tearDown()
		},
	).Return(nil)
	err := suite.transport.Close()
	suite.Assert().NoError(err)
}

func (suite *sentryTransportSuite) parseEvent(d *persqueue.WriteMessage) (*event, error) {
	ret := event{}
	if err := json.Unmarshal(d.Data, &ret); err != nil {
		return nil, err
	}
	return &ret, nil
}

func (suite *sentryTransportSuite) TestCaptureMessage() {
	suite.mock.On("Write", mock.Anything).Run(
		func(args mock.Arguments) {
			d := args.Get(0).(*persqueue.WriteMessage)
			suite.Require().NotNil(d)
			ev, err := suite.parseEvent(d)
			suite.Require().NoError(err)
			suite.Require().NotNil(ev)

			suite.Assert().Equal("Test Message", ev.Message)
			suite.Assert().Equal("TestProject", ev.Project)
			suite.Assert().Equal("test@0.0.1", ev.Version)
			suite.Assert().Equal(EnvironmentTesting, ev.Environment)
			suite.Assert().Equal("test-host.yandex.net", ev.Host)
			suite.Assert().Equal("info", ev.Level)
			suite.Assert().Equal("go", ev.Language)

			suite.Assert().Empty(ev.DC)
			suite.Assert().Empty(ev.File)
			suite.Assert().Empty(ev.Line)
			suite.Assert().Empty(ev.Column)
			suite.Assert().Empty(ev.Stack)
			suite.Assert().Empty(ev.IsInternal)
			suite.Assert().Empty(ev.IsRobot)
			suite.Assert().Empty(ev.IP)
			suite.Assert().Empty(ev.Region)
			suite.Assert().Empty(ev.Service)
			suite.Assert().Empty(ev.Block)
			suite.Assert().Empty(ev.SourceType)
			suite.Assert().Empty(ev.Source)
			suite.Assert().Empty(ev.SourceMethod)
			suite.Assert().Empty(ev.URL)
			suite.Assert().Empty(ev.Method)
			suite.Assert().Empty(ev.UserAgent)
			suite.Assert().Empty(ev.RequestID)
			suite.Assert().Empty(ev.Platform)
			suite.Assert().Empty(ev.Page)
			suite.Assert().Empty(ev.YandexUID)
			suite.Assert().Empty(ev.Experiments)
			suite.Assert().Empty(ev.Slots)
			suite.Assert().Empty(ev.Fingerprint)

			suite.Require().NotEmpty(ev.Additional)
			suite.Assert().Contains(ev.Additional, "contexts")
			suite.Assert().Contains(ev.Additional, "event_id")
			suite.Assert().NotContains(ev.Additional, "extra")
			suite.Assert().NotContains(ev.Additional, "vars")
		},
	).Return(nil)

	sentry.CaptureMessage("Test Message")
	suite.mock.AssertExpectations(suite.T())
}

func (suite *sentryTransportSuite) TestCaptureMessageWithScope() {
	suite.mock.On("Write", mock.Anything).Run(
		func(args mock.Arguments) {
			d := args.Get(0).(*persqueue.WriteMessage)
			suite.Require().NotNil(d)
			ev, err := suite.parseEvent(d)
			suite.Require().NoError(err)
			suite.Require().NotNil(ev)

			suite.Assert().Equal("Test Message", ev.Message)
			suite.Assert().Equal("TestProject", ev.Project)
			suite.Assert().Equal("test@0.0.1", ev.Version)
			suite.Assert().Equal(EnvironmentTesting, ev.Environment)
			suite.Assert().Equal("test-host.yandex.net", ev.Host)
			suite.Assert().Equal("info", ev.Level)
			suite.Assert().Equal("go", ev.Language)

			suite.Assert().Equal(VLA, ev.DC)
			suite.Assert().Equal("test-request-id", ev.RequestID)
			suite.Assert().Equal(PlatformDesktop, ev.Platform)
			suite.Assert().True(ev.IsInternal)
			suite.Assert().True(ev.IsRobot)
			suite.Assert().Equal("test block", ev.Block)
			suite.Assert().Equal("test service", ev.Service)
			suite.Assert().Equal("test source", ev.Source)
			suite.Assert().Equal("test source method", ev.SourceMethod)
			suite.Assert().Equal("test source type", ev.SourceType)
			suite.Assert().Equal("test url", ev.URL)
			suite.Assert().Equal("test page", ev.Page)
			suite.Assert().Equal("test region", ev.Region)
			suite.Assert().Equal("test slots", ev.Slots)
			suite.Assert().Equal("test experiments", ev.Experiments)
			suite.Assert().Equal("test user agent", ev.UserAgent)
			suite.Assert().Equal("test yandex uid", ev.YandexUID)
			suite.Assert().Equal("127.0.0.1", ev.IP)
			suite.Assert().Equal("test finger", ev.Fingerprint)

			suite.Assert().Empty(ev.File)
			suite.Assert().Empty(ev.Line)
			suite.Assert().Empty(ev.Column)
			suite.Assert().Empty(ev.Stack)
			suite.Assert().Empty(ev.Method)

			suite.Require().NotEmpty(ev.Additional)
			suite.Assert().Contains(ev.Additional, "contexts")
			suite.Assert().Contains(ev.Additional, "event_id")
			suite.Assert().Contains(ev.Additional, "extra")
			suite.Assert().NotContains(ev.Additional, "vars")

			contexts := ev.Additional["contexts"].(map[string]interface{})
			suite.Require().NotNil(contexts)
			suite.Assert().Equal("value", contexts["some"])

			extra := ev.Additional["extra"].(map[string]interface{})
			suite.Require().NotNil(extra)
			suite.Assert().Equal("extra value", extra["some"])
		},
	).Return(nil)

	sentry.WithScope(
		func(scope *sentry.Scope) {
			scope.SetUser(
				sentry.User{
					ID:        "test yandex uid",
					IPAddress: "127.0.0.1",
				},
			)
			scope.SetFingerprint([]string{"test finger"})
			scope.SetContext("some", "value")
			scope.SetExtra("some", "extra value")

			SetDC(scope, VLA)
			SetRequestID(scope, "test-request-id")
			SetPlatform(scope, PlatformDesktop)
			SetIsInternal(scope)
			SetIsRobot(scope)
			SetBlock(scope, "test block")
			SetService(scope, "test service")
			SetSource(scope, "test source")
			SetSourceMethod(scope, "test source method")
			SetSourceType(scope, "test source type")
			SetURL(scope, "test url")
			SetPage(scope, "test page")
			SetRegion(scope, "test region")
			SetSlots(scope, "test slots")
			SetExperiments(scope, "test experiments")
			SetUserAgent(scope, "test user agent")
			sentry.CaptureMessage("Test Message")
		},
	)
	suite.mock.AssertExpectations(suite.T())
}

func (suite *sentryTransportSuite) TestCaptureException() {
	suite.mock.On("Write", mock.Anything).Run(
		func(args mock.Arguments) {
			d := args.Get(0).(*persqueue.WriteMessage)
			suite.Require().NotNil(d)
			ev, err := suite.parseEvent(d)
			suite.Require().NoError(err)
			suite.Require().NotNil(ev)

			suite.Assert().Equal("*xerrors.newError: test exception", ev.Message)
			suite.Assert().Equal("TestProject", ev.Project)
			suite.Assert().Equal("test@0.0.1", ev.Version)
			suite.Assert().Equal(EnvironmentTesting, ev.Environment)
			suite.Assert().Equal("test-host.yandex.net", ev.Host)
			suite.Assert().Equal("error", ev.Level)
			suite.Assert().Equal("go", ev.Language)
			suite.Assert().Equal("/-S/noc/go/errorbooster/sentry_test.go", ev.File)
			suite.Assert().Equal(290, ev.Line)
			suite.Assert().Equal(0, ev.Column)
			suite.Assert().NotEmpty(ev.Stack)
			suite.Assert().Equal("(*sentryTransportSuite).TestCaptureException", ev.Method)

			suite.Assert().Empty(ev.DC)
			suite.Assert().Empty(ev.IsInternal)
			suite.Assert().Empty(ev.IsRobot)
			suite.Assert().Empty(ev.IP)
			suite.Assert().Empty(ev.Region)
			suite.Assert().Empty(ev.Service)
			suite.Assert().Empty(ev.Block)
			suite.Assert().Empty(ev.SourceType)
			suite.Assert().Empty(ev.Source)
			suite.Assert().Empty(ev.SourceMethod)
			suite.Assert().Empty(ev.URL)
			suite.Assert().Empty(ev.UserAgent)
			suite.Assert().Empty(ev.RequestID)
			suite.Assert().Empty(ev.Platform)
			suite.Assert().Empty(ev.Page)
			suite.Assert().Empty(ev.YandexUID)
			suite.Assert().Empty(ev.Experiments)
			suite.Assert().Empty(ev.Slots)
			suite.Assert().Empty(ev.Fingerprint)

			suite.Require().NotEmpty(ev.Additional)
			suite.Assert().Contains(ev.Additional, "contexts")
			suite.Assert().Contains(ev.Additional, "event_id")
			suite.Assert().NotContains(ev.Additional, "extra")
			suite.Assert().NotContains(ev.Additional, "vars")
		},
	).Return(nil)

	sentry.CaptureException(xerrors.New("test exception"))
	suite.mock.AssertExpectations(suite.T())
}

func (suite *sentryTransportSuite) TestRecover() {
	suite.mock.On("Write", mock.Anything).Run(
		func(args mock.Arguments) {
			d := args.Get(0).(*persqueue.WriteMessage)
			suite.Require().NotNil(d)
			ev, err := suite.parseEvent(d)
			suite.Require().NoError(err)
			suite.Require().NotNil(ev)

			suite.Assert().Equal("Test Panic", ev.Message)
			suite.Assert().Equal("TestProject", ev.Project)
			suite.Assert().Equal("test@0.0.1", ev.Version)
			suite.Assert().Equal(EnvironmentTesting, ev.Environment)
			suite.Assert().Equal("test-host.yandex.net", ev.Host)
			suite.Assert().Equal("fatal", ev.Level)
			suite.Assert().Equal("go", ev.Language)

			suite.Assert().Empty(ev.DC)
			suite.Assert().Empty(ev.File)
			suite.Assert().Empty(ev.Line)
			suite.Assert().Empty(ev.Column)
			suite.Assert().Empty(ev.Stack)
			suite.Assert().Empty(ev.IsInternal)
			suite.Assert().Empty(ev.IsRobot)
			suite.Assert().Empty(ev.IP)
			suite.Assert().Empty(ev.Region)
			suite.Assert().Empty(ev.Service)
			suite.Assert().Empty(ev.Block)
			suite.Assert().Empty(ev.SourceType)
			suite.Assert().Empty(ev.Source)
			suite.Assert().Empty(ev.SourceMethod)
			suite.Assert().Empty(ev.URL)
			suite.Assert().Empty(ev.Method)
			suite.Assert().Empty(ev.UserAgent)
			suite.Assert().Empty(ev.RequestID)
			suite.Assert().Empty(ev.Platform)
			suite.Assert().Empty(ev.Page)
			suite.Assert().Empty(ev.YandexUID)
			suite.Assert().Empty(ev.Experiments)
			suite.Assert().Empty(ev.Slots)
			suite.Assert().Empty(ev.Fingerprint)

			suite.Require().NotEmpty(ev.Additional)
			suite.Assert().Contains(ev.Additional, "contexts")
			suite.Assert().Contains(ev.Additional, "event_id")
			suite.Assert().NotContains(ev.Additional, "extra")
			suite.Assert().NotContains(ev.Additional, "vars")
		},
	).Return(nil)

	func() {
		defer sentry.Recover()
		panic("Test Panic")
	}()
	suite.mock.AssertExpectations(suite.T())
}
