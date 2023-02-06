package db

import (
	"context"

	"a.yandex-team.ru/noc/nocrfcsd/internal/models"
	"a.yandex-team.ru/noc/nocrfcsd/internal/snapshot/dbsnapshot"
)

// TestBulkCreateInfraEnvironmentsNil проверяет случай, когда массив окружений nil.
func (suite *functionalSuite) TestBulkCreateInfraEnvironmentsNil() {
	// suite.snapshot.Load(suite.T(), dbsnapshot.New(suite.tx))
	suite.Nil(suite.tx.BulkCreateInfraEnvironments(context.Background(), nil))
	suite.snapshot.Snapshot(suite.T(), dbsnapshot.New(suite.tx))
}

// TestBulkCreateInfraEnvironmentsEmpty проверяет случай, когда массив окружений пустой.
func (suite *functionalSuite) TestBulkCreateInfraEnvironmentsEmpty() {
	// suite.snapshot.Load(suite.T(), dbsnapshot.New(suite.tx))
	suite.Nil(suite.tx.BulkCreateInfraEnvironments(context.Background(), []*models.InfraEnvironment{}))
	suite.snapshot.Snapshot(suite.T(), dbsnapshot.New(suite.tx))
}

// TestBulkCreateInfraEnvironmentsDatacentersNil проверяет nil-список датацентров.
func (suite *functionalSuite) TestBulkCreateInfraEnvironmentsDatacentersNil() {
	environments := []*models.InfraEnvironment{
		{
			EnvironmentID:   43,
			EnvironmentName: "test environment",
			ServiceID:       42,
			ServiceName:     "test service",
			Datacenters:     nil,
		},
	}
	suite.Nil(suite.tx.BulkCreateInfraEnvironments(context.Background(), environments))
	suite.snapshot.Snapshot(suite.T(), dbsnapshot.New(suite.tx))
}

// TestBulkCreateInfraEnvironmentsDatacentersEmpty проверяет пустой список датацентров.
func (suite *functionalSuite) TestBulkCreateInfraEnvironmentsDatacentersEmpty() {
	environments := []*models.InfraEnvironment{
		{
			EnvironmentID:   43,
			EnvironmentName: "test environment",
			ServiceID:       42,
			ServiceName:     "test service",
			Datacenters:     []models.Datacenter{},
		},
	}
	suite.Nil(suite.tx.BulkCreateInfraEnvironments(context.Background(), environments))
	suite.snapshot.Snapshot(suite.T(), dbsnapshot.New(suite.tx))
}

// TestBulkCreateInfraEnvironmentsDatacentersOne проверяет список датацентров из одного ДЦ.
func (suite *functionalSuite) TestBulkCreateInfraEnvironmentsDatacentersOne() {
	environments := []*models.InfraEnvironment{
		{
			EnvironmentID:   43,
			EnvironmentName: "test environment",
			ServiceID:       42,
			ServiceName:     "test service",
			Datacenters:     []models.Datacenter{models.DatacenterIVA},
		},
	}
	suite.Nil(suite.tx.BulkCreateInfraEnvironments(context.Background(), environments))
	suite.snapshot.Snapshot(suite.T(), dbsnapshot.New(suite.tx))
}

// TestBulkCreateInfraEnvironmentsOnConflictUpdate проверяет обновление всех полей при конфликте
// EnvironmentID.
func (suite *functionalSuite) TestBulkCreateInfraEnvironmentsOnConflictUpdate() {
	// сначала создаём один environment с идентификатором 43
	suite.snapshot.Load(suite.T(), dbsnapshot.New(suite.tx))

	// затем создаём его ещё раз: тот же идентификатор, но остальные параметры другие
	replacedEnvironments := []*models.InfraEnvironment{
		{
			EnvironmentID:   43,
			EnvironmentName: "other environment name",
			ServiceID:       24,
			ServiceName:     "other service name",
			Datacenters:     []models.Datacenter{models.DatacenterMAN},
		},
	}
	suite.Nil(suite.tx.BulkCreateInfraEnvironments(context.Background(), replacedEnvironments))

	suite.snapshot.Snapshot(suite.T(), dbsnapshot.New(suite.tx))
}

