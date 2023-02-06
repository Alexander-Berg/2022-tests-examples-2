package errorbooster

import (
	"context"
	"encoding/json"
	"os"
	"strconv"
	"strings"
	"testing"

	"github.com/getsentry/sentry-go"
	"github.com/stretchr/testify/suite"

	"a.yandex-team.ru/kikimr/public/sdk/go/persqueue"
	"a.yandex-team.ru/library/go/core/log"
	"a.yandex-team.ru/library/go/core/log/nop"
	"a.yandex-team.ru/library/go/core/xerrors"
)

type integrationTestSuite struct {
	suite.Suite

	logger  log.Logger
	project string

	port  int
	topic string

	transport *SentryTransport
}

func TestLogBrokerIntegrationTestSuite(t *testing.T) {
	suite.Run(t, new(integrationTestSuite))
}

func (suite *integrationTestSuite) SetupSuite() {
	suite.logger = &nop.Logger{}
	suite.project = "Integration Test Project"

	portStr := os.Getenv("LOGBROKER_PORT")
	suite.Require().NotEmpty(portStr)

	port, err := strconv.Atoi(portStr)
	suite.Require().NoError(err)

	suite.port = port

	topics := strings.Split(os.Getenv("LOGBROKER_CREATE_TOPICS"), ",")
	suite.Require().NotEmpty(topics)

	suite.Require().Len(topics, 1)
	suite.topic = topics[0]
}

func (suite *integrationTestSuite) writerOptions() persqueue.WriterOptions {
	return persqueue.WriterOptions{
		Endpoint:       "localhost",
		Port:           suite.port,
		Topic:          suite.topic,
		SourceID:       []byte("integration-test"),
		RetryOnFailure: true,
	}
}

func (suite *integrationTestSuite) readerOptions() persqueue.ReaderOptions {
	return persqueue.ReaderOptions{
		Endpoint:       "localhost",
		Port:           suite.port,
		Topics:         []persqueue.TopicInfo{{Topic: suite.topic}},
		Consumer:       "integration-test",
		RetryOnFailure: true,
	}
}

func (suite *integrationTestSuite) SetupTest() {
	suite.transport = NewSentryTransport(context.Background(), suite.logger, suite.project, suite.writerOptions())
	err := sentry.Init(
		sentry.ClientOptions{
			Transport:   suite.transport,
			Environment: EnvironmentPreStable,
			Release:     "integrationTestSuite@0.1.0",
			ServerName:  "integration-test.yandex.net",
		},
	)
	suite.Require().NoError(err)
}

func (suite *integrationTestSuite) TearDownTest() {
	suite.Require().NoError(suite.transport.Close())
}

func (suite *integrationTestSuite) readEvent() *event {
	reader := persqueue.NewReader(suite.readerOptions())
	suite.Require().NotNil(reader)
	defer reader.Shutdown()

	_, err := reader.Start(context.Background())
	suite.Require().NoError(err)

	msg, ok := <-reader.C()
	suite.Require().True(ok)

	data, ok := msg.(*persqueue.Data)
	if !ok {
		suite.Require().Fail("Got unexpected message: %v", msg)
		return nil
	}
	data.Commit()
	batches := data.Batches()
	suite.Require().Len(batches, 1)
	messages := batches[0].Messages
	suite.Require().Len(messages, 1)

	ev := event{}
	err = json.Unmarshal(messages[0].Data, &ev)
	suite.Require().NoError(err)
	return &ev
}

func (suite *integrationTestSuite) TestCaptureMessage() {
	sentry.WithScope(
		func(scope *sentry.Scope) {
			scope.SetUser(
				sentry.User{
					ID:        "Integration Test Yandex UID",
					IPAddress: "127.0.0.2",
				},
			)
			scope.SetFingerprint([]string{"integration", "test", "fingerprint"})
			scope.SetContext("test", "integration")
			scope.SetExtra("test", "integration extra")

			SetDC(scope, KLG)
			SetRequestID(scope, "test-integration-request-id")
			SetPlatform(scope, PlatformUnsupported)
			SetIsInternal(scope)
			SetBlock(scope, "test integration block")
			SetService(scope, "test integration service")
			SetSource(scope, "test integration source")
			SetSourceMethod(scope, "test integration source method")
			SetSourceType(scope, "test integration source type")
			SetURL(scope, "test integration url")
			SetPage(scope, "test integration page")
			SetRegion(scope, "test integration region")
			SetSlots(scope, "test integration slots")
			SetExperiments(scope, "test integration experiments")
			SetUserAgent(scope, "test integration user agent")

			sentry.CaptureMessage("Integration Test Message")
		},
	)

	ev := suite.readEvent()
	suite.Require().NotNil(ev)
	suite.Assert().Equal("Integration Test Message", ev.Message)
	suite.Assert().Equal(suite.project, ev.Project)
	suite.Assert().Equal("integrationTestSuite@0.1.0", ev.Version)
	suite.Assert().Equal(EnvironmentPreStable, ev.Environment)
	suite.Assert().Equal("integration-test.yandex.net", ev.Host)
	suite.Assert().Equal("info", ev.Level)
	suite.Assert().Equal("go", ev.Language)

	suite.Assert().Equal(KLG, ev.DC)
	suite.Assert().Equal("test-integration-request-id", ev.RequestID)
	suite.Assert().Equal(PlatformUnsupported, ev.Platform)
	suite.Require().True(ev.IsInternal)
	suite.Require().False(ev.IsRobot)
	suite.Assert().Equal("test integration block", ev.Block)
	suite.Assert().Equal("test integration service", ev.Service)
	suite.Assert().Equal("test integration source", ev.Source)
	suite.Assert().Equal("test integration source method", ev.SourceMethod)
	suite.Assert().Equal("test integration source type", ev.SourceType)
	suite.Assert().Equal("test integration url", ev.URL)
	suite.Assert().Equal("test integration page", ev.Page)
	suite.Assert().Equal("test integration region", ev.Region)
	suite.Assert().Equal("test integration slots", ev.Slots)
	suite.Assert().Equal("test integration experiments", ev.Experiments)
	suite.Assert().Equal("test integration user agent", ev.UserAgent)
	suite.Assert().Equal("Integration Test Yandex UID", ev.YandexUID)
	suite.Assert().Equal("127.0.0.2", ev.IP)
	suite.Assert().Equal("integration,test,fingerprint", ev.Fingerprint)

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
	suite.Assert().Equal("integration", contexts["test"])

	extra := ev.Additional["extra"].(map[string]interface{})
	suite.Require().NotNil(extra)
	suite.Assert().Equal("integration extra", extra["test"])
}

