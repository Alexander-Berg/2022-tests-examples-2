package uaasproxy

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestIsIPAddress(t *testing.T) {
	assert.Equal(t, true, isIPAddress("127.0.0.1"))
	assert.Equal(t, true, isIPAddress("2a02:6b8:c02:f1d:8000:611:0:f001"))
	assert.Equal(t, false, isIPAddress("not ip address"))
}

var atoiTable = []struct {
	name      string
	input     []string
	output    []int
	shouldErr bool
}{
	{
		"ok",
		[]string{"1", "2", "3"},
		[]int{1, 2, 3},
		false,
	},
	{
		"ok with trim",
		[]string{" 1 ", "  2  ", "   3   "},
		[]int{1, 2, 3},
		false,
	},
	{
		"err",
		[]string{"hello", "darkness", "my old friend"},
		[]int{},
		true,
	},
}

func TestArrayAtoI(t *testing.T) {
	for _, tt := range atoiTable {
		t.Run(
			tt.name,
			func(t *testing.T) {
				out, err := arrayAtoI(tt.input)
				if !tt.shouldErr {
					assert.NoError(t, err)
					assert.Equal(t, tt.output, out)
				} else {
					assert.Error(t, err)
				}
			},
		)
	}
}
