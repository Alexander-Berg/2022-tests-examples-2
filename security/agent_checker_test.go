package supervisor

import (
	"fmt"
	"testing"
	"time"

	"github.com/stretchr/testify/require"
)

func TestCheckCertExpire(t *testing.T) {
	cases := []struct {
		Now, ValidAfter, ValidBefore time.Time
		NotifyPeriod                 time.Duration
		Expired                      bool
	}{
		//short lived certs
		{
			Now:          time.Date(2021, 01, 01, 12, 0, 0, 0, time.UTC),
			ValidAfter:   time.Date(2021, 01, 01, 0, 0, 0, 0, time.UTC),
			ValidBefore:  time.Date(2021, 01, 02, 0, 0, 0, 0, time.UTC),
			NotifyPeriod: 0,
			Expired:      false,
		},
		{
			Now:          time.Date(2021, 01, 01, 21, 0, 0, 0, time.UTC),
			ValidAfter:   time.Date(2021, 01, 01, 0, 0, 0, 0, time.UTC),
			ValidBefore:  time.Date(2021, 01, 02, 0, 0, 0, 0, time.UTC),
			NotifyPeriod: time.Hour,
			Expired:      true,
		},
		{
			Now:          time.Date(2021, 01, 01, 23, 30, 0, 0, time.UTC),
			ValidAfter:   time.Date(2021, 01, 01, 0, 0, 0, 0, time.UTC),
			ValidBefore:  time.Date(2021, 01, 02, 0, 0, 0, 0, time.UTC),
			NotifyPeriod: 30 * time.Minute,
			Expired:      true,
		},

		//semi long-lived certs
		{
			Now:          time.Date(2021, 01, 02, 0, 0, 0, 0, time.UTC),
			ValidAfter:   time.Date(2021, 01, 01, 0, 0, 0, 0, time.UTC),
			ValidBefore:  time.Date(2021, 01, 07, 0, 0, 0, 0, time.UTC),
			NotifyPeriod: 0,
			Expired:      false,
		},
		{
			Now:          time.Date(2021, 01, 06, 1, 0, 0, 0, time.UTC),
			ValidAfter:   time.Date(2021, 01, 01, 0, 0, 0, 0, time.UTC),
			ValidBefore:  time.Date(2021, 01, 07, 0, 0, 0, 0, time.UTC),
			NotifyPeriod: time.Hour,
			Expired:      true,
		},
		{
			Now:          time.Date(2021, 01, 06, 20, 0, 0, 0, time.UTC),
			ValidAfter:   time.Date(2021, 01, 01, 0, 0, 0, 0, time.UTC),
			ValidBefore:  time.Date(2021, 01, 07, 0, 0, 0, 0, time.UTC),
			NotifyPeriod: 30 * time.Minute,
			Expired:      true,
		},

		// long-lived certs
		{
			Now:          time.Date(2021, 02, 15, 0, 0, 0, 0, time.UTC),
			ValidAfter:   time.Date(2021, 01, 01, 0, 0, 0, 0, time.UTC),
			ValidBefore:  time.Date(2021, 03, 01, 0, 0, 0, 0, time.UTC),
			NotifyPeriod: 0,
			Expired:      false,
		},
		{
			Now:          time.Date(2021, 02, 25, 5, 0, 0, 0, time.UTC),
			ValidAfter:   time.Date(2021, 01, 01, 0, 0, 0, 0, time.UTC),
			ValidBefore:  time.Date(2021, 03, 01, 0, 0, 0, 0, time.UTC),
			NotifyPeriod: 12 * time.Hour,
			Expired:      true,
		},
		{
			Now:          time.Date(2021, 02, 28, 5, 0, 0, 0, time.UTC),
			ValidAfter:   time.Date(2021, 01, 01, 0, 0, 0, 0, time.UTC),
			ValidBefore:  time.Date(2021, 03, 01, 0, 0, 0, 0, time.UTC),
			NotifyPeriod: time.Hour,
			Expired:      true,
		},
		{
			Now:          time.Date(2021, 02, 28, 20, 0, 0, 0, time.UTC),
			ValidAfter:   time.Date(2021, 01, 01, 0, 0, 0, 0, time.UTC),
			ValidBefore:  time.Date(2021, 03, 01, 0, 0, 0, 0, time.UTC),
			NotifyPeriod: 30 * time.Minute,
			Expired:      true,
		},
	}

	for i, tc := range cases {
		caseName := fmt.Sprintf("%d-%s-%s", i, tc.ValidBefore.Sub(tc.ValidAfter), tc.Now.Sub(tc.ValidAfter))
		t.Run(caseName, func(t *testing.T) {
			notifyPeriod, expired := checkCertExpire(tc.Now, tc.ValidAfter, tc.ValidBefore)
			require.Equal(t, tc.Expired, expired)
			require.Equal(t, tc.NotifyPeriod, notifyPeriod)
		})
	}
}
