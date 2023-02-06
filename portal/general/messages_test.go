package errors

import (
	"fmt"
	"testing"

	"github.com/stretchr/testify/assert"
)

func Test_messages_wrap(t *testing.T) {
	testCases := []struct {
		name             string
		msgs             *messages
		wrapper          string
		expectedRaw      string
		expectedTemplate string
		expectedData     data
	}{
		{
			name:        "basic",
			msgs:        newMessages(fmt.Errorf("wrapped")),
			wrapper:     "wrapper",
			expectedRaw: "wrapper: wrapped",
		},
		{
			name:             "with data",
			msgs:             mPrintf("%s %s", "some", NewToken("data", "value")),
			wrapper:          "wrapper",
			expectedRaw:      "wrapper: some value",
			expectedTemplate: "wrapper: some [data]",
			expectedData: data{
				"data": []interface{}{"value"},
			},
		},
		{
			name:             "merged",
			msgs:             mPrintf("the %s", NewToken("num", "first")).join(mPrintf("the %s", NewToken("num", "second"))),
			wrapper:          "wrapper",
			expectedRaw:      "collapsed errors:\n\twrapper: the first\n\twrapper: the second",
			expectedTemplate: "collapsed errors: wrapper: the [num]",
			expectedData: data{
				"num": []interface{}{"first", "second"},
			},
		},
	}
	for _, testCase := range testCases {
		if testCase.expectedTemplate == "" {
			testCase.expectedTemplate = testCase.expectedRaw
		}
		if testCase.expectedData == nil {
			testCase.expectedData = make(data)
		}
		t.Run(testCase.name, func(t *testing.T) {
			wrapped := testCase.msgs.wrap(testCase.wrapper)
			raw := wrapped.mergeRaw()
			template, data := wrapped.mergeTemplates()
			assert.Equal(t, testCase.expectedRaw, raw)
			assert.Equal(t, testCase.expectedTemplate, template)
			assert.Equal(t, testCase.expectedData, data)
		})
	}
}

func Test_messages_join(t *testing.T) {
	testCases := []struct {
		name             string
		msgs             []*messages
		expectedRaw      string
		expectedTemplate string
		expectedData     data
	}{
		{
			name: "different templates, no data",
			msgs: []*messages{
				newMessages(fmt.Errorf("first")),
				newMessages(fmt.Errorf("second")),
			},
			expectedRaw: "collapsed errors:\n\tfirst\n\tsecond",
		},
		{
			name: "same templates, no data",
			msgs: []*messages{
				newMessages(fmt.Errorf("first")),
				newMessages(fmt.Errorf("first")),
			},
			expectedRaw:      "collapsed errors:\n\tfirst\n\tfirst",
			expectedTemplate: "collapsed errors: first",
		},
		{
			name: "same templates, with data",
			msgs: []*messages{
				mPrintf("the %s", NewToken("num", "first")),
				mPrintf("the %s", NewToken("num", "second")),
			},
			expectedRaw:      "collapsed errors:\n\tthe first\n\tthe second",
			expectedTemplate: "collapsed errors: the [num]",
			expectedData: data{
				"num": []interface{}{"first", "second"},
			},
		},
		{
			name: "different templates, with data",
			msgs: []*messages{
				mPrintf("the %s", NewToken("num", "first")),
				mPrintf("the other %s and %s", NewToken("num", "second"), NewToken("str", "third")),
			},
			expectedRaw:      "collapsed errors:\n\tthe first\n\tthe other second and third",
			expectedTemplate: "collapsed errors:\n\tthe [num]\n\tthe other [num@] and [str]",
			expectedData: data{
				"num":  []interface{}{"first"},
				"num@": []interface{}{"second"},
				"str":  []interface{}{"third"},
			},
		},
		{
			name: "different+same templates, with data",
			msgs: []*messages{
				mPrintf("first %s", NewToken("num", "first")),
				mPrintf("second %s", NewToken("num", "second")),
				mPrintf("second %s", NewToken("num", "third")),
			},
			expectedRaw:      "collapsed errors:\n\tfirst first\n\tsecond second\n\tsecond third",
			expectedTemplate: "collapsed errors:\n\tfirst [num]\n\tsecond [num@]",
			expectedData: data{
				"num":  []interface{}{"first"},
				"num@": []interface{}{"second", "third"},
			},
		},
		{
			name: "with joined",
			msgs: []*messages{
				mPrintf("the %s", NewToken("num", "first")),
				mPrintf("the %s", NewToken("num", "second")).join(mPrintf("the %s", NewToken("num", "third"))),
			},
			expectedRaw:      "collapsed errors:\n\tthe first\n\tthe second\n\tthe third",
			expectedTemplate: "collapsed errors: the [num]",
			expectedData: data{
				"num": []interface{}{"first", "second", "third"},
			},
		},
	}
	for _, testCase := range testCases {
		if testCase.expectedTemplate == "" {
			testCase.expectedTemplate = testCase.expectedRaw
		}
		if testCase.expectedData == nil {
			testCase.expectedData = make(data)
		}
		t.Run(testCase.name, func(t *testing.T) {
			joined := testCase.msgs[0]
			for _, other := range testCase.msgs[1:] {
				joined = joined.join(other)
			}
			raw := joined.mergeRaw()
			template, data := joined.mergeTemplates()
			assert.Equal(t, testCase.expectedRaw, raw)
			assert.Equal(t, testCase.expectedTemplate, template)
			assert.Equal(t, testCase.expectedData, data)
		})
	}
}
