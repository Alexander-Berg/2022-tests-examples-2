package startrek

import (
	"encoding/json"
	"fmt"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestMarshalUpdateIssueParameters(t *testing.T) {
	cases := []struct {
		params   []IssueParameter
		expected string
	}{
		{nil, "{}"},
		{[]IssueParameter{WithSummary("text")}, `{"summary":"text"}`},
		{[]IssueParameter{WithDescription("text")}, `{"description":"text"}`},

		{[]IssueParameter{WithStatus(nil)}, `{"status":null}`},
		{[]IssueParameter{WithStatus(&Entity{Key: "status"})}, `{"status":"status"}`},

		{[]IssueParameter{WithType(nil)}, `{"type":null}`},
		{[]IssueParameter{WithType(&Entity{Key: "type"})}, `{"type":"type"}`},

		{[]IssueParameter{WithPriority(nil)}, `{"priority":null}`},
		{[]IssueParameter{WithPriority(&Entity{Key: "priority"})}, `{"priority":"priority"}`},

		{[]IssueParameter{WithAuthor("author")}, `{"author":"author"}`},

		{[]IssueParameter{ClearAssignee()}, `{"assignee":null}`},
		{[]IssueParameter{WithAssignee("assignee")}, `{"assignee":"assignee"}`},

		{[]IssueParameter{WithFollowers([]string{"followers"})}, `{"followers":["followers"]}`},

		{[]IssueParameter{WithDuty([]string{"duty"})}, `{"duty":["duty"]}`},

		{[]IssueParameter{WithTags([]string{"tag"})}, `{"tags":["tag"]}`},
		{[]IssueParameter{AddTags("tag1", "tag2")}, `{"tags":{"add":["tag1","tag2"]}}`},
		{[]IssueParameter{RemoveTags("tag1")}, `{"tags":{"remove":["tag1"]}}`},
	}
	for idx, c := range cases {
		t.Run(fmt.Sprintf("case #%d", idx), func(t *testing.T) {
			payload := issueParameters{}
			for _, p := range c.params {
				p(payload)
			}
			data, err := json.Marshal(payload)
			assert.NoError(t, err)
			assert.Equal(t, c.expected, string(data))
		})
	}
}
