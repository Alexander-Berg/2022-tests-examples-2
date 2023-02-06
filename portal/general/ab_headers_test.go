package experiments

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/valyala/fastjson"
)

func TestRawDataABClient(t *testing.T) {
	inputJSON := `{
		"flag_A": {
			"value": "1"
		},
		"flag_B": {
			"value": "some_text"
		},
		"flag_D": {
			"value": "yes"
		},
		"flag_E": {
			"some_other_value": "1"
		},
		"flag_F": [
			"value"
		]
	}`

	parser := fastjson.Parser{}
	jsonObj, err := parser.Parse(inputJSON)
	if err != nil {
		t.Fatalf("%v", err)
	}

	client := CreateRawDataABFlagsClient(jsonObj.GetObject())

	assert := assert.New(t)

	assert.Equal(client.Has("flag_A"), true)
	assert.Equal(client.Has("flag_B"), true)
	assert.Equal(client.Has("flag_C"), false)
	assert.Equal(client.Has("flag_D"), true)
	assert.Equal(client.Has("flag_E"), false)
	assert.Equal(client.Has("flag_F"), false)

	assert.Equal(client.Get("flag_A"), "1")
	assert.Equal(client.Get("flag_B"), "some_text")
	assert.Equal(client.Get("flag_C"), "")
	assert.Equal(client.Get("flag_D"), "yes")
	assert.Equal(client.Get("flag_E"), "")
	assert.Equal(client.Get("flag_F"), "")
}
