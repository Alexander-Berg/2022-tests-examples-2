package db

import (
	"context"

	"github.com/gofrs/uuid"

	"a.yandex-team.ru/noc/nocrfcsd/internal/models"
)

func getBaseRFC(suite *functionalSuite) *models.RFC {
	err := suite.tx.BulkCreateInfraEnvironments(context.Background(), []*models.InfraEnvironment{
		{
			EnvironmentID:   42,
			EnvironmentName: "test environment",
			ServiceID:       42,
			ServiceName:     "test service",
		},
	})
	if err != nil {
		suite.T().Fatalf("error creating infra environments: %v", err)
	}

	id, err := uuid.NewV4()
	if err != nil {
		suite.T().Fatalf("error generating id: %v", err)
	}
	return &models.RFC{
		ID:             id,
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
		Datacenters:            []models.Datacenter{models.DatacenterMYT, models.DatacenterIVA},
		DevicesExpression:      "noc-sas,   iva13-s666,iva13-s667, {Ивантеевка} and not {в оффлайне} and {лаборатория Владимир},,,sas-e2.yndx.net",
		Devices:                []string{"noc-sas", "iva13-s666", "iva13-s667"},
		PreviousExperience:     models.PreviousExperienceSuccessfulWithProblems,
		ChangeAutomation:       models.ChangeAutomationManual,
		ServiceImpact:          models.ServiceImpactAbsent,
		ChangeTesting:          models.ChangeTestingManualTests,
		ChangeDescription:      "test description",
		PreparationDescription: "test preparation description",
		ExecutionDescription:   "test execution description",
		RollbackDescription:    "test rollback description",
		StartrekIssue: models.StartrekIssue{
			Key:    "NOCRFCS-42",
			Status: models.IssueStatusAgreementNeeded,
		},
		ForceAutoApprove: false,
	}
}

func (suite *functionalSuite) TestCreateRFCDevices() {
	rfcExpected := getBaseRFC(suite)
	if _, err := suite.tx.CreateRFC(context.Background(), rfcExpected); err != nil {
		suite.T().Fatalf("error creating rfc: %v", err)
	}

	rfcActual, err := suite.tx.GetRFCByStartrekIssueKey(context.Background(), rfcExpected.StartrekIssue.Key)
	if err != nil {
		suite.T().Fatalf("error reading rfc: %v", err)
	}

	suite.Equal(rfcExpected.DevicesExpression, rfcActual.DevicesExpression)
	suite.Equal(rfcExpected.Devices, rfcActual.Devices)
}

func (suite *functionalSuite) TestCreateRFCDevicesEmpty() {
	rfcExpected := getBaseRFC(suite)
	rfcExpected.DevicesExpression = ""
	rfcExpected.Devices = []string{}
	if _, err := suite.tx.CreateRFC(context.Background(), rfcExpected); err != nil {
		suite.T().Fatalf("error creating rfc: %v", err)
	}

	rfcActual, err := suite.tx.GetRFCByStartrekIssueKey(context.Background(), rfcExpected.StartrekIssue.Key)
	if err != nil {
		suite.T().Fatalf("error reading rfc: %v", err)
	}

	suite.Equal("", rfcActual.DevicesExpression)
	suite.Nil(rfcActual.Devices)
}

func (suite *functionalSuite) TestCreateRFCJugglerMute() {
	rfcExpected := getBaseRFC(suite)
	rfcExpected.JugglerMute = &models.JugglerMute{MondataHelpKeys: []string{"help_key1", "help_key2"}}
	if _, err := suite.tx.CreateRFC(context.Background(), rfcExpected); err != nil {
		suite.T().Fatalf("error creating rfc: %v", err)
	}

	rfcActual, err := suite.tx.GetRFCByStartrekIssueKey(context.Background(), rfcExpected.StartrekIssue.Key)
	if err != nil {
		suite.T().Fatalf("error reading rfc: %v", err)
	}

	suite.Equal(rfcExpected.JugglerMute, rfcActual.JugglerMute)
}

func (suite *functionalSuite) TestCreateRFCJugglerMuteNoMondataKeys() {
	rfcExpected := getBaseRFC(suite)
	rfcExpected.JugglerMute = &models.JugglerMute{MondataHelpKeys: nil}
	if _, err := suite.tx.CreateRFC(context.Background(), rfcExpected); err != nil {
		suite.T().Fatalf("error creating rfc: %v", err)
	}

	rfcActual, err := suite.tx.GetRFCByStartrekIssueKey(context.Background(), rfcExpected.StartrekIssue.Key)
	if err != nil {
		suite.T().Fatalf("error reading rfc: %v", err)
	}

	suite.Equal(rfcExpected.JugglerMute, rfcActual.JugglerMute)
}

func (suite *functionalSuite) TestCreateRFCNoJugglerMute() {
	rfcExpected := getBaseRFC(suite)
	rfcExpected.JugglerMute = nil
	if _, err := suite.tx.CreateRFC(context.Background(), rfcExpected); err != nil {
		suite.T().Fatalf("error creating rfc: %v", err)
	}

	rfcActual, err := suite.tx.GetRFCByStartrekIssueKey(context.Background(), rfcExpected.StartrekIssue.Key)
	if err != nil {
		suite.T().Fatalf("error reading rfc: %v", err)
	}

	suite.Equal(rfcExpected.JugglerMute, rfcActual.JugglerMute)
}
