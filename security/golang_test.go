package vulnparser

import (
	"fmt"
	"testing"

	"github.com/stretchr/testify/require"
)

func TestFixupGoRanges(t *testing.T) {
	cases := []struct {
		ranges   []string
		expected []string
	}{
		{
			ranges:   []string{">=1.1.1 <2.2.2"},
			expected: []string{">=1.1.1 <2.2.2"},
		},
		{
			ranges:   []string{""},
			expected: []string{},
		},
		{
			ranges:   []string{},
			expected: []string{},
		},
		{
			ranges:   []string{">=1.1.1 <2.2.2", "", "=3.0.0"},
			expected: []string{">=1.1.1 <2.2.2", "=3.0.0"},
		},
	}

	for _, tc := range cases {
		t.Run(fmt.Sprint(tc.ranges), func(t *testing.T) {
			actual := fixupGoRanges(tc.ranges)
			require.Equal(t, tc.expected, actual)
		})
	}
}

func TestParseGoRanges(t *testing.T) {
	cases := []struct {
		ranges   []string
		expected []goVerRange
		err      bool
	}{
		{
			ranges: []string{
				"f26b47038908e6b88193ed27055acb38b4c65995",
			},
			expected: []goVerRange{
				{
					{
						Comparator: "",
						Hash:       "f26b47038908e6b88193ed27055acb38b4c65995",
					},
				},
			},
			err: false,
		},
		{
			ranges: []string{
				"<f26b47038908e6b88193ed27055acb38b4c65995",
			},
			expected: []goVerRange{
				{
					{
						Comparator: "<",
						Hash:       "f26b47038908e6b88193ed27055acb38b4c65995",
					},
				},
			},
			err: false,
		},
		{
			ranges: []string{
				"<f26b47038908e6b88193ed27055acb38b4c65995",
				"=ca0518420b931db0923c97ec17e05e150a729a64",
			},
			expected: []goVerRange{
				{
					{
						Comparator: "<",
						Hash:       "f26b47038908e6b88193ed27055acb38b4c65995",
					},
				},
				{
					{
						Comparator: "=",
						Hash:       "ca0518420b931db0923c97ec17e05e150a729a64",
					},
				},
			},
			err: false,
		},
		{
			ranges: []string{
				">=c81e4f87c20a717b1dc52b2b77780fa789e19148 <ca0518420b931db0923c97ec17e05e150a729a64",
			},
			expected: []goVerRange{
				{
					{
						Comparator: ">=",
						Hash:       "c81e4f87c20a717b1dc52b2b77780fa789e19148",
					},
					{
						Comparator: "<",
						Hash:       "ca0518420b931db0923c97ec17e05e150a729a64",
					},
				},
			},
			err: false,
		},
		{
			ranges: []string{
				">=v1.0.1-r1 <ca0518420b931db0923c97ec17e05e150a729a64",
			},
			expected: []goVerRange{
				{
					{
						Comparator: ">=",
						Hash:       "1.0.1-r1",
					},
					{
						Comparator: "<",
						Hash:       "ca0518420b931db0923c97ec17e05e150a729a64",
					},
				},
			},
			err: false,
		},
		{
			ranges: []string{
				">=c81e4f87c20a717b1dc52b2b77780fa789e19148 <ca0518420b931db0923c97ec17e05e150a729a64",
				"<f26b47038908e6b88193ed27055acb38b4c65995",
			},
			expected: []goVerRange{
				{
					{
						Comparator: ">=",
						Hash:       "c81e4f87c20a717b1dc52b2b77780fa789e19148",
					},
					{
						Comparator: "<",
						Hash:       "ca0518420b931db0923c97ec17e05e150a729a64",
					},
				},
				{
					{
						Comparator: "<",
						Hash:       "f26b47038908e6b88193ed27055acb38b4c65995",
					},
				},
			},
			err: false,
		},
		{
			ranges: []string{
				">=c81e4f87c20a717b1dc52b2b77780fa789e19148 <ca0518420b931db0923c97ec17e05e150a729a64 >=6597fdb40134965e26f715854dc85f5e6cfaa6df <e16012435f82afafdfdd7963e95d86c9e8538322",
			},
			expected: []goVerRange{
				{
					{
						Comparator: ">=",
						Hash:       "c81e4f87c20a717b1dc52b2b77780fa789e19148",
					},
					{
						Comparator: "<",
						Hash:       "ca0518420b931db0923c97ec17e05e150a729a64",
					},
				},
				{
					{
						Comparator: ">=",
						Hash:       "6597fdb40134965e26f715854dc85f5e6cfaa6df",
					},
					{
						Comparator: "<",
						Hash:       "e16012435f82afafdfdd7963e95d86c9e8538322",
					},
				},
			},
			err: false,
		},
		{
			ranges: []string{
				">= c81e4f87c20a717b1dc52b2b77780fa789e19148 <ca0518420b931db0923c97ec17e05e150a729a64    >=6597fdb40134965e26f715854dc85f5e6cfaa6df <e16012435f82afafdfdd7963e95d86c9e8538322",
				"<f26b47038908e6b88193ed27055acb38b4c65995",
			},
			expected: []goVerRange{
				{
					{
						Comparator: ">=",
						Hash:       "c81e4f87c20a717b1dc52b2b77780fa789e19148",
					},
					{
						Comparator: "<",
						Hash:       "ca0518420b931db0923c97ec17e05e150a729a64",
					},
				},
				{
					{
						Comparator: ">=",
						Hash:       "6597fdb40134965e26f715854dc85f5e6cfaa6df",
					},
					{
						Comparator: "<",
						Hash:       "e16012435f82afafdfdd7963e95d86c9e8538322",
					},
				},
				{
					{
						Comparator: "<",
						Hash:       "f26b47038908e6b88193ed27055acb38b4c65995",
					},
				},
			},
			err: false,
		},
		{
			ranges: []string{
				"<f26b47038908e6b88193ed27055acb38b4c65995~",
			},
			expected: nil,
			err:      true,
		},
	}

	for _, tc := range cases {
		t.Run(fmt.Sprint(tc.ranges), func(t *testing.T) {
			actual, err := parseGoRanges(tc.ranges)
			if tc.err {
				require.Error(t, err)
				return
			}

			require.NoError(t, err)
			require.Equal(t, tc.expected, actual)
		})
	}
}
