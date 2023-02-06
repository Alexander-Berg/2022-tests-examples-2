package errors

import (
	"fmt"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func testRepresentation(t *testing.T, err error, expectedRaw, expectedTemplate string, expectedData data, expectedTags []string) {
	if expectedData == nil {
		expectedData = make(data)
	}
	if expectedTags == nil {
		expectedTags = make([]string, 0)
	}
	raw := err.Error()
	assert.Equal(t, expectedRaw, raw)
	errTemplated, ok := err.(errorTemplated)
	require.True(t, ok)
	template, data := errTemplated.GetTemplated()
	assert.Equal(t, expectedTemplate, template)
	assert.Equal(t, expectedData, data)
	errWithTags, ok := err.(errorWithTags)
	require.True(t, ok)
	assert.ElementsMatch(t, expectedTags, errWithTags.GetTags())
}

func TestError(t *testing.T) {
	testCases := []struct {
		msg string
	}{
		{"123"},
		{"%f %s %d"},
		{""},
	}
	for _, testCase := range testCases {
		err := Error(testCase.msg)
		testRepresentation(t, err, testCase.msg, testCase.msg, nil, nil)
	}
}

func TestErrorf(t *testing.T) {
	testCases := []struct {
		name             string
		format           string
		args             []interface{}
		expectedTemplate string
		expectedData     data
	}{
		{
			name:   "no format specifiers",
			format: "abcdef",
			args:   []interface{}{},
		},
		{
			name:   "format specifiers but no tokens",
			format: "%s %+05d %c",
			args:   []interface{}{"abc", 123, 'c'},
		},
		{
			name:             "with tokens",
			format:           "%4d %s %s",
			args:             []interface{}{NewToken("numeric", 123), "not token", NewToken("string", "abc")},
			expectedTemplate: "[numeric] not token [string]",
			expectedData: data{
				"numeric": []interface{}{123},
				"string":  []interface{}{"abc"},
			},
		},
		{
			name:             "with tokens (more than needed)",
			format:           "%s %s",
			args:             []interface{}{NewToken("a", "a"), NewToken("b", "b"), NewToken("c", "c")},
			expectedTemplate: "[a] [b]%!(EXTRA *errors.templateToken=[c])",
			expectedData: data{
				"a": []interface{}{"a"},
				"b": []interface{}{"b"},
				"c": []interface{}{"c"},
			},
		},
		{
			name:             "with tokens with name conflicts",
			format:           "%s %s",
			args:             []interface{}{NewToken("same name", 1), NewToken("same name", 2)},
			expectedTemplate: "[same name] [same name#]",
			expectedData: data{
				"same name":  []interface{}{1},
				"same name#": []interface{}{2},
			},
		},
	}
	for _, testCase := range testCases {
		expectedRaw := fmt.Sprintf(testCase.format, testCase.args...)
		if testCase.expectedTemplate == "" {
			testCase.expectedTemplate = expectedRaw
		}
		t.Run(testCase.name, func(t *testing.T) {
			err := Errorf(testCase.format, testCase.args...)
			testRepresentation(t, err, expectedRaw, testCase.expectedTemplate, testCase.expectedData, nil)
		})
	}
}

func TestWrap(t *testing.T) {
	testCases := []struct {
		name             string
		err              error
		wrapper          string
		expectedRaw      string
		expectedTemplate string
		expectedData     data
		expectedTags     []string
	}{
		{
			name:    "nil error",
			err:     nil,
			wrapper: "some wrapper",
		},
		{
			name:        "plain error",
			err:         fmt.Errorf("some error"),
			wrapper:     "some wrapper",
			expectedRaw: "some wrapper: some error",
		},
		{
			name:        "extra without any data",
			err:         Error("some error"),
			wrapper:     "some wrapper",
			expectedRaw: "some wrapper: some error",
		},
		{
			name:         "extra with tags",
			err:          WithAddedTags(Error("some error"), "a", "b"),
			wrapper:      "some wrapper",
			expectedRaw:  "some wrapper: some error",
			expectedTags: []string{"a", "b"},
		},
		{
			name:             "extra with some data",
			err:              Errorf("%s %d", NewToken("string", "abc"), NewToken("number", 123)),
			wrapper:          "some wrapper",
			expectedRaw:      "some wrapper: abc 123",
			expectedTemplate: "some wrapper: [string] [number]",
			expectedData: data{
				"string": []interface{}{"abc"},
				"number": []interface{}{123},
			},
		},
		{
			name:             "extra with some data, double wrapped",
			err:              Wrap(Errorf("%s %d", NewToken("string", "abc"), NewToken("number", 123)), "first"),
			wrapper:          "second",
			expectedRaw:      "second: first: abc 123",
			expectedTemplate: "second: first: [string] [number]",
			expectedData: data{
				"string": []interface{}{"abc"},
				"number": []interface{}{123},
			},
		},
	}
	for _, testCase := range testCases {
		if testCase.expectedTemplate == "" {
			testCase.expectedTemplate = testCase.expectedRaw
		}
		t.Run(testCase.name, func(t *testing.T) {
			wrapped := Wrap(testCase.err, testCase.wrapper)
			if testCase.err == nil {
				assert.NoError(t, wrapped)
				return
			}
			require.Error(t, wrapped)
			testRepresentation(t, wrapped, testCase.expectedRaw, testCase.expectedTemplate, testCase.expectedData, testCase.expectedTags)
		})
	}
}

func TestCollapse(t *testing.T) {
	testCases := []struct {
		name             string
		errs             []error
		expectedRaw      string
		expectedTemplate string
		expectedData     data
		expectedTags     []string
	}{
		{
			name: "nil errors",
			errs: nil,
		},
		{
			name:        "plain errors",
			errs:        []error{fmt.Errorf("some error"), fmt.Errorf("some other error")},
			expectedRaw: "collapsed errors:\n\tsome error\n\tsome other error",
		},
		{
			name:        "plain errors + nil errors",
			errs:        []error{fmt.Errorf("some error"), nil, fmt.Errorf("some other error"), nil},
			expectedRaw: "collapsed errors:\n\tsome error\n\tsome other error",
		},
		{
			name:        "extras without any data",
			errs:        []error{Error("some error"), Errorf("some %s error", "other")},
			expectedRaw: "collapsed errors:\n\tsome error\n\tsome other error",
		},
		{
			name:         "extras with tags",
			errs:         []error{WithAddedTags(Error("some error"), "a", "b"), WithAddedTags(Errorf("some %s error", "other"), "b", "c")},
			expectedRaw:  "collapsed errors:\n\tsome error\n\tsome other error",
			expectedTags: []string{"a", "b", "c"},
		},
		{
			name:             "extras with full data",
			errs:             []error{Errorf("some %s", NewToken("key1", "value1")), Errorf("some other %s", NewToken("key2", "value2"))},
			expectedRaw:      "collapsed errors:\n\tsome value1\n\tsome other value2",
			expectedTemplate: "collapsed errors:\n\tsome [key1]\n\tsome other [key2]",
			expectedData: data{
				"key1": []interface{}{"value1"},
				"key2": []interface{}{"value2"},
			},
		},
		{
			name:             "extras with partial data",
			errs:             []error{Errorf("error with %s", NewToken("key", "value")), Error("error without data")},
			expectedRaw:      "collapsed errors:\n\terror with value\n\terror without data",
			expectedTemplate: "collapsed errors:\n\terror with [key]\n\terror without data",
			expectedData: data{
				"key": []interface{}{"value"},
			},
		},
		{
			name:        "single error",
			errs:        []error{fmt.Errorf("some error")},
			expectedRaw: "some error",
		},
		{
			name:             "duplicate error with data",
			errs:             []error{Errorf("error %d", NewToken("errnum", 1)), Errorf("error %d", NewToken("errnum", 2))},
			expectedRaw:      "collapsed errors:\n\terror 1\n\terror 2",
			expectedTemplate: "collapsed errors: error [errnum]",
			expectedData: data{
				"errnum": []interface{}{1, 2},
			},
		},
		{
			name:             "duplicate error with data + unique error",
			errs:             []error{Errorf("error %d", NewToken("errnum", 1)), Errorf("error %d", NewToken("errnum", 2)), Errorf("different error %d", NewToken("errnum", 3))},
			expectedRaw:      "collapsed errors:\n\terror 1\n\terror 2\n\tdifferent error 3",
			expectedTemplate: "collapsed errors:\n\terror [errnum]\n\tdifferent error [errnum@]",
			expectedData: data{
				"errnum":  []interface{}{1, 2},
				"errnum@": []interface{}{3},
			},
		},
		{
			name:             "duplicate error with data + unique error; collapsed with duplicate unique error",
			errs:             []error{Collapse([]error{Errorf("error %d", NewToken("errnum", 1)), Errorf("error %d", NewToken("errnum", 2)), Errorf("different error %d", NewToken("errnum", 3))}), Errorf("different error %d", NewToken("errnum", 4))},
			expectedRaw:      "collapsed errors:\n\terror 1\n\terror 2\n\tdifferent error 3\n\tdifferent error 4",
			expectedTemplate: "collapsed errors:\n\terror [errnum]\n\tdifferent error [errnum@]",
			expectedData: data{
				"errnum":  []interface{}{1, 2},
				"errnum@": []interface{}{3, 4},
			},
		},
	}
	for _, testCase := range testCases {
		if testCase.expectedTemplate == "" {
			testCase.expectedTemplate = testCase.expectedRaw
		}
		t.Run(testCase.name, func(t *testing.T) {
			collapsed := Collapse(testCase.errs)
			nonNilErrs := 0
			for _, err := range testCase.errs {
				if err != nil {
					nonNilErrs += 1
				}
			}
			if nonNilErrs == 0 {
				assert.NoError(t, collapsed)
				return
			}
			require.Error(t, collapsed)
			testRepresentation(t, collapsed, testCase.expectedRaw, testCase.expectedTemplate, testCase.expectedData, testCase.expectedTags)
		})
	}
}

func TestWrapCollapse(t *testing.T) {
	testCases := []struct {
		name             string
		errs             []error
		wrapper          string
		expectedRaw      string
		expectedTemplate string
		expectedData     data
	}{
		{
			name:    "nil",
			errs:    []error{nil},
			wrapper: "wrapper",
		},
		{
			name:        "plain",
			errs:        []error{fmt.Errorf("1"), fmt.Errorf("2"), fmt.Errorf("3"), fmt.Errorf("4")},
			wrapper:     "wrapper",
			expectedRaw: "collapsed errors:\n\twrapper: 1\n\twrapper: 2\n\twrapper: 3\n\twrapper: 4",
		},
		{
			name:        "with multiline error",
			errs:        []error{fmt.Errorf("1"), fmt.Errorf("2\n2")},
			wrapper:     "wrapper",
			expectedRaw: "collapsed errors:\n\twrapper: 1\n\twrapper: 2\n\t2",
		},
		{
			name:             "with data",
			errs:             []error{Errorf("%s", NewToken("str", "string1")), Errorf("%s", NewToken("str", "string2")), Errorf("%d", NewToken("num", 123))},
			wrapper:          "wrapper",
			expectedRaw:      "collapsed errors:\n\twrapper: string1\n\twrapper: string2\n\twrapper: 123",
			expectedTemplate: "collapsed errors:\n\twrapper: [str]\n\twrapper: [num]",
			expectedData: data{
				"str": []interface{}{"string1", "string2"},
				"num": []interface{}{123},
			},
		},
		{
			name:             "singleline collapse",
			errs:             []error{Errorf("%s", NewToken("str", "string1")), Errorf("%s", NewToken("str", "string2"))},
			wrapper:          "wrapper",
			expectedRaw:      "collapsed errors:\n\twrapper: string1\n\twrapper: string2",
			expectedTemplate: "collapsed errors: wrapper: [str]",
			expectedData: data{
				"str": []interface{}{"string1", "string2"},
			},
		},
	}
	for _, testCase := range testCases {
		if testCase.expectedTemplate == "" {
			testCase.expectedTemplate = testCase.expectedRaw
		}
		t.Run(testCase.name, func(t *testing.T) {
			result := Wrap(Collapse(testCase.errs), testCase.wrapper)
			nonNilErrs := 0
			for _, err := range testCase.errs {
				if err != nil {
					nonNilErrs += 1
				}
			}
			if nonNilErrs == 0 {
				assert.NoError(t, result)
				return
			}
			require.Error(t, result)
			testRepresentation(t, result, testCase.expectedRaw, testCase.expectedTemplate, testCase.expectedData, nil)
		})
	}
}

func TestWithAddedTags(t *testing.T) {
	msg := "testError"
	tagMsg := "sampleTag"
	err := fmt.Errorf(msg)
	firstError := New(err)
	secondError := WithAddedTags(firstError, tagMsg)
	testRepresentation(t, firstError, msg, msg, nil, nil)
	testRepresentation(t, secondError, msg, msg, nil, []string{tagMsg})
}
