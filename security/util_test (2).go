package util

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestSplitAndAddValuesCorrectValues(t *testing.T) {
	data := map[string]interface{}{}
	SplitAndAddValues("alpha:1,bravo:well done,charlie:chaplin", ",", ":", data, "extra", "")
	require.Equal(t, map[string]interface{}{
		"alpha":   "1",
		"bravo":   "well done",
		"charlie": "chaplin",
	}, data)
}

func TestSplitAndAddValuesNonKeyValues(t *testing.T) {
	data := map[string]interface{}{}
	SplitAndAddValues("one=1;two=22;hello world;three=333;hi there", ";", "=", data, "extra", "prefix-")
	require.Equal(t, map[string]interface{}{
		"prefix-one":   "1",
		"prefix-two":   "22",
		"prefix-three": "333",
		"extra":        "hello world;hi there",
	}, data)
}