func (suite *integrationTestSuite) TestCaptureError() {
	sentry.WithScope(
		func(scope *sentry.Scope) {
			scope.SetUser(
				sentry.User{
					ID:        "Another Test Yandex UID",
					IPAddress: "127.0.0.3",
				},
			)
			scope.SetFingerprint([]string{"another", "test", "fingerprint"})
			scope.SetContext("another", "integration")
			scope.SetExtra("another", "integration extra")

			SetDC(scope, MYT)
			SetRequestID(scope, "test-another-request-id")
			SetPlatform(scope, PlatformTVApp)
			SetIsRobot(scope)
			SetBlock(scope, "test another block")
			SetService(scope, "test another service")
			SetSource(scope, "test another source")
			SetSourceMethod(scope, "test another source method")
			SetSourceType(scope, "test another source type")
			SetURL(scope, "test another url")
			SetPage(scope, "test another page")
			SetRegion(scope, "test another region")
			SetSlots(scope, "test another slots")
			SetExperiments(scope, "test another experiments")
			SetUserAgent(scope, "test another user agent")

			sentry.CaptureException(xerrors.New("Integration Test Error"))
		},
	)

	ev := suite.readEvent()
	suite.Require().NotNil(ev)
	suite.Assert().Equal("*xerrors.newError: Integration Test Error", ev.Message)
	suite.Assert().Equal(suite.project, ev.Project)
	suite.Assert().Equal("integrationTestSuite@0.1.0", ev.Version)
	suite.Assert().Equal(EnvironmentPreStable, ev.Environment)
	suite.Assert().Equal("integration-test.yandex.net", ev.Host)
	suite.Assert().Equal("error", ev.Level)
	suite.Assert().Equal("go", ev.Language)

	suite.Assert().Equal(MYT, ev.DC)
	suite.Assert().Equal("test-another-request-id", ev.RequestID)
	suite.Assert().Equal(PlatformTVApp, ev.Platform)
	suite.Require().False(ev.IsInternal)
	suite.Require().True(ev.IsRobot)
	suite.Assert().Equal("test another block", ev.Block)
	suite.Assert().Equal("test another service", ev.Service)
	suite.Assert().Equal("test another source", ev.Source)
	suite.Assert().Equal("test another source method", ev.SourceMethod)
	suite.Assert().Equal("test another source type", ev.SourceType)
	suite.Assert().Equal("test another url", ev.URL)
	suite.Assert().Equal("test another page", ev.Page)
	suite.Assert().Equal("test another region", ev.Region)
	suite.Assert().Equal("test another slots", ev.Slots)
	suite.Assert().Equal("test another experiments", ev.Experiments)
	suite.Assert().Equal("test another user agent", ev.UserAgent)
	suite.Assert().Equal("Another Test Yandex UID", ev.YandexUID)
	suite.Assert().Equal("127.0.0.3", ev.IP)
	suite.Assert().Equal("another,test,fingerprint", ev.Fingerprint)

	suite.Assert().Equal("/-S/noc/go/errorbooster/integration_test.go", ev.File)
	suite.Assert().Equal(233, ev.Line)
	suite.Assert().Equal(0, ev.Column)
	suite.Assert().NotEmpty(ev.Stack)
	suite.Assert().Equal("(*integrationTestSuite).TestCaptureError.func1", ev.Method)

	suite.Require().NotEmpty(ev.Additional)
	suite.Assert().Contains(ev.Additional, "contexts")
	suite.Assert().Contains(ev.Additional, "event_id")
	suite.Assert().Contains(ev.Additional, "extra")
	suite.Assert().NotContains(ev.Additional, "vars")

	contexts := ev.Additional["contexts"].(map[string]interface{})
	suite.Require().NotNil(contexts)
	suite.Assert().Equal("integration", contexts["another"])

	extra := ev.Additional["extra"].(map[string]interface{})
	suite.Require().NotNil(extra)
	suite.Assert().Equal("integration extra", extra["another"])
}
