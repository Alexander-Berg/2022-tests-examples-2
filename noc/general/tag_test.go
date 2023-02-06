package racktables

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/valyala/fastjson"
)

func TestTagUnmarshal(t *testing.T) {
	j, err := fastjson.Parse(`
	{
		"id": "1627",
		"parent_id": "815",
		"is_assignable": "yes",
		"tag": "Switchdev",
		"color": "FF00FF",
		"description": null,
		"trace": [
			"285",
			"862",
			"815"
		]
	}
	`)
	assert.NoError(t, err, "Failed to parse testcase json")
	entries, err := tagUnmarshal(j)
	assert.NoError(t, err, "Failed to unmarshall testcase json %v", err)
	assert.Equal(t, Tag{
		ID:           1627,
		ParentID:     815,
		IsAssignable: "yes",
		Tag:          "Switchdev",
		Color:        "FF00FF",
		Description:  "",
		Trace:        []int{285, 862, 815},
	}, entries)
}
