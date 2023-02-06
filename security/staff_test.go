package staffapi

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestChooseSecurePhone(t *testing.T) {
	cases := []struct {
		phones       []Phone
		secureNumber string
		err          bool
	}{
		{
			err:          true,
			secureNumber: "empty",
		},
		{
			phones: []Phone{
				{
					Number: "911",
				},
				{
					Number: "912",
				},
			},
			err:          true,
			secureNumber: "no_eds_main",
		},
		{
			phones: []Phone{
				{
					Number: "eds-911",
					IsEDS:  true,
				},
				{
					Number: "912",
				},
			},
			secureNumber: "eds-911",
		},
		{
			phones: []Phone{
				{
					Number: "911",
				},
				{
					Number: "eds-912",
					IsEDS:  true,
				},
			},
			secureNumber: "eds-912",
		},
		{
			phones: []Phone{
				{
					Number: "main-911",
					IsMain: true,
				},
				{
					Number: "912",
				},
			},
			secureNumber: "main-911",
		},
		{
			phones: []Phone{
				{
					Number: "911",
				},
				{
					Number: "main-912",
					IsMain: true,
				},
			},
			secureNumber: "main-912",
		},
		{
			phones: []Phone{
				{
					Number: "911",
					IsMain: true,
				},
				{
					Number: "eds-stronger-912",
					IsEDS:  true,
				},
			},
			secureNumber: "eds-stronger-912",
		},
		{
			phones: []Phone{
				{
					Number: "911",
					IsEDS:  true,
				},
				{
					Number: "main-eds-stronger-912",
					IsEDS:  true,
					IsMain: true,
				},
			},
			secureNumber: "main-eds-stronger-912",
		},
		{
			phones: []Phone{
				{
					Number: "main-eds-stronger-911-2",
					IsEDS:  true,
					IsMain: true,
				},
				{
					Number: "912",
					IsEDS:  true,
				},
			},
			secureNumber: "main-eds-stronger-911-2",
		},
	}

	for _, tc := range cases {
		t.Run(tc.secureNumber, func(t *testing.T) {
			secureNumber, err := chooseSecurePhone(tc.phones...)
			if tc.err {
				require.Error(t, err)
				return
			}

			require.Equal(t, tc.secureNumber, secureNumber)
		})
	}
}
