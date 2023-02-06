package testhelpers

import (
	"fmt"
	"os"
	"path"
	"runtime"

	"a.yandex-team.ru/library/go/test/yatest"
)

const (
	defaultPostgresURI = "postgres://postgres:postgres@localhost/rfcs"
)

func GetMigrationsDir() string {
	var migrationsDir string

	// если тесты через `ya make`, то будет выставлена переменная окружения макросом `ENV(YA_MAKE_TEST_RUN=1)`
	if os.Getenv("YA_MAKE_TEST_RUN") != "" {
		// ищем миграции тестовым данным, поставляемым макросом `DATA(arcadia/noc/nocrfcsd/migrations)`
		migrationsDir = yatest.SourcePath("noc/nocrfcsd/migrations")
	} else { // тесты напрямую через `go test` без участия `ya make`
		_, filename, _, ok := runtime.Caller(0)
		if !ok {
			panic("could not detect current test file name")
		}
		pkgDir := path.Dir(filename)
		internalDir := path.Dir(pkgDir)
		projectDir := path.Dir(internalDir)
		migrationsDir = path.Join(projectDir, "migrations")
	}
	return migrationsDir
}

func GetDatabaseConnectionString() string {
	// если тесты через ya make, то будет использован рецепт `antiadblock/postgres_local/recipe`,
	// который выставит переменные окружения `PG_*`
	user := os.Getenv("PG_LOCAL_USER")
	password := os.Getenv("PG_LOCAL_PASSWORD")
	dbName := os.Getenv("PG_LOCAL_DATABASE")
	port := os.Getenv("PG_LOCAL_PORT")
	if user != "" && password != "" && port != "" && dbName != "" {
		return fmt.Sprintf("user=%s password=%s host=localhost port=%s dbname=%s", user, password, port, dbName)
	}

	// если переменных окружения нет, то позволяем разработчику указать кастомный URI
	uri := os.Getenv("POSTGRES_URI")
	if uri != "" {
		return uri
	}

	// по-умолчанию используем локальный postgres с популярными параметрами (логин/пароль)
	return defaultPostgresURI
}
