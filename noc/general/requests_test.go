package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"net/http/httptest"
	"net/url"
	"os"
	"reflect"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/library/go/core/log"
	"a.yandex-team.ru/library/go/yandex/blackbox/httpbb"
	"a.yandex-team.ru/library/go/yandex/tvm/tvmauth"
	"a.yandex-team.ru/noc/puncher/client/macrosd"
	"a.yandex-team.ru/noc/puncher/client/requestsd"
	"a.yandex-team.ru/noc/puncher/client/rulesd"
	"a.yandex-team.ru/noc/puncher/client/usersd"
	"a.yandex-team.ru/noc/puncher/cmd/puncher-daemon/actions"
	"a.yandex-team.ru/noc/puncher/cmd/puncher-daemon/errors"
	"a.yandex-team.ru/noc/puncher/cmd/puncher-daemon/policy"
	"a.yandex-team.ru/noc/puncher/lib/logging"
	"a.yandex-team.ru/noc/puncher/mock/configmock"
	"a.yandex-team.ru/noc/puncher/mock/macrosdmock"
	"a.yandex-team.ru/noc/puncher/mock/requestsdmock"
	"a.yandex-team.ru/noc/puncher/mock/rulesdmock"
	"a.yandex-team.ru/noc/puncher/mock/startrekmock"
	"a.yandex-team.ru/noc/puncher/mock/usersdmock"
	"a.yandex-team.ru/noc/puncher/models"
	"a.yandex-team.ru/noc/puncher/models/modelstest"
)

const (
	respStatusSuccess = "success"
	respStatusError   = "error"
)

var fakeAuth actions.FakeAuth
var testServer *httptest.Server
var rulesdClient rulesd.Client

var (
	dateOneWeekLater    time.Time
	dateThreeMonthLater time.Time
)

func initDates() {
	now := time.Now().Truncate(time.Second)
	dateOneWeekLater = now.AddDate(0, 0, 7)
	dateThreeMonthLater = now.AddDate(0, 3, 0)
}

type CreateRequestTest struct {
	name        string
	currentUser models.Target
	rule        *models.Rule
	request     models.Request
	err         errors.HTTPError
}

var createRequestTests []CreateRequestTest

