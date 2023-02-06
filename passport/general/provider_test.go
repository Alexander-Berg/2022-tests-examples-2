package mysql

import (
	"bytes"
	"fmt"
	"os"
	"os/exec"
	"path"
	"strconv"
	"testing"

	"github.com/jmoiron/sqlx"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/test/yatest"
)

func getSourcePath() string {
	return yatest.SourcePath("passport/infra/daemons/yasms_internal/internal/model/mysql")
}

func makeConfig() ProviderConfig {
	mysqlPort, err := strconv.Atoi(os.Getenv("RECIPE_MYSQL_PORT"))
	if err != nil {
		panic(err)
	}

	return ProviderConfig{
		DBName:       "sms",
		Host:         "127.0.0.1",
		UsernameFile: path.Join(getSourcePath(), "gotest/mysql.user"),
		PasswordFile: path.Join(getSourcePath(), "gotest/mysql.password"),
		Port:         uint16(mysqlPort),
		Lazy:         false,
	}
}

func initProviderWithConfig(config ProviderConfig) (*Provider, error) {
	mysqlPath := os.Getenv("RECIPE_MYSQL_DIR")
	if mysqlPath == "" {
		panic("no mysql executable is specified")
	}

	cmd := exec.Command(path.Join(mysqlPath, "mysql"),
		"-u", "root",
		"-h", config.Host, "-P", strconv.Itoa(int(config.Port)),
		"-e", "source "+path.Join(getSourcePath(), "gotest/sms.sql"))
	var stdout bytes.Buffer
	var stderr bytes.Buffer
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr
	err := cmd.Run()

	if err != nil {
		fmt.Printf("%s\n---------\n%s\n", stdout.String(), stderr.String())
		panic(err)
	}

	return NewMySQLProvider(config)
}

func initProvider() (*Provider, error) {
	return initProviderWithConfig(makeConfig())
}

func TestMySQLProvider_New(t *testing.T) {
	provider, err := initProvider()
	require.NoErrorf(t, err, "Failed to init db")
	err = provider.Ping()
	require.NoErrorf(t, err, "Failed to ping db")
}

func TestMySQLProvider_FailedInit(t *testing.T) {
	config := makeConfig()
	config.PasswordFile = "kek.txt"
	_, err := initProviderWithConfig(config)
	require.Error(t, err)

	config = makeConfig()
	config.UsernameFile = "kek.txt"
	_, err = initProviderWithConfig(config)
	require.Error(t, err)

	config = makeConfig()
	config.DBName = "non-existent-db"
	_, err = initProviderWithConfig(config)
	require.Error(t, err)
}

func TestMySQLProvider_Lazy(t *testing.T) {
	config := makeConfig()
	config.Lazy = true
	config.DBName = "asdf"
	provider, err := initProviderWithConfig(config)
	require.NoError(t, err)
	_, err = provider.withDriver(func(*sqlx.DB) (interface{}, error) {
		return nil, nil
	})
	require.Error(t, err)
	provider.config.DBName = "sms"
	_, err = provider.withDriver(func(*sqlx.DB) (interface{}, error) {
		return nil, nil
	})
	require.NoError(t, err)
}
