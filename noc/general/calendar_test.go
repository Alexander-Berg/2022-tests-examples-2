package app

import (
	"testing"
	"time"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/library/go/core/log"
	"a.yandex-team.ru/noc/puncher/client/calendar"
	"a.yandex-team.ru/noc/puncher/config"
	"a.yandex-team.ru/noc/puncher/lib/logging"
	"a.yandex-team.ru/noc/puncher/mock/calendarmock"
	"a.yandex-team.ru/noc/puncher/models"
)

type testCase struct {
	day      time.Time
	expected bool
}

func TestIsHoliday(t *testing.T) {
	testServer := calendarmock.NewServer()

	var testCases []testCase

	testCases = append(testCases, testCase{
		day:      time.Date(2021, 12, 31, 0, 0, 0, 0, time.Now().Location()),
		expected: true},
	)

	for i := 0; i < 8; i++ {
		testCases = append(testCases, testCase{
			day:      time.Date(2022, 1, 1+i, 0, 0, 0, 0, time.Now().Location()),
			expected: true},
		)
	}

	for i := 0; i < 5; i++ {
		testCases = append(testCases, testCase{
			day:      time.Date(2022, 1, 10+i, 0, 0, 0, 0, time.Now().Location()),
			expected: false},
		)
	}

	for i := 0; i < 2; i++ {
		testCases = append(testCases, testCase{
			day:      time.Date(2022, 1, 15+i, 0, 0, 0, 0, time.Now().Location()),
			expected: true},
		)
	}

	cfgd := config.CfgDuration{}
	cfgd.Duration = 10 * time.Second
	conf := config.CalendarConfig{
		BaseURL: testServer.URL,
		TimeOut: cfgd,
	}
	logger := logging.Must(log.DebugLevel).WithName("Test logger")
	client := calendar.NewClient(conf, nil, 0, logger)
	for _, test := range testCases {
		c, err := client.GetDays(test.day, 0)
		assert.NoError(t, err)
		assert.Equal(t, test.expected, isHoliday(c))
	}
}

func TestIsExpired(t *testing.T) {
	a := App{}
	logger := logging.Must(log.DebugLevel).WithName("Test logger")
	a.logger = logger
	r := models.Rule{}
	almanach := &calendar.Calendar{
		Holidays: []calendar.Day{},
		Err: &calendar.CalendarError{
			Name:    "",
			Message: "",
		},
	}

	almanach.Holidays = []calendar.Day{
		{
			Date: calendar.DateTime{Time: time.Date(2022, 1, 1, 0, 0, 0, 0, time.Local)},
			Type: calendar.Weekend,
		},
		{
			Date: calendar.DateTime{Time: time.Date(2022, 1, 2, 0, 0, 0, 0, time.Local)},
			Type: calendar.Weekend,
		},
		{
			Date: calendar.DateTime{Time: time.Date(2022, 1, 3, 0, 0, 0, 0, time.Local)},
			Type: calendar.Weekday,
		},
		{
			Date: calendar.DateTime{Time: time.Date(2022, 1, 4, 0, 0, 0, 0, time.Local)},
			Type: calendar.Weekend,
		},
		{
			Date: calendar.DateTime{Time: time.Date(2022, 1, 5, 0, 0, 0, 0, time.Local)},
			Type: calendar.Weekday,
		},
		{
			Date: calendar.DateTime{Time: time.Date(2022, 1, 6, 0, 0, 0, 0, time.Local)},
			Type: calendar.Weekend,
		},
	}

	// Until == nil test
	assert.Nil(t, a.getExpectedUntil(almanach, &r))

	// Before calendar.Holidays[0] test
	tm := time.Date(2021, 12, 31, 0, 0, 0, 0, time.Local)
	r.Until = &tm
	assert.Equal(t, tm, *a.getExpectedUntil(almanach, &r))

	// Dynamic rule test
	tm = time.Date(2022, 1, 1, 0, 0, 0, 0, time.Local)
	r.System = models.RuleSystemCAuth
	assert.Equal(t, tm, *a.getExpectedUntil(almanach, &r))

	// Static rule weekday test
	tm = time.Date(2022, 1, 3, 0, 0, 0, 0, time.Local)
	r.System = models.RuleSystemBigPuncher
	assert.Equal(t, tm.Add(12*time.Hour), *a.getExpectedUntil(almanach, &r))

	// Static rule weekend rule test (expiration date passed during last 2 weeks)
	tm = time.Date(2022, 1, 2, 0, 0, 0, 0, time.Local)
	assert.Equal(t, time.Date(2022, 1, 3, 12, 0, 0, 0, time.Local), *a.getExpectedUntil(almanach, &r))

	// Static rule weekend rule test (expiration date passed during last weekends)
	tm = time.Date(2022, 1, 6, 0, 0, 0, 0, time.Local)
	assert.Nil(t, a.getExpectedUntil(almanach, &r))

	almanach.Holidays = []calendar.Day{
		{
			Date: calendar.DateTime{Time: time.Date(2022, 1, 1, 0, 0, 0, 0, time.Local)},
			Type: calendar.Weekend,
		},
		{
			Date: calendar.DateTime{Time: time.Date(2022, 1, 2, 0, 0, 0, 0, time.Local)},
			Type: calendar.Weekend,
		},
		{
			Date: calendar.DateTime{Time: time.Date(2022, 1, 3, 0, 0, 0, 0, time.Local)},
			Type: calendar.Weekday,
		},
		{
			Date: calendar.DateTime{Time: time.Date(2022, 1, 4, 0, 0, 0, 0, time.Local)},
			Type: calendar.Weekend,
		},
		{
			Date: calendar.DateTime{Time: time.Date(2022, 1, 5, 0, 0, 0, 0, time.Local)},
			Type: calendar.Weekday,
		},
	}

	tm = time.Date(2022, 1, 5, 0, 0, 0, 0, time.Local)
	assert.Equal(t, time.Date(2022, 1, 5, 12, 0, 0, 0, time.Local), *a.getExpectedUntil(almanach, &r))

	tm = time.Date(2022, 1, 4, 0, 0, 0, 0, time.Local)
	assert.Equal(t, time.Date(2022, 1, 5, 12, 0, 0, 0, time.Local), *a.getExpectedUntil(almanach, &r))
}