func initCreateRequestTests() {
	createRequestTests = []CreateRequestTest{
		{
			"create test case #1",
			modelstest.Alice,
			nil,
			models.Request{
				Sources:      []models.Target{modelstest.DptYandexMnt},
				Destinations: []models.Target{modelstest.CAliceHosts},
				Protocol:     "tcp",
				Locations:    []string{"office", "vpn"},
				Comment:      "test case #1",
			},
			nil,
		},
		{
			"create test case #2",
			modelstest.Alice,
			nil,
			models.Request{
				Sources:      []models.Target{modelstest.Alice},
				Destinations: []models.Target{modelstest.CAliceHosts},
				Protocol:     "tcp",
				Locations:    []string{"office", "vpn"},
				Until:        &dateOneWeekLater,
				Comment:      "test case #2",
			},
			nil,
		},
		{
			"create test case #3",
			modelstest.Alice,
			nil,
			models.Request{
				Sources:      []models.Target{modelstest.Alice},
				Destinations: []models.Target{modelstest.CAliceHosts},
				Protocol:     "tcp",
				Locations:    []string{"office", "vpn"},
				Until:        &dateThreeMonthLater,
				Comment:      "test case #3",
			},
			policy.ErrLongDurationForRuleWithLogin,
		},
		{
			"create test case #4",
			modelstest.Alice,
			nil,
			models.Request{
				Sources:      []models.Target{modelstest.Alice},
				Destinations: []models.Target{modelstest.CAliceHosts},
				Protocol:     "tcp",
				Locations:    []string{"office", "vpn"},
				Until:        nil,
				Comment:      "test case #4",
			},
			policy.ErrLongDurationForRuleWithLogin,
		},
		{
			"create test case #5",
			modelstest.Supreme,
			nil,
			models.Request{
				Sources:      []models.Target{modelstest.Alice},
				Destinations: []models.Target{modelstest.CAliceHosts},
				Protocol:     "tcp",
				Locations:    []string{"office", "vpn"},
				Until:        &dateThreeMonthLater,
				Comment:      "test case #5",
			},
			nil,
		},
		{
			"create test case #6",
			modelstest.Alice,
			&models.Rule{
				Sources:      models.MakeRuleTargets([]models.Target{modelstest.Alice}),
				Destinations: models.MakeRuleTargets([]models.Target{modelstest.CAliceHosts}),
				Protocol:     "tcp",
				Locations:    []string{"office", "vpn"},
				Until:        &dateThreeMonthLater,
				Status:       "active",
				System:       models.RuleSystemPuncher,
			},
			models.Request{
				Sources:      []models.Target{modelstest.Alice, modelstest.DptYandexMnt},
				Destinations: []models.Target{modelstest.CAliceHosts},
				Protocol:     "tcp",
				Locations:    []string{"office", "vpn"},
				Until:        &dateThreeMonthLater,
				Comment:      "test case #6",
			},
			nil,
		},
		{
			"create test case #7",
			modelstest.Alice,
			&models.Rule{
				Sources:      models.MakeRuleTargets([]models.Target{modelstest.Alice}),
				Destinations: models.MakeRuleTargets([]models.Target{modelstest.CAliceHosts}),
				Protocol:     "tcp",
				Locations:    []string{"office", "vpn"},
				Until:        &dateThreeMonthLater,
				Status:       "active",
				System:       models.RuleSystemPuncher,
			},
			models.Request{
				Sources:      []models.Target{modelstest.Alice, modelstest.Bob},
				Destinations: []models.Target{modelstest.CAliceHosts},
				Protocol:     "tcp",
				Locations:    []string{"office", "vpn"},
				Until:        &dateThreeMonthLater,
				Comment:      "test case #7",
			},
			policy.ErrLongDurationForRuleWithLogin,
		},
		{
			"create test case #8",
			modelstest.Alice,
			&models.Rule{
				Sources:      models.MakeRuleTargets([]models.Target{modelstest.Alice}),
				Destinations: models.MakeRuleTargets([]models.Target{modelstest.CAliceHosts}),
				Protocol:     "tcp",
				Locations:    []string{"office", "vpn"},
				Until:        &dateOneWeekLater,
				Status:       "active",
				System:       models.RuleSystemPuncher,
			},
			models.Request{
				Sources:      []models.Target{modelstest.Alice},
				Destinations: []models.Target{modelstest.CAliceHosts},
				Protocol:     "tcp",
				Locations:    []string{"office", "vpn"},
				Until:        nil,
				Comment:      "test case #8",
			},
			policy.ErrChangeDurationForRuleWithLogin,
		},
		{
			"create test case #9",
			modelstest.Alice,
			&models.Rule{
				Sources:      models.MakeRuleTargets([]models.Target{modelstest.Alice}),
				Destinations: models.MakeRuleTargets([]models.Target{modelstest.CAliceHosts}),
				Protocol:     "tcp",
				Locations:    []string{"office", "vpn"},
				Until:        &dateOneWeekLater,
				Status:       "active",
				System:       models.RuleSystemPuncher,
			},
			models.Request{
				Sources:      []models.Target{modelstest.DptYandexMnt},
				Destinations: []models.Target{modelstest.CAliceHosts},
				Protocol:     "tcp",
				Locations:    []string{"office", "vpn"},
				Until:        nil,
				Comment:      "test case #9",
			},
			nil,
		},
		{
			"create test case #10",
			modelstest.Alice,
			&models.Rule{
				Sources:      models.MakeRuleTargets([]models.Target{modelstest.Alice}),
				Destinations: models.MakeRuleTargets([]models.Target{modelstest.CAliceHosts}),
				Protocol:     "tcp",
				Locations:    []string{"office", "vpn"},
				Until:        nil,
				Status:       "active",
				System:       models.RuleSystemPuncher,
			},
			models.Request{
				Sources:      []models.Target{modelstest.Alice},
				Destinations: []models.Target{modelstest.CAnotherAliceHosts},
				Protocol:     "tcp",
				Locations:    []string{"office", "vpn"},
				Until:        nil,
				Comment:      "test case #10",
			},
			nil,
		},
		{
			"create test case #11",
			modelstest.Alice,
			&models.Rule{
				Sources:      models.MakeRuleTargets([]models.Target{modelstest.Alice}),
				Destinations: models.MakeRuleTargets([]models.Target{modelstest.CAliceHosts}),
				Protocol:     "tcp",
				Locations:    []string{"office", "vpn"},
				Until:        nil,
				Status:       "active",
				System:       models.RuleSystemPuncher,
			},
			models.Request{
				Sources:      []models.Target{modelstest.Alice},
				Destinations: []models.Target{modelstest.CShared},
				Protocol:     "tcp",
				Locations:    []string{"office", "vpn"},
				Until:        nil,
				Comment:      "test case #11",
			},
			nil,
		},
		{
			"create test case #12",
			modelstest.Alice,
			&models.Rule{
				Sources:      models.MakeRuleTargets([]models.Target{modelstest.Alice}),
				Destinations: models.MakeRuleTargets([]models.Target{modelstest.CAliceHosts}),
				Protocol:     "tcp",
				Locations:    []string{"office", "vpn"},
				Until:        nil,
				Status:       "active",
				System:       models.RuleSystemCAuth,
				ReadOnly:     true,
			},
			models.Request{
				Sources:      []models.Target{modelstest.Alice},
				Destinations: []models.Target{modelstest.CShared},
				Protocol:     "tcp",
				Locations:    []string{"office", "vpn"},
				Until:        nil,
				Comment:      "test case #12",
			},
			actions.ErrEditGeneratedRule,
		},
		{
			"create test case #13",
			modelstest.Alice,
			&models.Rule{
				Sources:      models.MakeRuleTargets([]models.Target{modelstest.CAliceHosts}),
				Destinations: models.MakeRuleTargets([]models.Target{modelstest.CAliceHosts}),
				Protocol:     "tcp",
				Locations:    []string{"office", "vpn"},
				Until:        nil,
				Status:       "active",
				System:       models.RuleSystemBigPuncher,
			},
			models.Request{
				Sources:      []models.Target{modelstest.CAliceHosts},
				Destinations: []models.Target{modelstest.CShared},
				Protocol:     "tcp",
				Locations:    []string{"office", "vpn"},
				Until:        nil,
				Comment:      "test case #13",
			},
			nil,
		},
		{
			"create test case #14",
			modelstest.Alice,
			nil,
			models.Request{
				Sources:      []models.Target{modelstest.Alice, modelstest.DptYandexMnt},
				Destinations: []models.Target{modelstest.CAliceHosts},
				Protocol:     "invalid",
				Locations:    []string{"office", "vpn"},
				Until:        &dateOneWeekLater,
				Comment:      "test case #14",
			},
			errors.NewBadValueError("protocol", "invalid"),
		},
	}
}

var updateRequestTests []struct {
	name         string
	currentUser  models.Target
	rule         *models.Rule
	firstRequest models.Request
	request      models.Request
	err          errors.HTTPError
}

