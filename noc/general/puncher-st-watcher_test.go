package main

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"os"
	"testing"

	"github.com/go-chi/chi/v5"
	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/library/go/core/log"
	"a.yandex-team.ru/noc/go/startrek"
	"a.yandex-team.ru/noc/puncher/client/requestsd"
	"a.yandex-team.ru/noc/puncher/client/usersd"
	"a.yandex-team.ru/noc/puncher/lib/logging"
	"a.yandex-team.ru/noc/puncher/mock/configmock"
	"a.yandex-team.ru/noc/puncher/mock/requestsdmock"
	"a.yandex-team.ru/noc/puncher/mock/startrekmock"
	"a.yandex-team.ru/noc/puncher/mock/usersdmock"
	"a.yandex-team.ru/noc/puncher/models"
	"a.yandex-team.ru/noc/puncher/models/modelstest"
)

var testServer *httptest.Server
var usersdServer *usersdmock.Server
var requestsdServer *requestsdmock.Server

var app startrekWatcherApp

var fixturesRequests = make(map[string]models.Request)

func initSnapshot() {
	requests := []models.Request{
		{
			Sources:      []models.Target{modelstest.Alice},
			Destinations: []models.Target{modelstest.CAliceHosts},
			Protocol:     "tcp",
			Locations:    []string{"office", "vpn"},
			Author:       modelstest.Alice,
			Task:         "TEST-2",
			Status:       models.RequestStatusConfirmed,
		},
		{
			Sources:      []models.Target{modelstest.Alice},
			Destinations: []models.Target{modelstest.CAliceHosts},
			Protocol:     "tcp",
			Locations:    []string{"office", "vpn"},
			Author:       modelstest.Alice,
			Task:         "TEST-3",
			Status:       models.RequestStatusNew,
		},
		{
			Sources:      []models.Target{modelstest.Alice},
			Destinations: []models.Target{modelstest.CAliceHosts},
			Protocol:     "tcp",
			Locations:    []string{"office", "vpn"},
			Author:       modelstest.Alice,
			Task:         "TEST-4",
			Status:       models.RequestStatusConfirmed,
		},
		{
			Sources:      []models.Target{modelstest.Alice},
			Destinations: []models.Target{modelstest.CAliceHosts},
			Protocol:     "tcp",
			Locations:    []string{"office", "vpn"},
			Author:       modelstest.Alice,
			Task:         "TEST-5",
			Status:       models.RequestStatusNew,
		},
	}

	for _, request := range requests {
		_request := requestsdServer.InsertRequest(request)
		fixturesRequests[request.Task] = _request
	}
}

func run(m *testing.M) int {
	startrekServer := startrekmock.NewServer()
	defer startrekServer.Close()

	usersdServer = usersdmock.NewServer()
	defer usersdServer.Close()

	requestsdServer = requestsdmock.NewServer()
	defer requestsdServer.Close()

	app = startrekWatcherApp{}

	configService := configmock.NewTestConfig()
	configService.StarTrek.APIV2URL = startrekServer.URL
	starTreckConfig := configService.StarTrek

	app.config = configService.StartrekWatcher
	app.logger = logging.Must(log.InfoLevel)

	app.starTrekClient = &startrek.Client{
		APIV2URL: startrekServer.URL,
		APIToken: starTreckConfig.Token,
		Client: http.Client{
			Timeout: starTreckConfig.Timeout.Duration,
		},
		UserAgent: "Puncher",
	}
	app.usersdClient = usersd.NewClient(usersdServer.URL)
	app.requestsdClient = requestsd.NewClient(requestsdServer.URL)

	r := chi.NewRouter()
	r.MethodFunc(http.MethodPost, "/", starTrekUpdateHandler(&app))

	testServer = httptest.NewServer(r)
	defer testServer.Close()

	initSnapshot()

	return m.Run()
}

func TestMain(m *testing.M) {
	exitCode := run(m)

	// teardown

	os.Exit(exitCode)
}

func TestInit(t *testing.T) {
	usersdServer.SetSuperUsers("%supreme%")

	err := app.Init()
	if err != nil {
		t.Errorf("init failed: %s", err)
	}

	request, ok := requestsdServer.GetRequest(fixturesRequests["TEST-2"].ID)
	assert.True(t, ok)
	assert.True(t, request.SIBDiscussion)

	request, ok = requestsdServer.GetRequest(fixturesRequests["TEST-3"].ID)
	assert.True(t, ok)
	assert.False(t, request.SIBDiscussion)
	assert.True(t, request.ResponsibleDiscussion)
}

func TestNewUpdates(t *testing.T) {
	request, ok := requestsdServer.GetRequest(fixturesRequests["TEST-4"].ID)
	if !ok {
		t.Fatalf("Error while getting request: not found")
	}
	assert.False(t, request.SIBDiscussion)

	usersdServer.SetSuperUsers("%supreme2%")

	update := startTrekEvent{
		Event: event{},
		Issue: issue{
			Key: "TEST-4",
		},
	}

	data, err := json.Marshal(update)
	if err != nil {
		t.Fatal(err)
	}

	req, err := http.NewRequest("POST", testServer.URL, bytes.NewBuffer(data))
	assert.NoError(t, err)
	req.Header.Add("Content-Type", "application/json")

	client := &http.Client{}
	resp, err := client.Do(req)

	assert.NoError(t, err)

	assert.Equal(t, resp.StatusCode, 200)

	request, ok = requestsdServer.GetRequest(fixturesRequests["TEST-4"].ID)
	if !ok {
		t.Fatalf("Error while getting request: not found")
	}
	assert.True(t, request.SIBDiscussion)
}

func TestChangeStatus(t *testing.T) {
	usersdServer.SetSuperUsers("%supreme%")

	update := startTrekEvent{
		Event: event{},
		Issue: issue{
			Key: "TEST-5",
		},
	}

	data, err := json.Marshal(update)
	if err != nil {
		t.Fatal(err)
	}

	req, err := http.NewRequest("POST", testServer.URL, bytes.NewBuffer(data))
	assert.NoError(t, err)
	req.Header.Add("Content-Type", "application/json")

	client := &http.Client{}
	resp, err := client.Do(req)

	assert.NoError(t, err)

	assert.Equal(t, resp.StatusCode, 200)

	request, ok := requestsdServer.GetRequest(fixturesRequests["TEST-5"].ID)
	if !ok {
		t.Fatalf("Error while getting requests: not found")
	}

	assert.True(t, request.ResponsibleDiscussion)
	assert.False(t, request.SIBDiscussion)

	request.Status = models.RequestStatusConfirmed
	request = requestsdServer.UpdateRequest(request)

	assert.NoError(t, err)

	req, err = http.NewRequest("POST", testServer.URL, bytes.NewBuffer(data))
	assert.NoError(t, err)
	req.Header.Add("Content-Type", "application/json")

	resp, err = client.Do(req)

	assert.NoError(t, err)

	assert.Equal(t, resp.StatusCode, 200)

	request, ok = requestsdServer.GetRequest(fixturesRequests["TEST-5"].ID)
	assert.True(t, ok)
	assert.True(t, request.SIBDiscussion)
}
