package workflow

import (
	"context"

	"a.yandex-team.ru/noc/nocrfcsd/internal/snapshot/dbsnapshot"
)

// TestRiskCostEstimateOKApprove проверяет оценку риска с переходом в аппрув через OK. Убеждаемся, что таск
// переходит к шагу startOKApprovement из-за наличия нужных согласующих responsibles в input-файле.
func (suite *functionalSuite) TestRiskCostEstimateOKApprove() {
	suite.snapshot.Load(suite.T(), dbsnapshot.New(suite.tx), suite.startrekMockHandler, suite.approversLoader)
	suite.Nil(suite.bg.SelectAndRun(context.Background()))
	suite.snapshot.Snapshot(suite.T(), dbsnapshot.New(suite.tx), suite.mockHTTPServer)
}

// TestRiskCostEstimateForceAutoApprove проверяет переход в auto approve при установленном forceAutoApprove даже в
// случае, если риск высокий.
func (suite *functionalSuite) TestRiskCostEstimateForceAutoApprove() {
	suite.snapshot.Load(suite.T(), dbsnapshot.New(suite.tx), suite.startrekMockHandler, suite.approversLoader)
	suite.Nil(suite.bg.SelectAndRun(context.Background()))
	suite.snapshot.Snapshot(suite.T(), dbsnapshot.New(suite.tx), suite.mockHTTPServer)
}

// TestRiskCostEstimateManualApprovement проверяет оценку риска с переходом в ручной аппрув. Убеждаемся, что таск
// переходит к шагу startManualApprovement из-за пустого конфига согласующих responsibles в input-файле.
func (suite *functionalSuite) TestRiskCostEstimateManualApprovement() {
	suite.snapshot.Load(suite.T(), dbsnapshot.New(suite.tx), suite.startrekMockHandler, suite.approversLoader)
	suite.Nil(suite.bg.SelectAndRun(context.Background()))
	suite.snapshot.Snapshot(suite.T(), dbsnapshot.New(suite.tx), suite.mockHTTPServer)
}

// TestRiskCostEstimateAutoApprove проверяет оценку риска с автоматическим аппрувом. Убеждаемся, что отсутствие
// принужительных согласующих и низкий риск переводят таск к шагу autoApprove.
func (suite *functionalSuite) TestRiskCostEstimateAutoApprove() {
	suite.snapshot.Load(suite.T(), dbsnapshot.New(suite.tx), suite.startrekMockHandler, suite.approversLoader)
	suite.Nil(suite.bg.SelectAndRun(context.Background()))
	suite.snapshot.Snapshot(suite.T(), dbsnapshot.New(suite.tx), suite.mockHTTPServer)
}

// TestRiskCostEstimateAdditionalApprovers проверяет оценку риска с дополнительными согласующими. Убеждаемся, что
// при указании дополнительных согласующих автоаппрува не будет, не смотря на низкий риск. Также убеждаемся, что
// ручного аппрува не будет (а будет аппрув через сервис OK, то есть переход к шагу startOKApprovement), не смотря на
// пустой список согласующих в конфиге responsibles, - как раз из-за наличия дополнительных согласующих.
func (suite *functionalSuite) TestRiskCostEstimateAdditionalApprovers() {
	suite.snapshot.Load(
		suite.T(),
		dbsnapshot.New(suite.tx),
		suite.startrekMockHandler,
		suite.infraMockHandler,
		suite.approversLoader,
	)
	suite.Nil(suite.bg.SelectAndRun(context.Background()))
	suite.snapshot.Snapshot(suite.T(), dbsnapshot.New(suite.tx), suite.mockHTTPServer)
}

// TestRiskCostEstimateOneDatacenter проверяет, что наличие всего лишь одного ДЦ не добавляет риска. Это реальный
// случай с NOCRFCS-10778, который был неправильно оценен в risk=12, когда должен был оцениваться в risk=10.
// Смотри: NOCDEV-6599.
func (suite *functionalSuite) TestRiskCostEstimateOneDatacenter() {
	suite.snapshot.Load(suite.T(), dbsnapshot.New(suite.tx), suite.startrekMockHandler, suite.approversLoader)
	suite.Nil(suite.bg.SelectAndRun(context.Background()))
	suite.snapshot.Snapshot(suite.T(), dbsnapshot.New(suite.tx), suite.mockHTTPServer)
}

// TestRiskCostEstimateTwoDatacenters проверяет, что если количество ДЦ два или более, то риск увеличивается. Это
// взятый за основу NOCRFCS-10778, в котором добавлен второй ДЦ MYT, чтобы проверить, что риск возрастёт с risk=10
// до risk=12. Смотри: NOCDEV-6599.
func (suite *functionalSuite) TestRiskCostEstimateTwoDatacenters() {
	suite.snapshot.Load(suite.T(), dbsnapshot.New(suite.tx), suite.startrekMockHandler, suite.approversLoader)
	suite.Nil(suite.bg.SelectAndRun(context.Background()))
	suite.snapshot.Snapshot(suite.T(), dbsnapshot.New(suite.tx), suite.mockHTTPServer)
}