func initUpdateRequestTests() {
	updateRequestTests = []struct {
		name         string
		currentUser  models.Target
		rule         *models.Rule
		firstRequest models.Request
		request      models.Request
		err          errors.HTTPError
	}{
		{
			"update test case #1",
			modelstest.Alice,
			&models.Rule{
				Sources:      models.MakeRuleTargets([]models.Target{modelstest.Alice, modelstest.Bob}),
				Destinations: models.MakeRuleTargets([]models.Target{modelstest.CAliceHosts}),
				Protocol:     "tcp",
				Locations:    []string{"office", "vpn"},
				Until:        &dateThreeMonthLater,
				Status:       "active",
			},
			models.Request{
				Sources:      []models.Target{modelstest.Alice, modelstest.Bob},
				Destinations: []models.Target{modelstest.CAliceHosts},
				Protocol:     "tcp",
				Locations:    []string{"office", "vpn"},
				Until:        &dateThreeMonthLater,
				Comment:      "update test case #1",
				Author:       modelstest.Alice,
				Task:         "TEST-1",
				Status:       "new",
			},
			models.Request{
				Sources:      []models.Target{modelstest.Alice, modelstest.DptYandexMnt},
				Destinations: []models.Target{modelstest.CAliceHosts},
				Protocol:     "tcp",
				Locations:    []string{"office", "vpn"},
				Until:        &dateThreeMonthLater,
				Comment:      "update test case #1",
			},
			nil,
		},
		{
			"update test case #2",
			modelstest.Alice,
			&models.Rule{
				Sources:      models.MakeRuleTargets([]models.Target{modelstest.Alice, modelstest.Bob}),
				Destinations: models.MakeRuleTargets([]models.Target{modelstest.CAliceHosts}),
				Protocol:     "tcp",
				Locations:    []string{"office", "vpn"},
				Until:        nil,
				Status:       "active",
			},
			models.Request{
				Sources:      []models.Target{modelstest.DptYandexMnt},
				Destinations: []models.Target{modelstest.CAliceHosts},
				Protocol:     "tcp",
				Locations:    []string{"office", "vpn"},
				Until:        nil,
				Comment:      "update test case #2",
				Author:       modelstest.Alice,
				Task:         "TEST-1",
				Status:       "new",
			},
			models.Request{
				Sources:      []models.Target{modelstest.Alice, modelstest.DptYandexMnt},
				Destinations: []models.Target{modelstest.CAliceHosts},
				Protocol:     "tcp",
				Locations:    []string{"office", "vpn"},
				Until:        nil,
				Comment:      "update test case #2",
			},
			nil,
		},
		{
			"update test case #3",
			modelstest.Alice,
			&models.Rule{
				Sources:      models.MakeRuleTargets([]models.Target{modelstest.DptYandexMnt}),
				Destinations: models.MakeRuleTargets([]models.Target{modelstest.CAliceHosts}),
				Protocol:     "tcp",
				Locations:    []string{"office", "vpn"},
				Until:        &dateThreeMonthLater,
				Status:       "active",
			},
			models.Request{
				Sources:      []models.Target{modelstest.Alice},
				Destinations: []models.Target{modelstest.CAliceHosts},
				Protocol:     "tcp",
				Locations:    []string{"office", "vpn"},
				Until:        &dateOneWeekLater,
				Comment:      "update test case #3",
				Author:       modelstest.Alice,
				Task:         "TEST-1",
				Status:       "new",
			},
			models.Request{
				Sources:      []models.Target{modelstest.Alice},
				Destinations: []models.Target{modelstest.CAliceHosts},
				Protocol:     "tcp",
				Locations:    []string{"office", "vpn"},
				Until:        &dateThreeMonthLater,
				Comment:      "update test case #3",
				Author:       modelstest.Alice,
				Task:         "TEST-1",
				Status:       "new",
			},
			policy.ErrLongDurationForRuleWithLogin,
		},
		{
			"update test case #4",
			modelstest.Alice,
			nil,
			models.Request{
				Sources:      []models.Target{modelstest.Alice},
				Destinations: []models.Target{modelstest.CShared},
				Protocol:     "tcp",
				Locations:    []string{"office", "vpn"},
				Until:        &dateOneWeekLater,
				Comment:      "update test case #4",
				Author:       modelstest.Alice,
				Task:         "TEST-1",
				Status:       "new",
			},
			models.Request{
				Sources:      []models.Target{modelstest.Alice, modelstest.Bob},
				Destinations: []models.Target{modelstest.CShared},
				Protocol:     "tcp",
				Locations:    []string{"office", "vpn"},
				Until:        &dateOneWeekLater,
				Comment:      "update test case #4",
			},
			nil,
		},
		{
			"update test case #5",
			modelstest.Eve,
			nil,
			models.Request{
				Sources:      []models.Target{modelstest.Alice},
				Destinations: []models.Target{modelstest.CShared},
				Protocol:     "tcp",
				Locations:    []string{"office", "vpn"},
				Until:        &dateOneWeekLater,
				Comment:      "update test case #5",
				Author:       modelstest.Alice,
				Task:         "TEST-1",
				Status:       "new",
			},
			models.Request{
				Sources:      []models.Target{modelstest.Alice, modelstest.Bob},
				Destinations: []models.Target{modelstest.CShared},
				Protocol:     "tcp",
				Locations:    []string{"office", "vpn"},
				Until:        &dateOneWeekLater,
				Comment:      "update test case #5",
			},
			errors.NewHTTPError(400, "You are not responsible for this request"),
		},
	}
}

