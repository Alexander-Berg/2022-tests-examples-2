package main

import (
	"a.yandex-team.ru/library/go/core/log"
	"a.yandex-team.ru/library/go/core/log/zap"
	"fmt"
	"github.com/DATA-DOG/go-sqlmock"
	"github.com/stretchr/testify/assert"
	"os"
	"testing"
	"time"
)

func setupEnvTest(t *testing.T, envs map[string]string) func(t *testing.T) {
	t.Log("setup environment variables for test")
	for name, value := range envs {
		t.Log("setup environment variable ", name, " to ", value)
		_ = os.Setenv(name, value)
	}
	return func(t *testing.T) {
		for name := range envs {
			t.Log("cleanup environment variable ", name)
			_ = os.Unsetenv(name)
		}
		t.Log("teardown environment variables for test")
	}
}

func TestGetEnvFields(t *testing.T) {
	envs := make(map[string]string)
	envs[proxyNameEnvVar] = "LOLKEK"
	envs["SOME_OTHER_LOVELY_ENV"] = "ABRACADABRA"
	teardown := setupEnvTest(t, envs)
	defer teardown(t)
	fields := getEnvFields()

	assert.Contains(t, fields, log.String(proxyNameEnvVar, "LOLKEK"))
	assert.NotContains(t, fields, log.String("SOME_OTHER_LOVELY_ENV", "ABRACADABRA"))
}

func TestGetProxyMode(t *testing.T) {
	type data struct {
		proxyName string
		proxyMode string
		err       string
	}
	var cases = []data{
		{"presto_ro", "ro", ""},
		{"presto_rw", "rw", ""},
		{"some_other_proxy", "", "Unknown proxy mode"},
		{"", "", fmt.Sprintf("%s is empty", proxyNameEnvVar)},
	}
	for _, tc := range cases {
		t.Run(tc.proxyName, func(t *testing.T) {
			envs := make(map[string]string)
			envs["HAPROXY_PROXY_NAME"] = tc.proxyName
			teardown := setupEnvTest(t, envs)
			defer teardown(t)
			mode, err := getProxyMode()

			assert.Equal(t, mode, tc.proxyMode)
			if (err != nil) || (tc.err != "") {
				assert.EqualError(t, err, tc.err)
			}
		})
	}
}

func TestGetDSN(t *testing.T) {
	defaultCfg := Config{
		User:     "user1",
		Password: "12345678",
	}

	timeoutCfg := Config{
		User:         "user1",
		Password:     "12345678",
		Timeout:      3 * time.Second,
		ReadTimeout:  1 * time.Second,
		WriteTimeout: 1 * time.Second,
	}

	type data struct {
		hostname string
		port     string
		cfg      Config
		dsn      string
		err      string
	}
	errMsg := fmt.Sprintf("%s or %s is empty", serverNameEnvVar, serverPortEnvVar)
	var cases = []data{
		{"example.yandex.net", "3306", defaultCfg, "user1:12345678@tcp(example.yandex.net:3306)/", ""},
		{"example2.yandex.net", "5555", defaultCfg, "user1:12345678@tcp(example2.yandex.net:5555)/", ""},
		{"", "3306", defaultCfg, "", errMsg},
		{"example3.yandex.net", "", defaultCfg, "", errMsg},
		{"example.yandex.net", "3306", timeoutCfg, "user1:12345678@tcp(example.yandex.net:3306)/?readTimeout=1s&timeout=3s&writeTimeout=1s", ""},
	}
	for _, tc := range cases {
		t.Run(fmt.Sprintf("%s:%s", tc.hostname, tc.port), func(t *testing.T) {
			envs := make(map[string]string)
			envs[serverNameEnvVar] = tc.hostname
			envs[serverPortEnvVar] = tc.port
			teardown := setupEnvTest(t, envs)
			defer teardown(t)
			dsn, err := getDSN(&tc.cfg)

			assert.Equal(t, dsn, tc.dsn)
			if (err != nil) || (tc.err != "") {
				assert.EqualError(t, err, tc.err)
			}
		})
	}
}

func TestDoQuery(t *testing.T) {
	db, mock, err := sqlmock.New(sqlmock.MonitorPingsOption(true))
	if err != nil {
		t.Fatalf("an error '%s' was not expected when opening a stub database connection", err)
	}
	defer db.Close()

	columns := []string{
		slaveIOState,
	}
	values := "Waiting for master to send event"

	mock.ExpectPing()
	mock.ExpectQuery("SHOW SLAVE STATUS").WillReturnRows(sqlmock.NewRows(columns).FromCSVString(values))
	_, err = doQuery(db)
	if err != nil {
		t.Fatalf("an error '%s' was not expected while doing query", err)
	}
	if err := mock.ExpectationsWereMet(); err != nil {
		t.Errorf("there were unfulfilled expectations: %s", err)
	}
}

func TestCheckQueryResult(t *testing.T) {
	logger, _ := zap.New(zap.ConsoleConfig(log.ErrorLevel))

	columns := []string{
		slaveIOState,
	}
	values := "Waiting for master to send event"

	type data struct {
		rows    *sqlmock.Rows
		mode    string
		retcode int
	}
	var cases = []data{
		{sqlmock.NewRows(columns).FromCSVString(values), "ro", 0},
		{sqlmock.NewRows(columns).FromCSVString(values), "rw", 1},
		{sqlmock.NewRows([]string{}).FromCSVString(""), "ro", 0},
		{sqlmock.NewRows([]string{}).FromCSVString(""), "rw", 0},
	}
	for _, tc := range cases {
		t.Run(fmt.Sprintf("%v:%s", tc.rows, tc.mode), func(t *testing.T) {
			db, mock, err := sqlmock.New(sqlmock.MonitorPingsOption(true))
			if err != nil {
				t.Fatalf("an error '%s' was not expected when opening a stub database connection", err)
			}
			defer db.Close()

			mock.ExpectPing()
			mock.ExpectQuery("SHOW SLAVE STATUS").WillReturnRows(tc.rows)
			rows, _ := doQuery(db)
			retcode, _ := checkQueryResult(rows, tc.mode, logger)

			assert.Equal(t, retcode, tc.retcode)
		})
	}
}
