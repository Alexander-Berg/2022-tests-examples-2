package time

import (
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
)

func Test_format(t *testing.T) {
	moscowLocation, err := time.LoadLocation("Europe/Moscow")
	if err != nil {
		panic(err)
	}
	testCases := []struct {
		timestamp      Time
		yyyymmdd       string
		yyyymmddhhmmss string
		hhmm           string
		iso            string
	}{
		{
			timestamp:      time.Date(2022, 02, 11, 15, 34, 12, 0, moscowLocation),
			yyyymmdd:       "20220211",
			yyyymmddhhmmss: "20220211153412",
			hhmm:           "1534",
			iso:            "2022-02-11T15:34:12",
		},
	}

	for _, testCase := range testCases {
		t.Run(testCase.timestamp.String(), func(t *testing.T) {
			assert.Equal(t, testCase.yyyymmdd, AsYYYYMMDD(testCase.timestamp))
			assert.Equal(t, testCase.yyyymmddhhmmss, AsYYYYMMDDHHMMSS(testCase.timestamp))
			assert.Equal(t, testCase.hhmm, AsHHMM(testCase.timestamp))
			assert.Equal(t, testCase.iso, AsISO(testCase.timestamp))
		})
	}
}