var requestsdServer *requestsdmock.Server

func run(m *testing.M) int {
	logger := logging.Must(log.InfoLevel)

	startrekServer := startrekmock.NewServer()
	defer startrekServer.Close()

	usersdServer := usersdmock.NewServer()
	defer usersdServer.Close()

	requestsdServer = requestsdmock.NewServer()
	defer requestsdServer.Close()

	rulesdServer := rulesdmock.NewServer()
	defer rulesdServer.Close()

	macrosdServer := macrosdmock.NewServer()
	defer macrosdServer.Close()

	configService := configmock.NewTestConfig()
	configService.StarTrek.APIV2URL = startrekServer.URL
	// configService.Users.AdminUsers = []string{"%alice%", "%bob%"}
	// configService.Users.SuperUsers = []string{"%supreme%"}

	usersdClient := usersd.NewClient(usersdServer.URL)
	requestsdClient := requestsd.NewClient(requestsdServer.URL)
	rulesdClient = rulesd.NewClient(rulesdServer.URL)
	macrosdClient := macrosd.NewClient(macrosdServer.URL)
	tvm := &tvmauth.Client{}
	bb, err := httpbb.NewIntranet()
	if err != nil {
		panic(err)
	}
	actionsService := actions.Init(
		usersdClient,
		requestsdClient,
		rulesdClient,
		macrosdClient,
		configService,
		bb,
		tvm,
		logger,
	)

	testServer = httptest.NewServer(
		httpHandler(actionsService, fakeAuth.Handler, logger),
	)
	defer testServer.Close()

	initDates()
	initCreateRequestTests()
	initUpdateRequestTests()

	return m.Run()
}

func TestMain(m *testing.M) {
	os.Exit(run(m))
}

func MustMarshalRequest(t *testing.T, req models.Request) []byte {
	var v struct {
		Request struct {
			RuleID       *models.ID `json:"rule_id"`
			Sources      []string   `json:"sources"`
			Destinations []string   `json:"destinations"`
			Protocol     string     `json:"protocol"`
			Ports        []string   `json:"ports"`
			Locations    []string   `json:"locations"`
			Until        *time.Time `json:"until"`
			Comment      string     `json:"comment"`
			// SIBDiscussion bool       `json:"sibdiscussion"`
		} `json:"request"`
	}

	v.Request.RuleID = req.RuleID

	v.Request.Sources = make([]string, len(req.Sources))
	for i := range req.Sources {
		v.Request.Sources[i] = req.Sources[i].MachineName
	}

	v.Request.Destinations = make([]string, len(req.Destinations))
	for i := range req.Destinations {
		v.Request.Destinations[i] = req.Destinations[i].MachineName
	}

	v.Request.Protocol = req.Protocol

	v.Request.Ports = make([]string, len(req.Ports))
	for i := range req.Ports {
		v.Request.Ports[i] = req.Ports[i].Text
	}

	v.Request.Locations = req.Locations
	v.Request.Until = req.Until
	v.Request.Comment = req.Comment

	buf, err := json.Marshal(v)
	if err != nil {
		t.Fatalf("Unable to marshal request %v: %s", req, err)
	}

	return buf
}

func getJSON(method, url string, request []byte, response interface{}) (*http.Response, error) {
	req, err := http.NewRequest(method, url, bytes.NewBuffer(request))
	if err != nil {
		return nil, err
	}
	if request != nil {
		req.Header.Set("Content-Type", "application/json")
	}

	client := &http.Client{}
	res, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer func() {
		_ = res.Body.Close()
	}()

	body, err := ioutil.ReadAll(res.Body)
	if err != nil {
		return res, fmt.Errorf("error reading data: %s", err)
	}

	err = json.Unmarshal(body, &response)
	if err != nil {
		return res, fmt.Errorf("invalid JSON from %s %s: %s (status: %s; body: %#v)", method, url, err, res.Status, string(body))
	}

	return res, nil
}

func TestRequestNoExtraFieldsInErrorResponse(t *testing.T) {
	fakeAuth.Set(modelstest.Alice)

	var response interface{}
	res, err := getJSON("POST", testServer.URL+"/requests", []byte(`{`), &response)
	assert.NoError(t, err)

	assert.Equal(t, res.StatusCode, 400)
	assert.Equal(t, response, map[string]interface{}{
		"status":     "error",
		"error_code": "error",
		"message":    "Bad JSON: unexpected EOF",
		"tanker":     map[string]interface{}{},
		"error_message": map[string]interface{}{
			"ru": "Bad JSON: unexpected EOF",
			"en": "Bad JSON: unexpected EOF",
		},
	})
}

func TestRequestCreateWithUnknownSource(t *testing.T) {
	fakeAuth.Set(modelstest.Supreme)

	var response interface{}
	res, err := getJSON("POST", testServer.URL+"/requests", []byte(`{
			"request": {
				"sources": ["@unknown@"],
				"destinations": ["_C_ALICE_HOSTS_"],
				"protocol": "tcp",
				"locations": ["office", "vpn"],
				"ports": ["80", "1024-9999"],
				"until": null,
				"comment": "Some comment"
			}
		}`), &response)
	assert.NoError(t, err)

	assert.Equal(t, res.StatusCode, 400)
	assert.Equal(t, response, map[string]interface{}{
		"status":  "error",
		"message": "Unknown source @unknown@",
		"tanker": map[string]interface{}{
			"key":     "unknown_source",
			"payload": []interface{}{"@unknown@"},
		},
		"error_code": "unknown_source",
		"error_message": map[string]interface{}{
			"ru": "Unknown source @unknown@",
			"en": "Unknown source @unknown@",
		},
	})
}

