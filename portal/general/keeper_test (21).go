package time

import (
	"net/url"
	"testing"
	"time"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/libs/utils/common"
	"a.yandex-team.ru/portal/avocado/libs/utils/log3"
	"a.yandex-team.ru/portal/avocado/proto/morda_data"
)

func Test_keeper_initTimestamps(t *testing.T) {
	moscowLocation, err := time.LoadLocation("Europe/Moscow")
	require.NoError(t, err)
	referenceTime := time.Date(2022, 02, 11, 1, 2, 3, 4, moscowLocation)
	referenceTimestamp := referenceTime.UnixNano()

	testCases := []struct {
		name              string
		env               common.Environment
		isRequestInternal bool
		currentTime       Time
		cgi               url.Values
		shouldBeManual    bool
		expectTimestamp   int64
	}{
		{
			name:            "dev env without override",
			env:             common.Development,
			currentTime:     referenceTime,
			expectTimestamp: referenceTimestamp,
		},
		{
			name:        "timestamp override",
			env:         common.Development,
			currentTime: referenceTime,
			cgi: url.Values{
				"unixtime": []string{
					"12345",
				},
			},
			shouldBeManual:  true,
			expectTimestamp: time.Unix(12345, 0).UnixNano(),
		},
		{
			name:        "date override",
			env:         common.Development,
			currentTime: referenceTime,
			cgi: url.Values{
				"date": []string{
					"2222-03-10",
				},
			},
			shouldBeManual:  true,
			expectTimestamp: time.Date(2222, 03, 10, 1, 2, 3, 4, moscowLocation).UnixNano(),
		},
		{
			name:        "date override alt",
			env:         common.Development,
			currentTime: referenceTime,
			cgi: url.Values{
				"date": []string{
					"22220310",
				},
			},
			shouldBeManual:  true,
			expectTimestamp: time.Date(2222, 03, 10, 1, 2, 3, 4, moscowLocation).UnixNano(),
		},
		{
			name:        "time override",
			env:         common.Development,
			currentTime: referenceTime,
			cgi: url.Values{
				"time": []string{
					"22:22:22",
				},
			},
			shouldBeManual:  true,
			expectTimestamp: time.Date(2022, 02, 11, 22, 22, 22, 4, moscowLocation).UnixNano(),
		},
		{
			name:        "time override with no seconds",
			env:         common.Development,
			currentTime: referenceTime,
			cgi: url.Values{
				"time": []string{
					"22:22",
				},
			},
			shouldBeManual:  true,
			expectTimestamp: time.Date(2022, 02, 11, 22, 22, 3, 4, moscowLocation).UnixNano(),
		},
		{
			name:        "time override alt",
			env:         common.Development,
			currentTime: referenceTime,
			cgi: url.Values{
				"time": []string{
					"222222",
				},
			},
			shouldBeManual:  true,
			expectTimestamp: time.Date(2022, 02, 11, 22, 22, 22, 4, moscowLocation).UnixNano(),
		},
		{
			name:        "date and time override",
			env:         common.Development,
			currentTime: referenceTime,
			cgi: url.Values{
				"date": []string{
					"2222-03-10",
				},
				"time": []string{
					"22:22:22",
				},
			},
			shouldBeManual:  true,
			expectTimestamp: time.Date(2222, 03, 10, 22, 22, 22, 4, moscowLocation).UnixNano(),
		},
		{
			name:        "date and time and timestamp override (timestamp override overrides everything)",
			env:         common.Development,
			currentTime: referenceTime,
			cgi: url.Values{
				"unixtime": {
					"12345",
				},
				"date": []string{
					"2222-03-10",
				},
				"time": []string{
					"22:22:22",
				},
			},
			shouldBeManual:  true,
			expectTimestamp: time.Unix(12345, 0).UnixNano(),
		},
		{
			name:        "manual time in testing env",
			env:         common.Testing,
			currentTime: referenceTime,
			cgi: url.Values{
				"unixtime": {
					"12345",
				},
				"date": []string{
					"2222-03-10",
				},
				"time": []string{
					"22:22:22",
				},
			},
			shouldBeManual:  true,
			expectTimestamp: time.Unix(12345, 0).UnixNano(),
		},
		{
			name:              "manual time for internal request",
			env:               common.Production,
			isRequestInternal: true,
			currentTime:       referenceTime,
			cgi: url.Values{
				"unixtime": {
					"12345",
				},
				"date": []string{
					"2222-03-10",
				},
				"time": []string{
					"22:22:22",
				},
			},
			shouldBeManual:  true,
			expectTimestamp: time.Unix(12345, 0).UnixNano(),
		},
		{
			name:        "(no) manual time for non-internal request in production env",
			env:         common.Production,
			currentTime: referenceTime,
			cgi: url.Values{
				"unixtime": {
					"12345",
				},
				"date": []string{
					"2222-03-10",
				},
				"time": []string{
					"22:22:22",
				},
			},
			shouldBeManual:  false,
			expectTimestamp: referenceTimestamp,
		},
	}

	for _, testCase := range testCases {
		t.Run(testCase.name, func(t *testing.T) {
			ctl := gomock.NewController(t)
			requestGetter := NewMockrequestGetter(ctl)
			requestGetter.EXPECT().GetRequest().Return(models.Request{
				CGI:        testCase.cgi,
				IsInternal: testCase.isRequestInternal,
			}).AnyTimes()
			geoGetter := NewMockgeoGetter(ctl)
			geoGetter.EXPECT().GetGeo().Return(models.Geo{
				TimeZone: &models.TimeZone{
					Offset: time.Hour * 3,
					Name:   "Europe/Moscow",
				},
			}).AnyTimes()
			timeProvider := NewMockTimeProvider(ctl)
			timeProvider.EXPECT().GetCurrentTime().Return(testCase.currentTime).AnyTimes()
			timeProvider.EXPECT().GetMoscowLocation().Return(moscowLocation).AnyTimes()
			holidaysGetter := NewMockHolidaysGetter(ctl)
			holidaysGetter.EXPECT().GetHoliday(gomock.Any(), gomock.Any()).Return(models.HolidayInfo{}, false).AnyTimes()

			keeper := NewKeeper(nil, log3.NewLoggerStub(), requestGetter, geoGetter, timeProvider, holidaysGetter, testCase.env)

			keeper.Init()

			cache := keeper.cache

			require.NotNil(t, cache)

			assert.Equal(t, testCase.currentTime.UnixNano(), cache.RealTimestamp)
			assert.Equal(t, testCase.shouldBeManual, cache.IsManual)
			assert.Equal(t, testCase.expectTimestamp, cache.Timestamp)
		})
	}
}