// TestListInfraEnvironmentsEmpty проверяет случай, когда в базе нет ни одного infra environment.
func (suite *functionalSuite) TestListInfraEnvironmentsEmpty() {
	actual, err := suite.tx.ListInfraEnvironments(context.Background(), nil)
	suite.Nil(err)
	suite.Nil(actual)
}

// TestListInfraEnvironmentsNilFilter проверяет, что возвращаются все infra environment с nil-фильтром.
func (suite *functionalSuite) TestListInfraEnvironmentsNilFilter() {
	suite.snapshot.Load(suite.T(), dbsnapshot.New(suite.tx))
	expected := []*models.InfraEnvironment{
		{
			EnvironmentID:   1,
			EnvironmentName: "test environment1",
			ServiceID:       42,
			ServiceName:     "test service",
			Datacenters:     []models.Datacenter{models.DatacenterIVA},
		},
		{
			EnvironmentID:   2,
			EnvironmentName: "test environment2",
			ServiceID:       42,
			ServiceName:     "test service",
			Datacenters:     []models.Datacenter{models.DatacenterMAN},
		},
	}

	actual, err := suite.tx.ListInfraEnvironments(context.Background(), nil)
	suite.Nil(err)
	suite.Equal(expected, actual)
}

// TestListInfraEnvironmentsEmptyFilter проверяет, что возвращаются все infra environment с пустым фильтром.
func (suite *functionalSuite) TestListInfraEnvironmentsEmptyFilter() {
	suite.snapshot.Load(suite.T(), dbsnapshot.New(suite.tx))
	expected := []*models.InfraEnvironment{
		{
			EnvironmentID:   1,
			EnvironmentName: "test environment1",
			ServiceID:       42,
			ServiceName:     "test service",
			Datacenters:     []models.Datacenter{models.DatacenterIVA},
		},
		{
			EnvironmentID:   2,
			EnvironmentName: "test environment2",
			ServiceID:       42,
			ServiceName:     "test service",
			Datacenters:     []models.Datacenter{models.DatacenterMAN},
		},
	}

	actual, err := suite.tx.ListInfraEnvironments(context.Background(), &models.InfraEnvironmentFilters{})
	suite.Nil(err)
	suite.Equal(expected, actual)
}

// TestListInfraEnvironmentsFilterEnvironmentName проверяет фильтр EnvironmentID.
func (suite *functionalSuite) TestListInfraEnvironmentsFilterEnvironmentName() {
	suite.snapshot.Load(suite.T(), dbsnapshot.New(suite.tx))
	expected := []*models.InfraEnvironment{
		{
			EnvironmentID:   1,
			EnvironmentName: "test environment1",
			ServiceID:       42,
			ServiceName:     "test service",
			Datacenters:     []models.Datacenter{models.DatacenterIVA},
		},
	}

	actual, err := suite.tx.ListInfraEnvironments(context.Background(), &models.InfraEnvironmentFilters{
		EnvironmentName: "test environment1",
	})
	suite.Nil(err)
	suite.Equal(expected, actual)
}

// TestListInfraEnvironmentsFilterServiceName проверяет фильтр ServiceName.
func (suite *functionalSuite) TestListInfraEnvironmentsFilterServiceName() {
	suite.snapshot.Load(suite.T(), dbsnapshot.New(suite.tx))
	expected := []*models.InfraEnvironment{
		{
			EnvironmentID:   1,
			EnvironmentName: "test environment",
			ServiceID:       42,
			ServiceName:     "test service1",
			Datacenters:     []models.Datacenter{models.DatacenterIVA},
		},
	}

	actual, err := suite.tx.ListInfraEnvironments(context.Background(), &models.InfraEnvironmentFilters{
		ServiceName: "test service1",
	})
	suite.Nil(err)
	suite.Equal(expected, actual)
}
