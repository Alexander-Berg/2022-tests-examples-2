package testutils

import (
	_codeqlRepo "a.yandex-team.ru/security/impulse/api/repositories/codeqldb/mocks"
	_cronRepo "a.yandex-team.ru/security/impulse/api/repositories/cron/mocks"
	_organizationRepo "a.yandex-team.ru/security/impulse/api/repositories/organization/mocks"
	_projectRepo "a.yandex-team.ru/security/impulse/api/repositories/project/mocks"
	_scanRepo "a.yandex-team.ru/security/impulse/api/repositories/scan/mocks"
	_scanInstanceRepo "a.yandex-team.ru/security/impulse/api/repositories/scaninstance/mocks"
	_scanTypeRepo "a.yandex-team.ru/security/impulse/api/repositories/scantype/mocks"
	_taskRepo "a.yandex-team.ru/security/impulse/api/repositories/task/mocks"
	_vulnerabilityRepo "a.yandex-team.ru/security/impulse/api/repositories/vulnerability/mocks"
	_vulnerabilityCategoryRepo "a.yandex-team.ru/security/impulse/api/repositories/vulnerabilitycategory/mocks"
	_vulnerabilityTotalStatisticsRepo "a.yandex-team.ru/security/impulse/api/repositories/vulnerabilitytotalstatistics/mocks"
	_workflowRepo "a.yandex-team.ru/security/impulse/api/repositories/workflow/mocks"
	_codeqlUsecase "a.yandex-team.ru/security/impulse/api/usecases/codeqldb"
	_cronUsecase "a.yandex-team.ru/security/impulse/api/usecases/cron"
	_organizationUsecase "a.yandex-team.ru/security/impulse/api/usecases/organization"
	_projectUsecase "a.yandex-team.ru/security/impulse/api/usecases/project"
	_scanUsecase "a.yandex-team.ru/security/impulse/api/usecases/scan"
	_scanInstanceUsecase "a.yandex-team.ru/security/impulse/api/usecases/scaninstance"
	_taskUsecase "a.yandex-team.ru/security/impulse/api/usecases/task"
	_vulnerabilityUsecase "a.yandex-team.ru/security/impulse/api/usecases/vulnerability"
	_vulnerabilityCategoryUsecase "a.yandex-team.ru/security/impulse/api/usecases/vulnerabilitycategory"
	_vulnerabilityTotalStatisticsUsecase "a.yandex-team.ru/security/impulse/api/usecases/vulnerabilitytotalstatistics"
)

type TestingCtx struct {
	CodeQLRepoMock                       *_codeqlRepo.Repository
	CronRepoMock                         *_cronRepo.Repository
	ScanRepoMock                         *_scanRepo.Repository
	ProjectRepoMock                      *_projectRepo.Repository
	ScanTypeRepoMock                     *_scanTypeRepo.Repository
	OrganiztionRepoMock                  *_organizationRepo.Repository
	WorkflowRepoMock                     *_workflowRepo.Repository
	ScanInstanceRepoMock                 *_scanInstanceRepo.Repository
	TaskRepoMock                         *_taskRepo.Repository
	VulnerabilityRepoMock                *_vulnerabilityRepo.Repository
	VulnerabilityTotalStatisticsRepoMock *_vulnerabilityTotalStatisticsRepo.Repository
	VulnerabilityCategoryRepoMock        *_vulnerabilityCategoryRepo.Repository

	CodeQLUsecase                       _codeqlUsecase.Usecase
	CronUsecase                         _cronUsecase.Usecase
	ScanUsecase                         _scanUsecase.Usecase
	TaskUsecase                         _taskUsecase.Usecase
	ScanInstanceUsecase                 _scanInstanceUsecase.Usecase
	ProjectUsecase                      _projectUsecase.Usecase
	OrganizationUsecase                 _organizationUsecase.Usecase
	VulnerabilityCategoryUsecase        _vulnerabilityCategoryUsecase.Usecase
	VulnerabilityTotalStatisticsUsecase _vulnerabilityTotalStatisticsUsecase.Usecase
	VulnerabilityUsecase                _vulnerabilityUsecase.Usecase
}

func NewTestingCtx() *TestingCtx {
	cronRepo := new(_cronRepo.Repository)
	codeQLRepo := new(_codeqlRepo.Repository)
	scanRepo := new(_scanRepo.Repository)
	projectRepo := new(_projectRepo.Repository)
	scanTypeRepo := new(_scanTypeRepo.Repository)
	organizationRepo := new(_organizationRepo.Repository)
	workflowRepo := new(_workflowRepo.Repository)
	scanInstanceRepo := new(_scanInstanceRepo.Repository)
	taskRepo := new(_taskRepo.Repository)
	vulnerabilityRepo := new(_vulnerabilityRepo.Repository)
	vulnerabilityTotalStatisticsRepo := new(_vulnerabilityTotalStatisticsRepo.Repository)
	vulnerabilityCategoryRepo := new(_vulnerabilityCategoryRepo.Repository)

	codeQLUsecase := _codeqlUsecase.NewCodeQLDatabaseUsecase(codeQLRepo)
	cronUsecase := _cronUsecase.NewCronUsecase(cronRepo)
	scanUsecase := _scanUsecase.NewScanUsecase(scanRepo, projectRepo, scanTypeRepo, scanInstanceRepo, workflowRepo)
	taskUsecase := _taskUsecase.NewTaskUsecase(taskRepo)
	scanInstanceUsecase := _scanInstanceUsecase.NewScanInstanceStatusUsecase(scanRepo, scanInstanceRepo)
	projectUsecase := _projectUsecase.NewProjectUsecase(projectRepo, scanInstanceRepo, scanInstanceUsecase)
	organizationUsecase := _organizationUsecase.NewOrganizationUsecase(organizationRepo, projectUsecase, scanInstanceRepo, scanInstanceUsecase)
	vulnerabilityTotalStatisticsUsecase := _vulnerabilityTotalStatisticsUsecase.NewVulnerabilityTotalStatisticsUsecase(vulnerabilityTotalStatisticsRepo)
	vulnerabilityUsecase := _vulnerabilityUsecase.NewVulnerabilityUsecase(vulnerabilityRepo, vulnerabilityTotalStatisticsUsecase)
	vulnerabilityCategoryUsecase := _vulnerabilityCategoryUsecase.NewVulnerabilityCategoryUsecase(vulnerabilityCategoryRepo)
	return &TestingCtx{
		codeQLRepo,
		cronRepo,
		scanRepo,
		projectRepo,
		scanTypeRepo,
		organizationRepo,
		workflowRepo,
		scanInstanceRepo,
		taskRepo,
		vulnerabilityRepo,
		vulnerabilityTotalStatisticsRepo,
		vulnerabilityCategoryRepo,

		codeQLUsecase,
		cronUsecase,
		scanUsecase,
		taskUsecase,
		scanInstanceUsecase,
		projectUsecase,
		organizationUsecase,
		vulnerabilityCategoryUsecase,
		vulnerabilityTotalStatisticsUsecase,
		vulnerabilityUsecase,
	}

}
