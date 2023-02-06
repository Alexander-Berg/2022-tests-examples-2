package topnews

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestParse(t *testing.T) {
	type testCase struct {
		name    string
		data    string
		regions map[int]struct{}
	}

	testCases := []testCase{
		{
			name: "some regions",
			data: `{
			"regions": {
				"1": {},
				"2": {},
				"3": {}
			}
		}`,
			regions: map[int]struct{}{
				1: struct{}{},
				2: struct{}{},
				3: struct{}{},
			},
		},
	}

	for _, testCase := range testCases {
		t.Run(testCase.name, func(t *testing.T) {
			_, regions, err := (*newsdata).parse(nil, []byte(testCase.data))
			require.NoError(t, err)
			assert.Equal(t, testCase.regions, regions)
		})
	}
}