func TestRequestNoExtraFieldsInSuccessResponse(t *testing.T) {
	fakeAuth.Set(modelstest.Alice)

	var response interface{}
	res, err := getJSON("POST", testServer.URL+"/requests", []byte(`{
			"request": {
				"sources": ["@dpt_yandex_mnt@"],
				"destinations": ["_C_ALICE_HOSTS_"],
				"protocol": "tcp",
				"locations": ["office", "vpn"],
				"ports": ["80", "1024-9999"],
				"until": null,
				"comment": "Hello, world!"
			}
		}`), &response)
	assert.NoError(t, err)

	var id, added, updated interface{}
	if response, ok := response.(map[string]interface{}); ok {
		if request, ok := response["request"].(map[string]interface{}); ok {
			id = request["id"]
			added = request["added"]
			updated = request["updated"]

			assert.NotZero(t, id)
		}
	}

	assert.Equal(t, res.StatusCode, 200)
	expected := map[string]interface{}{
		"status": "success",
		"request": map[string]interface{}{
			"id":      id,
			"rule_id": nil,
			"type":    "create",
			"sources": []interface{}{
				map[string]interface{}{
					"type":         "department",
					"machine_name": "@dpt_yandex_mnt@",
					"title": map[string]interface{}{
						"en": "Directorate of maintenance",
						"ru": "Департамент эксплуатации",
					},
					"is_deleted":   false,
					"is_user_type": true,
					"external":     false,
				},
			},
			"destinations": []interface{}{
				map[string]interface{}{
					"type":         "conductorgroup",
					"machine_name": "_C_ALICE_HOSTS_",
					"title": map[string]interface{}{
						"en": "_C_ALICE_HOSTS_",
						"ru": "_C_ALICE_HOSTS_",
					},
					"is_deleted":   false,
					"is_user_type": false,
					"external":     false,
				},
			},
			"protocol":  "tcp",
			"locations": []interface{}{"office", "vpn"},
			"ports":     []interface{}{"80", "1024-9999"},
			"until":     nil,
			"status":    "confirmed",
			"author": map[string]interface{}{
				"type":         "user",
				"machine_name": "%alice%",
				"title": map[string]interface{}{
					"en": "Alice",
					"ru": "Алиса",
				},
				"is_deleted":   false,
				"is_user_type": true,
				"external":     false,
				"login":        "alice",
			},
			"comment":               "Hello, world!",
			"task":                  "TEST-1",
			"added":                 added,
			"updated":               updated,
			"sibdiscussion":         false,
			"responsiblediscussion": false,
			"system":                "puncher",
			"responsibles": []interface{}{
				map[string]interface{}{
					"is_deleted":   false,
					"is_user_type": true,
					"external":     false,
					"login":        "alice",
					"machine_name": "%alice%",
					"title": map[string]interface{}{
						"en": "Alice",
						"ru": "Алиса",
					},
					"type": "user",
				},
			},
			"can_approve": false,
			"can_reject":  true,
		},
		"rule": nil,
	}
	assert.Equal(t, response, expected)
}

func TestRequestCreation(t *testing.T) {
	for _, testcase := range createRequestTests {
		fakeAuth.Set(testcase.currentUser)

		request := testcase.request

		if testcase.rule != nil {
			rule, err := rulesdClient.CreateRule(*testcase.rule)
			if err != nil {
				t.Fatalf("%s: unable to insert rule: %s", testcase.name, err)
			}
			request.RuleID = &rule.ID
		}

		var response struct {
			Status  string
			Message string
			Tanker  models.Tanker
			Request struct {
				Task string
			}
		}
		httpResponse, err := getJSON("POST", testServer.URL+"/requests", MustMarshalRequest(t, request), &response)
		if err != nil {
			t.Fatalf("%s: error POSTing request: %s", testcase.name, err)
		}

		if testcase.err == nil {
			if httpResponse.StatusCode != 200 {
				t.Errorf("%s: got http status %d, want 200", testcase.name, httpResponse.StatusCode)
			}
			if response.Status != respStatusSuccess {
				t.Errorf("%s: got status %s, want success", testcase.name, response.Status)
			}
			if response.Message != "" {
				t.Errorf("%s: got message %v", testcase.name, response.Message)
			}
			if !reflect.DeepEqual(response.Tanker, models.Tanker{}) {
				t.Errorf("%s: got tanker %v", testcase.name, response.Tanker)
			}
			if response.Request.Task == "" {
				t.Errorf("%s: got empty task, want non-empty", testcase.name)
			}
		} else {
			if httpResponse.StatusCode == 200 {
				t.Errorf("%s: got http status %d", testcase.name, httpResponse.StatusCode)
			}
			if response.Status != respStatusError {
				t.Errorf("%s: got status %s, want error", testcase.name, response.Status)
			}
			if response.Message != testcase.err.Message() {
				t.Errorf("%s: got message %v, want %v", testcase.name, response.Message, testcase.err.Message())
			}
			assert.Equal(t, response.Tanker, testcase.err.Tanker())
		}
	}
}

