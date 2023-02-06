package db

import (
	"context"
	"time"

	"github.com/gofrs/uuid"

	"a.yandex-team.ru/noc/nocrfcsd/internal/models"
)

func (suite *functionalSuite) TestGetRFCByStartrekIssueKey() {
	err := suite.tx.BulkCreateInfraEnvironments(context.Background(), []*models.InfraEnvironment{
		{
			EnvironmentID:   42,
			EnvironmentName: "test environment",
			ServiceID:       42,
			ServiceName:     "test service",
		},
	})
	if err != nil {
		panic(err)
	}
	id, err := uuid.NewV4()
	if err != nil {
		panic(err)
	}

	createTime, err := time.Parse(time.RFC3339, "2006-01-02T12:00:00Z")
	if err != nil {
		panic(err)
	}
	updateTime, err := time.Parse(time.RFC3339, "2006-01-02T12:00:00Z")
	if err != nil {
		panic(err)
	}

	startTime, err := time.Parse(time.RFC3339, "2006-01-02T15:04:05Z")
	if err != nil {
		panic(err)
	}
	endTime, err := time.Parse(time.RFC3339, "2006-01-02T16:04:05Z")
	if err != nil {
		panic(err)
	}

	rfcExpected := &models.RFC{
		ID:             id,
		CreateTime:     createTime,
		UpdateTime:     updateTime,
		Name:           "test request for change",
		ChangeType:     models.ChangeTypeEmergency,
		LinkedIncident: "NOCREQUESTS-1",
		Responsible: models.StaffUser{
			ID:        42,
			UID:       "100500",
			Login:     "testuser",
			FirstName: "",
			LastName:  "",
		},
		AddToResponsiblesCalendar: true,
		AdditionalApprovers:       nil,
		ChangedService: models.InfraEnvironment{
			EnvironmentID:   42,
			EnvironmentName: "test environment",
			ServiceID:       42,
			ServiceName:     "test service",
		},
		Datacenters:          []models.Datacenter{models.DatacenterOther},
		PreviousExperience:   models.PreviousExperienceSuccessfulWithProblems,
		ChangeAutomation:     models.ChangeAutomationManual,
		ServiceImpact:        models.ServiceImpactAbsent,
		ChangeTesting:        models.ChangeTestingManualTests,
		StartTime:            startTime.In(time.UTC),
		EndTime:              endTime.In(time.UTC),
		ChangeDescription:    "test description",
		ExecutionDescription: "test execution description",
		RollbackDescription:  "test rollback description",
		StartrekIssue: models.StartrekIssue{
			Key:    "NOCRFCS-42",
			Status: models.IssueStatusAgreementNeeded,
		},
	}

	_, err = suite.tx.CreateRFC(context.Background(), rfcExpected)
	if err != nil {
		panic(err)
	}

	rfcActual, err := suite.tx.GetRFCByStartrekIssueKey(context.Background(), "NOCRFCS-42")
	if err != nil {
		panic(err)
	}
	suite.Equal(*rfcExpected, *rfcActual)
}
