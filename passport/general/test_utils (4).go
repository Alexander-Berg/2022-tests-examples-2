package storage

import (
	"database/sql"
	"errors"
	"os"

	_ "github.com/mattn/go-sqlite3"

	"a.yandex-team.ru/passport/infra/daemons/yasmsd/internal/config"
	"a.yandex-team.ru/passport/infra/daemons/yasmsd/internal/utils"
)

// Создание тестовой базы SQLite (база в памяти для тестов).
func CreateTestSQLiteDatabase(filename string) (*Storage, error) {
	schema, err := utils.FileContents(filename)
	if err != nil {
		return nil, err
	}

	db, err := sql.Open("sqlite3", "file:test.db?cache=shared&mode=memory")
	if err != nil {
		return nil, err
	}

	_, err = db.Exec(schema)
	if err != nil {
		_ = db.Close()
		return nil, err
	}

	return &Storage{
		DB:   db,
		Host: "localhost",
		URL:  "memory:file/test.db",
	}, nil
}

// Создание тестовой базы MySQL (интеграционное и нагрузочное тестирование).
func CreateTestMySQLDatabase(filename string) (*Storage, error) {
	schema, err := utils.FileContents(filename)
	if err != nil {
		return nil, err
	}

	storage, err := MysqlDB(
		&Config{
			Host:   "localhost",
			Port:   3306,
			Schema: "smstest",
		},
		&config.Credentials{
			User:     "root",
			Password: "",
		})
	if err != nil {
		return nil, err
	}

	_, err = storage.DB.Exec(schema)
	if err != nil {
		storage.Close()
		return nil, err
	}

	return storage, nil
}

// Создание тестовой базы с типом в зависимости от переменной окружения (STORAGE).
func CreateTestDatabase(filename string) (*Storage, error) {
	t := os.Getenv("STORAGE")
	if t == "MYSQL" {
		return CreateTestMySQLDatabase(filename)
	} else if t == "SQLITE" || len(t) == 0 {
		return CreateTestSQLiteDatabase(filename)
	}

	return nil, errors.New("unknown storage type")
}
