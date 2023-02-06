package time

import (
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/libs/utils/common"
	"a.yandex-team.ru/portal/avocado/libs/utils/fs"
	"a.yandex-team.ru/portal/avocado/libs/utils/log3"
	"a.yandex-team.ru/portal/avocado/libs/utils/runtimeconfig/v2"
)

func TestHolidaysReader(t *testing.T) {
	fileInfo := fs.NewVirtualFileInfo("/opt/www/bases/madm/testing_ready/holidays.json", time.Now())
	fileContentsAsString := `{
   "225" : {
      "20201201" : [
         {
            "date" : "2020-12-01",
            "day-type" : "a",
            "geo" : "225",
            "holiday-name" : "b",
            "is-holiday" : "true",
            "is-transfer" : "false"
         }
      ]
   }
}`
	fileContents := []byte(fileContentsAsString)
	file := fs.NewVirtualFile(fileContents, fileInfo)
	vfs, err := fs.NewVirtualFileSystem(file)
	require.NoError(t, err)

	logger := log3.NewLoggerStub()

	fileWatcher, err := runtimeconfig.NewFileWatcher(vfs, logger, nil, nil)
	require.NoError(t, err)

	holidaysGetter, err := NewHolidaysGetter("", common.Development, log3.NewLoggerStub(), fileWatcher)
	require.NoError(t, err)

	holidaysGetter.WaitForInit()

	testCases := []struct {
		name string
		geos []int
		date holidayDate

		expectHoliday     bool
		expectHolidayInfo models.HolidayInfo
	}{
		{
			name: "complete miss",
			geos: []int{-1, -2, -3},
			date: "20201201",
		},
		{
			name: "from madm",
			geos: []int{225},
			date: "20201201",

			expectHoliday: true,
			expectHolidayInfo: models.HolidayInfo{
				Name:      "b",
				IsHoliday: true,
			},
		},
		{
			name: "from static data",
			geos: []int{149},
			date: "20211006",

			expectHoliday: true,
			expectHolidayInfo: models.HolidayInfo{
				Name:      "День архивиста Беларуси",
				IsHoliday: false,
			},
		},
	}

	for _, testCase := range testCases {
		t.Run(testCase.name, func(t *testing.T) {
			holiday, ok := holidaysGetter.GetHoliday(testCase.geos, testCase.date)

			assert.Equal(t, testCase.expectHoliday, ok)

			if testCase.expectHoliday {
				assert.Equal(t, testCase.expectHolidayInfo, holiday)
			}
		})
	}
}