func Test_keeper_initHolidays(t *testing.T) {
	moscowLocation, err := time.LoadLocation("Europe/Moscow")
	require.NoError(t, err)

	referenceHolidays := holidaysByGeoByDate{
		1: holidaysByDate{
			"20220101": []models.HolidayInfo{
				{
					Name:      "a1",
					IsHoliday: true,
				},
			},
			"20220102": []models.HolidayInfo{
				{
					Name:      "b1",
					IsHoliday: false,
				},
			},
			"20220104": []models.HolidayInfo{
				{
					Name:      "d1",
					IsHoliday: true,
				},
			},
		},
		2: holidaysByDate{
			"20220101": []models.HolidayInfo{
				{
					Name:      "a2",
					IsHoliday: true,
				},
			},
			"20220102": []models.HolidayInfo{
				{
					Name:      "b2",
					IsHoliday: true,
				},
			},
			"20220103": []models.HolidayInfo{
				{
					Name:      "c2",
					IsHoliday: true,
				},
			},
			"20220104": []models.HolidayInfo{
				{
					Name:      "d2",
					IsHoliday: true,
				},
			},
			"20220105": []models.HolidayInfo{
				{
					Name:      "e2",
					IsHoliday: true,
				},
			},
		},
	}

	testCases := []struct {
		name                   string
		currentTime            Time
		localTimeZoneOffset    time.Duration
		geoAndParents          []uint32
		holidays               holidaysByGeoByDate
		expectHolidayInfo      models.HolidayInfo
		expectHolidayYesterday bool
		expectHolidayToday     bool
		expectHolidayTomorrow  bool
	}{
		{
			name:                "single geo",
			currentTime:         time.Date(2022, 01, 02, 12, 0, 0, 0, time.UTC),
			localTimeZoneOffset: time.Hour * 3,
			geoAndParents:       []uint32{1},
			holidays:            referenceHolidays,
			expectHolidayInfo: models.HolidayInfo{
				Name:      "b1",
				IsHoliday: false,
			},
			expectHolidayYesterday: true,
			expectHolidayToday:     false,
			expectHolidayTomorrow:  false,
		},
		{
			name:                   "next day but before next day",
			currentTime:            time.Date(2022, 01, 03, 1, 0, 0, 0, time.UTC),
			localTimeZoneOffset:    time.Hour * 1,
			geoAndParents:          []uint32{1},
			holidays:               referenceHolidays,
			expectHolidayInfo:      models.HolidayInfo{},
			expectHolidayYesterday: true,
			expectHolidayToday:     false,
			expectHolidayTomorrow:  false,
		},
		{
			name:                   "utc today but local tomorrow",
			currentTime:            time.Date(2022, 01, 02, 23, 0, 0, 0, time.UTC),
			localTimeZoneOffset:    time.Hour * 5,
			geoAndParents:          []uint32{1},
			holidays:               referenceHolidays,
			expectHolidayInfo:      models.HolidayInfo{},
			expectHolidayYesterday: false,
			expectHolidayToday:     false,
			expectHolidayTomorrow:  true,
		},
		{
			name:                "utc today but local tomorrow with two geos",
			currentTime:         time.Date(2022, 01, 02, 23, 0, 0, 0, time.UTC),
			localTimeZoneOffset: time.Hour * 5,
			geoAndParents:       []uint32{1, 2},
			holidays:            referenceHolidays,
			expectHolidayInfo: models.HolidayInfo{
				Name:      "c2",
				IsHoliday: true,
			},
			expectHolidayYesterday: false,
			expectHolidayToday:     true,
			expectHolidayTomorrow:  true,
		},
		{
			name:                "next day but before next day with two geos",
			currentTime:         time.Date(2022, 01, 03, 1, 0, 0, 0, time.UTC),
			localTimeZoneOffset: time.Hour * 1,
			geoAndParents:       []uint32{1, 2},
			holidays:            referenceHolidays,
			expectHolidayInfo: models.HolidayInfo{
				Name:      "c2",
				IsHoliday: true,
			},
			expectHolidayYesterday: true,
			expectHolidayToday:     false,
			expectHolidayTomorrow:  true,
		},
	}

	for _, testCase := range testCases {
		t.Run(testCase.name, func(t *testing.T) {
			ctl := gomock.NewController(t)
			requestGetter := NewMockrequestGetter(ctl)
			requestGetter.EXPECT().GetRequest().Return(models.Request{}).AnyTimes()
			geoGetter := NewMockgeoGetter(ctl)
			geoGetter.EXPECT().GetGeo().Return(models.Geo{
				Parents: testCase.geoAndParents,
				TimeZone: &models.TimeZone{
					Offset: testCase.localTimeZoneOffset,
					Name:   "forced zone",
				},
			}).AnyTimes()
			timeProvider := NewMockTimeProvider(ctl)
			timeProvider.EXPECT().GetCurrentTime().Return(testCase.currentTime).AnyTimes()
			timeProvider.EXPECT().GetMoscowLocation().Return(moscowLocation).AnyTimes()
			holidaysGetterMock := NewMockHolidaysGetter(ctl)
			holidaysGetterMock.EXPECT().GetHoliday(gomock.Any(), gomock.Any()).DoAndReturn(
				func(geos []int, date holidayDate) (models.HolidayInfo, bool) {
					return (*holidaysGetter).getHoliday(nil, geos, date, testCase.holidays)
				}).AnyTimes()

			keeper := NewKeeper(nil, log3.NewLoggerStub(), requestGetter, geoGetter, timeProvider, holidaysGetterMock, common.Development)

			keeper.Init()

			cache := keeper.cache

			require.NotNil(t, cache)

			assert.Equal(t, &morda_data.Time_HolidayInfo{
				HolidayName: testCase.expectHolidayInfo.Name,
				IsHoliday:   testCase.expectHolidayInfo.IsHoliday,
			}, cache.HolidayInfo)

			assert.Equal(t, &morda_data.Time_HolidaysYTT{
				Yesterday: testCase.expectHolidayYesterday,
				Today:     testCase.expectHolidayToday,
				Tomorrow:  testCase.expectHolidayTomorrow,
			}, cache.HolidaysYTT)

		})
	}
}

