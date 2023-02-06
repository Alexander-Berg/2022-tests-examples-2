package filter

import (
	"encoding/json"
	"testing"

	"github.com/stretchr/testify/require"
)

func TestUnmarshalJSON_Failed(t *testing.T) {
	type TestCase struct {
		data          interface{}
		err           string
		isSchemaValid bool
	}

	cases := []TestCase{
		{
			data: map[string]interface{}{
				"some_field": "some_value",
			},
			err: "json does not match any filter type",
		},
		{
			data: map[string]interface{}{
				"logic_op": "AND",
				"args": []map[string]interface{}{
					{
						"some_field": "some_value",
					},
				},
			},
			err: "json does not match any filter type",
		},
		{
			data: map[string]interface{}{
				"field":      "",
				"compare_op": "EQUAL",
				"values": []string{
					"1",
				},
			},
			err: "field name can't be empty",
		},
		{
			data: map[string]interface{}{
				"field":      "gateid",
				"compare_op": "EQUAL",
				"values":     []string{},
			},
			err: "field filter must have at least one value",
		},
		{
			data: map[string]interface{}{
				"logic_op": "AND",
				"args":     []map[string]interface{}{},
			},
			err: "logic operator must have at least one argument",
		},
		{
			data: map[string]interface{}{
				"field":      "gateid",
				"compare_op": "EQUAL",
				"values": []string{
					"1",
				},
				"logic_op": "AND",
				"args": []map[string]interface{}{
					{
						"field":      "gateid",
						"compare_op": "EQUAL",
						"values": []string{
							"1",
						},
					},
				},
			},
			err: "json matches more than one filter type",
		},
		{
			data: map[string]interface{}{
				"field":      "gateid",
				"compare_op": "SOME_OPERATOR",
				"values": []string{
					"1",
				},
			},
			err:           "unknown compare operator type 'SOME_OPERATOR'",
			isSchemaValid: true,
		},
		{
			data: map[string]interface{}{
				"logic_op": "SOME_OPERATOR",
				"args": []map[string]interface{}{
					{
						"field":      "gateid",
						"compare_op": "EQUAL",
						"values": []string{
							"1",
						},
					},
				},
			},
			err:           "unknown logic operator type 'SOME_OPERATOR'",
			isSchemaValid: true,
		},
	}

	for idx, c := range cases {
		data, err := json.Marshal(c.data)
		require.NoError(t, err, idx)

		if !c.isSchemaValid {
			require.Error(t, ValidateJSONSchema(data), idx)
		}

		var container FilterContainer
		err = json.Unmarshal(data, &container)
		require.Error(t, err, idx)
		require.Contains(t, err.Error(), c.err, idx)
	}
}

func TestUnmarshalJSON_FieldFilter(t *testing.T) {
	data, err := json.Marshal(map[string]interface{}{
		"field":      "mode",
		"compare_op": "CONTAINS",
		"values": []string{
			"taxi",
		},
	})
	require.NoError(t, err)
	require.NoError(t, ValidateJSONSchema(data))

	filter, err := FromJSON(data)
	require.NoError(t, err)

	field, ok := filter.(*FieldFilter)
	require.True(t, ok)
	require.Equal(t, FieldFilter{
		Field:     "mode",
		CompareOp: Contains,
		Values:    []string{"taxi"},
	}, *field)
}

func TestUnmarshalJSON_LogicOpFilter(t *testing.T) {
	data, err := json.Marshal(map[string]interface{}{
		"logic_op": "AND",
		"args": []map[string]interface{}{
			{
				"field":      "mode",
				"compare_op": "CONTAINS",
				"values": []string{
					"taxi",
				},
			},
			{
				"logic_op": "OR",
				"args": []map[string]interface{}{
					{
						"field":      "gateid",
						"compare_op": "EQUAL",
						"values": []string{
							"129",
							"100500",
						},
					},
					{
						"field":      "gateid2",
						"compare_op": "NOT_EQUAL",
						"values": []string{
							"7",
						},
					},
				},
			},
		},
	})
	require.NoError(t, err)
	require.NoError(t, ValidateJSONSchema(data))

	filter, err := FromJSON(data)
	require.NoError(t, err)

	logicOp, ok := filter.(*LogicOpFilter)
	require.True(t, ok)
	require.Equal(t, LogicAnd, logicOp.LogicOp)
	require.Equal(t, 2, len(logicOp.Args))

	arg1, ok := logicOp.Args[0].Filter.(*FieldFilter)
	require.True(t, ok)
	require.Equal(t, FieldFilter{
		Field:     "mode",
		CompareOp: Contains,
		Values:    []string{"taxi"},
	}, *arg1)

	arg2, ok := logicOp.Args[1].Filter.(*LogicOpFilter)
	require.True(t, ok)
	require.Equal(t, LogicOr, arg2.LogicOp)
	require.Equal(t, 2, len(arg2.Args))

	arg21, ok := arg2.Args[0].Filter.(*FieldFilter)
	require.True(t, ok)
	require.Equal(t, FieldFilter{
		Field:     "gateid",
		CompareOp: Equal,
		Values:    []string{"129", "100500"},
	}, *arg21)

	arg22, ok := arg2.Args[1].Filter.(*FieldFilter)
	require.True(t, ok)
	require.Equal(t, FieldFilter{
		Field:     "gateid2",
		CompareOp: NotEqual,
		Values:    []string{"7"},
	}, *arg22)
}
