package filter

import (
	"testing"

	"github.com/stretchr/testify/require"
)

var testSchema = &Schema{
	Fields: FieldsSchema{
		"gateid":      NumberFieldWithCompareSchema,
		"gateid2":     NumberFieldSchema,
		"mode":        StringFieldSchema,
		"destination": nil,
		"ts":          DatetimeFieldSchema,
		"block": EnumFieldSchema(map[string]interface{}{
			"good1": nil,
			"good2": nil,
		}),
	},
	CheckDepth: true,
	MaxDepth:   2,
}

type TestValidateCase struct {
	filter Filter
	schema *Schema
	err    string
}

func (c *TestValidateCase) run(t *testing.T, idx int) {
	err := c.schema.Validate(c.filter)
	if c.err == "" {
		require.NoError(t, err, idx)
	} else {
		require.Error(t, err, idx)
		require.Contains(t, err.Error(), c.err, idx)
	}
}

func TestValidate_Failed(t *testing.T) {
	cases := []TestValidateCase{
		{
			filter: &FieldFilter{
				Field:     "gateid3",
				CompareOp: Equal,
				Values:    []string{"129"},
			},
			schema: testSchema,
			err:    "field 'gateid3' is not permitted",
		},
		{
			filter: &FieldFilter{
				Field:     "gateid",
				CompareOp: Contains,
				Values:    []string{"129"},
			},
			schema: testSchema,
			err:    "compare operator 'CONTAINS' is not permitted for field 'gateid'",
		},
		{
			filter: &FieldFilter{
				Field:     "gateid2",
				CompareOp: StartsWith,
				Values:    []string{"129"},
			},
			schema: testSchema,
			err:    "compare operator 'STARTS_WITH' is not permitted for field 'gateid2'",
		},
		{
			filter: &LogicOpFilter{
				LogicOp: LogicAnd,
				Args: []FilterContainer{
					{
						&FieldFilter{
							Field:     "gateid",
							CompareOp: Contains,
							Values:    []string{"129"},
						},
					},
				},
			},
			schema: testSchema,
			err:    "compare operator 'CONTAINS' is not permitted for field 'gateid'",
		},
		{
			filter: &LogicOpFilter{
				LogicOp: LogicAnd,
				Args: []FilterContainer{
					{
						&LogicOpFilter{
							LogicOp: LogicOr,
							Args: []FilterContainer{
								{
									&FieldFilter{
										Field:     "gateid",
										CompareOp: Equal,
										Values:    []string{"129"},
									},
								},
							},
						},
					},
				},
			},
			schema: &Schema{
				CheckDepth: true,
				MaxDepth:   1,
			},
			err: "filter depth exceeded limit: 1",
		},
		{
			filter: &FieldFilter{
				Field:     "gateid",
				CompareOp: Less,
				Values:    []string{"129", "128"},
			},
			schema: testSchema,
			err:    "compare operator 'LESS' requires single value in 'gateid'",
		},
		{
			filter: &FieldFilter{
				Field:     "gateid",
				CompareOp: More,
				Values:    []string{"129", "128"},
			},
			schema: testSchema,
			err:    "compare operator 'MORE' requires single value in 'gateid'",
		},
		{
			filter: &FieldFilter{
				Field:     "gateid",
				CompareOp: More,
				Values:    []string{},
			},
			schema: testSchema,
			err:    "no values in 'gateid'",
		},
		{
			filter: &FieldFilter{
				Field:     "gateid",
				CompareOp: More,
				Values:    []string{"string"},
			},
			schema: testSchema,
			err:    "field 'gateid' has not allowed value 'string': should be numeric",
		},
		{
			filter: &FieldFilter{
				Field:     "ts",
				CompareOp: More,
				Values:    []string{"not_time"},
			},
			schema: testSchema,
			err:    "field 'ts' has not allowed value 'not_time': should be RFC3339 formatted datetime",
		},
		{
			filter: &FieldFilter{
				Field:     "ts",
				CompareOp: More,
				Values:    []string{"Mon, 02 Jan 2006 15:04:05 MST"},
			},
			schema: testSchema,
			err:    "field 'ts' has not allowed value 'Mon, 02 Jan 2006 15:04:05 MST': should be RFC3339 formatted datetime",
		},
		{
			filter: &FieldFilter{
				Field:     "block",
				CompareOp: Equal,
				Values:    []string{"not_value"},
			},
			schema: testSchema,
			err:    "field 'block' has not allowed value 'not_value': should be from values list",
		},
	}

	for idx, c := range cases {
		c.run(t, idx)
	}
}

func TestValidate_FieldFilter(t *testing.T) {
	cases := []TestValidateCase{
		{
			filter: &FieldFilter{
				Field:     "gateid",
				CompareOp: Equal,
				Values:    []string{"129"},
			},
			schema: testSchema,
		},
		{
			filter: &FieldFilter{
				Field:     "gateid2",
				CompareOp: NotEqual,
				Values:    []string{"129", "100500"},
			},
			schema: testSchema,
		},
		{
			filter: &FieldFilter{
				Field:     "mode",
				CompareOp: Contains,
				Values:    []string{"taxi"},
			},
			schema: testSchema,
		},
		{
			filter: &FieldFilter{
				Field:     "destination",
				CompareOp: StartsWith,
				Values:    []string{"+7"},
			},
			schema: testSchema,
		},
		{
			filter: &FieldFilter{
				Field:     "gateid",
				CompareOp: More,
				Values:    []string{"129"},
			},
			schema: testSchema,
		},
		{
			filter: &FieldFilter{
				Field:     "ts",
				CompareOp: More,
				Values:    []string{"2006-01-02T15:04:05Z"},
			},
			schema: testSchema,
		},
		{
			filter: &FieldFilter{
				Field:     "block",
				CompareOp: Equal,
				Values:    []string{"good1"},
			},
			schema: testSchema,
		},
		{
			filter: &FieldFilter{
				Field:     "block",
				CompareOp: Equal,
				Values:    []string{"good2"},
			},
			schema: testSchema,
		},
	}

	for idx, c := range cases {
		c.run(t, idx)
	}
}

func TestValidate_LogicOpFilter(t *testing.T) {
	cases := []TestValidateCase{
		{
			filter: &LogicOpFilter{
				LogicOp: LogicAnd,
				Args: []FilterContainer{
					{
						&FieldFilter{
							Field:     "mode",
							CompareOp: Contains,
							Values:    []string{"taxi"},
						},
					},
					{
						&LogicOpFilter{
							LogicOp: LogicOr,
							Args: []FilterContainer{
								{
									&FieldFilter{
										Field:     "gateid",
										CompareOp: Equal,
										Values:    []string{"129", "100500"},
									},
								},
								{
									&FieldFilter{
										Field:     "gateid2",
										CompareOp: NotEqual,
										Values:    []string{"7"},
									},
								},
							},
						},
					},
				},
			},
			schema: testSchema,
		},
	}

	for idx, c := range cases {
		c.run(t, idx)
	}
}
