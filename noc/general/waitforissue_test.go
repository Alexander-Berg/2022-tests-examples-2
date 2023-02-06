package workflow

import (
	"context"

	"a.yandex-team.ru/noc/nocrfcsd/internal/snapshot/dbsnapshot"
)

// TestWaitForIssueNoIssue проверяет ситуацию, в которую попадает таск при первых срабатываниях, когда startrek issue
// ещё не создан. Убеждаемся, что таск получает ошибку от startrek и падает, увеличивая счётчик ретраев.
func (suite *functionalSuite) TestWaitForIssueNoIssue() {
	suite.snapshot.Load(suite.T(), dbsnapshot.New(suite.tx), suite.startrekMockHandler)
	suite.Nil(suite.bg.SelectAndRun(context.Background()))
	suite.snapshot.Snapshot(suite.T(), dbsnapshot.New(suite.tx), suite.mockHTTPServer)
}

// TestWaitForIssueHasIssue проверяет успешную ситуацию: startrek вернул тикет по заданному unique, и таск перешёл
// на следующий шаг.
func (suite *functionalSuite) TestWaitForIssueHasIssue() {
	suite.snapshot.Load(suite.T(), dbsnapshot.New(suite.tx), suite.startrekMockHandler)
	suite.Nil(suite.bg.SelectAndRun(context.Background()))
	suite.snapshot.Snapshot(suite.T(), dbsnapshot.New(suite.tx), suite.mockHTTPServer)
}