func TestRequestCreationUsingUpdate(t *testing.T) {
	for _, testcase := range createRequestTests {
		fakeAuth.Set(testcase.currentUser)

		firstRequest := models.Request{
			Sources:      []models.Target{modelstest.DptYandexMnt},
			Destinations: []models.Target{modelstest.CShared},
			Locations:    []string{"office", "vpn"},
			Status:       "new",
			Task:         "TEST-1",
			Author:       modelstest.Supreme,
		}
		request := testcase.request

		if testcase.rule != nil {
			if testcase.rule.System == models.RuleSystemCAuth {
				continue // there should not be requests for cauth system
			}

			rule, err := rulesdClient.CreateRule(*testcase.rule)
			if err != nil {
				t.Fatalf("%s: unable to insert rule: %s", testcase.name, err)
			}

			firstRequest.RuleID = &rule.ID
			firstRequest = requestsdServer.InsertRequest(firstRequest)

			request.RuleID = &rule.ID
		} else {
			firstRequest = requestsdServer.InsertRequest(firstRequest)
		}

		var response struct {
			Status  string
			Message string
			Tanker  models.Tanker
			Request struct {
				Task string
			}
		}
		httpResponse, err := getJSON("PUT", testServer.URL+"/requests/"+firstRequest.ID.Hex(), MustMarshalRequest(t, request), &response)
		if err != nil {
			t.Errorf("%s: error POSTing request: %s", testcase.name, err)
			continue
		}

		if testcase.err == nil {
			if httpResponse.StatusCode != 200 {
				t.Errorf("%s: got http status %d, want 200", testcase.name, httpResponse.StatusCode)
			}
			if response.Status != respStatusSuccess {
				t.Errorf("%s: got status %s, want success", testcase.name, response.Status)
			}
			if response.Message != "" {
				t.Errorf("%s: got message %v", testcase.name, response.Message)
			}
			if !reflect.DeepEqual(response.Tanker, models.Tanker{}) {
				t.Errorf("%s: got tanker %v", testcase.name, response.Tanker)
			}
			if response.Request.Task == "" {
				t.Errorf("%s: got empty task, want non-empty", testcase.name)
			}
		} else {
			if httpResponse.StatusCode == 200 {
				t.Errorf("%s: got http status %d", testcase.name, httpResponse.StatusCode)
			}
			if response.Status != respStatusError {
				t.Errorf("%s: got status %s, want error", testcase.name, response.Status)
			}
			if response.Message != testcase.err.Message() {
				t.Errorf("%s: got message %v, want %v", testcase.name, response.Message, testcase.err.Message())
			}
			assert.Equal(t, response.Tanker, testcase.err.Tanker())
		}
	}
}

func TestRequestUpdate(t *testing.T) {
	for _, testcase := range updateRequestTests {
		fakeAuth.Set(testcase.currentUser)

		firstRequest := testcase.firstRequest
		request := testcase.request

		if testcase.rule != nil {
			rule, err := rulesdClient.CreateRule(*testcase.rule)
			if err != nil {
				t.Fatalf("%s: unable to insert rule: %s", testcase.name, err)
			}

			firstRequest.RuleID = &rule.ID
			firstRequest = requestsdServer.InsertRequest(firstRequest)

			request.RuleID = &rule.ID
		} else {
			firstRequest = requestsdServer.InsertRequest(firstRequest)
		}

		var response struct {
			Status  string
			Message string
			Tanker  models.Tanker
			Request struct {
				Task string
			}
		}
		httpResponse, err := getJSON("PUT", testServer.URL+"/requests/"+firstRequest.ID.Hex(), MustMarshalRequest(t, request), &response)
		if err != nil {
			t.Errorf("%s: error POSTing request: %s", testcase.name, err)
			continue
		}

		if testcase.err == nil {
			if httpResponse.StatusCode != 200 {
				t.Errorf("%s: got http status %d, want 200", testcase.name, httpResponse.StatusCode)
			}
			if response.Status != respStatusSuccess {
				t.Errorf("%s: got status %s, want success", testcase.name, response.Status)
			}
			if response.Message != "" {
				t.Errorf("%s: got message %v", testcase.name, response.Message)
			}
			if !reflect.DeepEqual(response.Tanker, models.Tanker{}) {
				t.Errorf("%s: got tanker %v", testcase.name, response.Tanker)
			}
			if response.Request.Task == "" {
				t.Errorf("%s: got empty task, want non-empty", testcase.name)
			}
		} else {
			if httpResponse.StatusCode == 200 {
				t.Errorf("%s: got http status %d", testcase.name, httpResponse.StatusCode)
			}
			if response.Status != respStatusError {
				t.Errorf("%s: got status %s, want error", testcase.name, response.Status)
			}
			if response.Message != testcase.err.Message() {
				t.Errorf("%s: got message %v, want %v", testcase.name, response.Message, testcase.err.Message())
			}
			if !reflect.DeepEqual(response.Tanker, testcase.err.Tanker()) {
				t.Errorf("%s: got tanker %v, want %v", testcase.name, response.Tanker, testcase.err.Tanker())
			}
		}
	}
}

func TestRequestDeduplication(t *testing.T) {
	fakeAuth.Set(modelstest.Alice)

	var response struct {
		Status  string
		Request models.Request
	}
	httpResponse, err := getJSON("POST", testServer.URL+"/requests", MustMarshalRequest(t, models.Request{
		Sources:      []models.Target{modelstest.DptYandexMnt, modelstest.Alice, modelstest.DptYandexMnt},
		Destinations: []models.Target{modelstest.CAliceHosts, modelstest.CAliceHosts},
		Protocol:     "tcp",
		Locations:    []string{"office", "vpn"},
		Until:        &dateOneWeekLater,
		Comment:      "deduplication",
	}), &response)
	if err != nil {
		t.Error("Error POSTing request:", err)
	}

	if httpResponse.StatusCode != 200 {
		t.Errorf("got http status %d, want 200", httpResponse.StatusCode)
	}
	if response.Status != respStatusSuccess {
		t.Errorf("got status %s, want success", response.Status)
	}
	if len(response.Request.Sources) != 2 {
		t.Errorf("got %d sources, want 2", len(response.Request.Sources))
	}
	if len(response.Request.Destinations) != 1 {
		t.Errorf("got %d destinations, want 1", len(response.Request.Destinations))
	}
}