func Test_keeper_makeUserLocation(t *testing.T) {
	testCases := []struct {
		name               string
		timeZoneName       string
		expectTimeZoneName string
	}{
		{
			name:               "valid zone",
			timeZoneName:       "Europe/Moscow",
			expectTimeZoneName: "Europe/Moscow",
		},
		{
			name:               "invalid zone",
			timeZoneName:       "Europe/Moscowasdasd",
			expectTimeZoneName: "Europe/Moscowasdasd*",
		},
		{
			name:               "invalid zone alt",
			timeZoneName:       "UTC+01",
			expectTimeZoneName: "UTC+01*",
		},
		{
			name:               "invalid zone alt2",
			timeZoneName:       "UTC-01",
			expectTimeZoneName: "UTC-01*",
		},
	}

	for _, testCase := range testCases {
		t.Run(testCase.name, func(t *testing.T) {
			ctl := gomock.NewController(t)
			requestGetter := NewMockrequestGetter(ctl)
			geoGetter := NewMockgeoGetter(ctl)
			geoGetter.EXPECT().GetGeo().Return(models.Geo{
				TimeZone: &models.TimeZone{
					Offset: 3 * time.Hour,
					Name:   testCase.timeZoneName,
				},
			})
			timeProvider := NewMockTimeProvider(ctl)
			holidaysGetter := NewMockHolidaysGetter(ctl)
			holidaysGetter.EXPECT().GetHoliday(gomock.Any(), gomock.Any()).Return(models.HolidayInfo{}, false).AnyTimes()

			keeper := NewKeeper(nil, log3.NewLoggerStub(), requestGetter, geoGetter, timeProvider, holidaysGetter, common.Development)
			keeper.makeUserLocation()

			assert.Equal(t, testCase.expectTimeZoneName, keeper.userLocation.String())
		})
	}

}
