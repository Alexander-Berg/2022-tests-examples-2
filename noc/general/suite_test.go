package db

import (
	"context"
	"testing"

	"github.com/stretchr/testify/suite"

	"a.yandex-team.ru/library/go/core/log/nop"
	"a.yandex-team.ru/library/go/test/yatest"
	"a.yandex-team.ru/noc/nocrfcsd/internal/repository"
	"a.yandex-team.ru/noc/nocrfcsd/internal/snapshot"
	"a.yandex-team.ru/noc/nocrfcsd/internal/testhelpers"
	"a.yandex-team.ru/noc/nocrfcsd/internal/uuidgenerator"
)

type functionalSuite struct {
	suite.Suite
	db *PostgresDatabase
	// общая транзакция на все тесты пакеты
	rootTx repository.Repository
	// транзакция на один тест пакета
	tx repository.Repository

	snapshot *snapshot.Config
}

func (suite *functionalSuite) SetupSuite() {
	var err error

	suite.snapshot = snapshot.New(snapshot.PackageSourcePath(yatest.SourcePath("noc/nocrfcsd/internal/db")))

	uuidgen := uuidgenerator.NewPredictableWithSeed(42)

	logger := (&nop.Logger{}).Logger()

	suite.db = NewPostgresDatabase(context.Background(), testhelpers.GetDatabaseConnectionString(), uuidgen, logger)
	if err := suite.db.Init(); err != nil {
		panic(err)
	}

	// Трюк в том, что миграции применяются один раз на все тесты пакета, а сами тесты изолируются через "вложенные
	// транзакции", которые на самом деле представляют собой SAVEPOINT-ы. Это даёт следующие возможности:
	// - ускоряет тесты: откат к savepoint-у быстрее очистки или пересоздания схемы/базы
	// - не требует логики очистки базы после тестов
	// - позволяет выполнять параллельные тесты (go test ./... -parallel 10)
	//
	// Например, для двух тестов в пакете будут выполняться следующие SQL-инструкции:
	//
	// BEGIN;  -- в SetupSuite начинается транзакция
	// CREATE TABLE ...;  -- в SetupSuite применяются миграции внутри транзакции
	// SAVEPOINT SP1;  -- в BeforeTest начинается "вложенная транзакция" для первого теста
	// INSERT ...;  -- выполняется код первого теста
	// ROLLBACK TO SAVEPOINT SP1;  -- в AfterTest откатывается "вложенная транзакция" первого теста
	// SAVEPOINT SP1;  -- это BeforeTest для второго теста
	// INSERT ...;  -- выполняется код второго теста
	// ROLLBACK TO SAVEPOINT SP1;  -- это AfterTest для второго теста
	// ROLLBACK;  -- в TearDownSuite откатывается транзакция, оставляя базу чистой

	suite.rootTx, err = suite.db.Begin(context.Background())
	if err != nil {
		panic(err)
	}

	if err := suite.rootTx.Migrate(context.Background(), testhelpers.GetMigrationsDir()); err != nil {
		panic(err)
	}
}

func (suite *functionalSuite) TearDownSuite() {
	suite.rootTx.Rollback(context.Background())
}

func (suite *functionalSuite) BeforeTest(suiteName, testName string) {
	var err error
	suite.tx, err = suite.rootTx.Begin(context.Background())
	if err != nil {
		panic(err)
	}
}

func (suite *functionalSuite) AfterTest(suiteName, testName string) {
	suite.tx.Rollback(context.Background())
}

func TestFunctionalSuite(t *testing.T) {
	suite.Run(t, new(functionalSuite))
}
