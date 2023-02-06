package racktables

import (
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/valyala/fastjson"
)

func TestPnsLogUnmarshal(t *testing.T) {
	j, err := fastjson.Parse(`
	[
		{
			"id": "200258",
			"port_id": "874566",
			"object_id": "45539",
			"time": "1648456037",
			"type": "ошибка наливки",
			"text": "Catching shell promp\n"
		}
	]
	`)
	assert.NoError(t, err, "Failed to parse testcase json")
	entries, err := pnsLogUnmarshal(j)
	assert.NoError(t, err, "Failed to unmarshall testcase json %v", err)
	assert.Equal(t, []PnsLog{{
		ID:       200258,
		PortID:   874566,
		ObjectID: 45539,
		Time:     time.Unix(1648456037, 0),
		Type:     PnsLogType("ошибка наливки"),
		Text:     "Catching shell promp\n",
	}}, entries)
}