func TestRequestApproveRuleCreation(t *testing.T) {
	fakeAuth.Set(modelstest.Supreme)

	var createResponse struct {
		Status string `json:"status"`
		// Message string         `json:"message"`
		Request models.Request `json:"request"`
	}
	_, err := getJSON("POST", testServer.URL+"/requests", []byte(`{
				"request": {
					"sources": ["%alice%"],
					"destinations": ["_C_ALICE_HOSTS_"],
					"protocol": "tcp",
					"locations": ["office", "vpn"],
					"ports": ["80", "1024-9999"],
					"until": null,
					"comment": "Test"
				}
			}`), &createResponse)
	if err != nil {
		t.Fatal(err)
	}

	if createResponse.Status != respStatusSuccess {
		t.Errorf("got response status %q, want %q", createResponse.Status, "success")
	}

	var response interface{}
	res, err := getJSON("POST", testServer.URL+"/requests/"+createResponse.Request.ID.Hex()+"/approve", nil, &response)
	if err != nil {
		t.Fatal(err)
	}

	if res.StatusCode != 200 {
		t.Errorf("got http status %d (%+v), want 200", res.StatusCode, response)
	}

	var requestID, requestAdded, requestUpdated interface{}
	var ruleID, ruleAdded, ruleUpdated interface{}
	if response, ok := response.(map[string]interface{}); ok {
		if request, ok := response["request"].(map[string]interface{}); ok {
			requestID = request["id"]
			requestAdded = request["added"]
			requestUpdated = request["updated"]
		}
		if rule, ok := response["rule"].(map[string]interface{}); ok {
			ruleID = rule["id"]
			ruleAdded = rule["added"]
			ruleUpdated = rule["updated"]
		}
	}
	if requestID == nil {
		t.Fatal("got nil, want request id")
	}
	if requestID != createResponse.Request.ID.Hex() {
		t.Errorf("got request id %q, want %q", requestID, createResponse.Request.ID.Hex())
	}
	if requestAdded != createResponse.Request.Added.Format(time.RFC3339Nano) {
		t.Errorf("got add time %q, want %q", requestAdded, createResponse.Request.Added.Format(time.RFC3339Nano))
	}
	if requestUpdated == createResponse.Request.Updated.Format(time.RFC3339Nano) {
		t.Errorf("got update time %q, want new value", requestUpdated)
	}
	if ruleID == nil {
		t.Fatal("got nil, want rule id")
	}

	if res.StatusCode != 200 {
		t.Errorf("got http status %d, want 200", res.StatusCode)
	}
	expected := map[string]interface{}{
		"status": "success",
		"request": map[string]interface{}{
			"id":      requestID,
			"rule_id": nil,
			"type":    "create",
			"sources": []interface{}{
				map[string]interface{}{
					"type":         "user",
					"machine_name": "%alice%",
					"title": map[string]interface{}{
						"en": "Alice",
						"ru": "Алиса",
					},
					"is_deleted":   false,
					"is_user_type": true,
					"external":     false,
					"login":        "alice",
				},
			},
			"destinations": []interface{}{
				map[string]interface{}{
					"type":         "conductorgroup",
					"machine_name": "_C_ALICE_HOSTS_",
					"title": map[string]interface{}{
						"en": "_C_ALICE_HOSTS_",
						"ru": "_C_ALICE_HOSTS_",
					},
					"is_deleted":   false,
					"is_user_type": false,
					"external":     false,
				},
			},
			"protocol":  "tcp",
			"locations": []interface{}{"office", "vpn"},
			"ports":     []interface{}{"80", "1024-9999"},
			"until":     nil,
			"status":    "approved",
			"author": map[string]interface{}{
				"type":         "user",
				"machine_name": "%supreme%",
				"title": map[string]interface{}{
					"en": "Supreme User",
					"ru": "Верховный Пользователь",
				},
				"is_deleted":   false,
				"is_user_type": true,
				"external":     false,
				"login":        "supreme",
			},
			"comment":               "Test",
			"task":                  "TEST-1",
			"added":                 requestAdded,
			"updated":               requestUpdated,
			"sibdiscussion":         false,
			"responsiblediscussion": false,
			"system":                "puncher",
			"responsibles": []interface{}{
				map[string]interface{}{
					"is_deleted":   false,
					"is_user_type": true,
					"external":     false,
					"login":        "alice",
					"machine_name": "%alice%",
					"title": map[string]interface{}{
						"en": "Alice",
						"ru": "Алиса",
					},
					"type": "user",
				},
			},
			"can_approve": false,
			"can_reject":  false,
		},
		"rule": map[string]interface{}{
			"id": ruleID,
			"sources": []interface{}{
				map[string]interface{}{
					"type":         "user",
					"machine_name": "%alice%",
					"title": map[string]interface{}{
						"en": "Alice",
						"ru": "Алиса",
					},
					"is_deleted":   false,
					"is_user_type": true,
					"external":     false,
					"login":        "alice",
				},
			},
			"destinations": []interface{}{
				map[string]interface{}{
					"type":         "conductorgroup",
					"machine_name": "_C_ALICE_HOSTS_",
					"title": map[string]interface{}{
						"en": "_C_ALICE_HOSTS_",
						"ru": "_C_ALICE_HOSTS_",
					},
					"is_deleted":   false,
					"is_user_type": false,
					"external":     false,
				},
			},
			"protocol":  "tcp",
			"readonly":  false,
			"locations": []interface{}{"office", "vpn"},
			"ports":     []interface{}{"80", "1024-9999"},
			"until":     nil,
			"status":    "active",
			"tasks":     []interface{}{"TEST-1"},
			"comment":   "Test",
			"system":    "puncher",
			"added":     ruleAdded,
			"updated":   ruleUpdated,
		},
	}
	assert.Equal(t, response, expected)
}

func TestRequestRejectRuleCreation(t *testing.T) {
	fakeAuth.Set(modelstest.Alice)
	validDate := time.Now().AddDate(0, 1, 26).Format(time.RFC3339)

	var createResponse struct {
		Status string `json:"status"`
		// Message string         `json:"message"`
		Request models.Request `json:"request"`
	}
	_, err := getJSON("POST", testServer.URL+"/requests", []byte(`{
				"request": {
					"sources": ["%alice%"],
					"destinations": ["_C_ALICE_HOSTS_"],
					"protocol": "tcp",
					"locations": ["office", "vpn"],
					"ports": ["80", "1024-9999"],
					"until": "`+validDate+`",
					"comment": "Test"
				}
			}`), &createResponse)
	if err != nil {
		t.Fatal(err)
	}

	if createResponse.Status != "success" {
		t.Errorf("got response status %q, want %q", createResponse.Status, "success")
	}

	fakeAuth.Set(modelstest.Supreme)

	var response interface{}
	res, err := getJSON("POST", testServer.URL+"/requests/"+createResponse.Request.ID.Hex()+"/reject", nil, &response)
	if err != nil {
		t.Fatal(err)
	}

	if res.StatusCode != 200 {
		t.Errorf("got http status %d, want 200; response: %+v", res.StatusCode, response)
	}

	var requestID, requestAdded, requestUpdated interface{}
	if response, ok := response.(map[string]interface{}); ok {
		if request, ok := response["request"].(map[string]interface{}); ok {
			requestID = request["id"]
			requestAdded = request["added"]
			requestUpdated = request["updated"]
		}
	}
	if requestID == nil {
		t.Fatal("got nil, want request id")
	}
	if requestID != createResponse.Request.ID.Hex() {
		t.Errorf("got request id %q, want %q", requestID, createResponse.Request.ID.Hex())
	}
	if requestAdded != createResponse.Request.Added.Format(time.RFC3339Nano) {
		t.Errorf("got add time %q, want %q", requestAdded, createResponse.Request.Added.Format(time.RFC3339Nano))
	}
	if requestUpdated == createResponse.Request.Updated.Format(time.RFC3339Nano) {
		t.Errorf("got update time %q, want new value", requestUpdated)
	}

	jsonRequest := map[string]interface{}{
		"id":      requestID,
		"rule_id": nil,
		"type":    "create",
		"sources": []interface{}{
			map[string]interface{}{
				"type":         "user",
				"machine_name": "%alice%",
				"title": map[string]interface{}{
					"en": "Alice",
					"ru": "Алиса",
				},
				"is_deleted":   false,
				"is_user_type": true,
				"external":     false,
				"login":        "alice",
			},
		},
		"destinations": []interface{}{
			map[string]interface{}{
				"type":         "conductorgroup",
				"machine_name": "_C_ALICE_HOSTS_",
				"title": map[string]interface{}{
					"en": "_C_ALICE_HOSTS_",
					"ru": "_C_ALICE_HOSTS_",
				},
				"is_deleted":   false,
				"is_user_type": false,
				"external":     false,
			},
		},
		"protocol":  "tcp",
		"locations": []interface{}{"office", "vpn"},
		"ports":     []interface{}{"80", "1024-9999"},
		"until":     validDate,
		"status":    "closed_by_security",
		"author": map[string]interface{}{
			"type":         "user",
			"machine_name": "%alice%",
			"title": map[string]interface{}{
				"en": "Alice",
				"ru": "Алиса",
			},
			"is_deleted":   false,
			"is_user_type": true,
			"external":     false,
			"login":        "alice",
		},
		"comment":               "Test",
		"task":                  "TEST-1",
		"added":                 requestAdded,
		"updated":               requestUpdated,
		"sibdiscussion":         false,
		"responsiblediscussion": false,
		"system":                "puncher",
		"responsibles": []interface{}{
			map[string]interface{}{
				"is_deleted":   false,
				"is_user_type": true,
				"external":     false,
				"login":        "alice",
				"machine_name": "%alice%",
				"title": map[string]interface{}{
					"en": "Alice",
					"ru": "Алиса",
				},
				"type": "user",
			},
		},
		"can_approve": false,
		"can_reject":  false,
	}

	if res.StatusCode != 200 {
		t.Errorf("got http status %d, want 200", res.StatusCode)
	}
	expected := map[string]interface{}{
		"status":  "success",
		"request": jsonRequest,
	}
	assert.Equal(t, response, expected)

	url := testServer.URL + "/requests?" + url.Values{"id": {requestID.(string)}}.Encode()

	var getResponse map[string]interface{}
	_, err = getJSON("GET", url, nil, &getResponse)
	assert.NoError(t, err)

	jsonRequest["can_reject"] = false
	jsonRequest["can_approve"] = false

	expected = map[string]interface{}{
		"status":   "success",
		"requests": []interface{}{jsonRequest},
		"count":    1.0,
		"links":    map[string]interface{}{"first": url},
		"search": map[string]interface{}{
			"id": requestID.(string),
		},
	}
	assert.Equal(t, getResponse, expected)
}
