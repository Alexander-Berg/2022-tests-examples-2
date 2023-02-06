package filter

import (
	"testing"

	"github.com/stretchr/testify/require"
)

var mysqlTestFields = map[string]string{
	"gateid":      "sqlgateid",
	"mode":        "sqlmode",
	"destination": "sqldestination",
}

type TestToMySQLQueryCase struct {
	filter Filter
	query  string
	args   []interface{}
	err    string
}

func (c *TestToMySQLQueryCase) run(t *testing.T, idx int) {
	query, args, err := c.filter.ToMySQLQuery(mysqlTestFields, nil)
	if c.err == "" {
		require.NoError(t, err, idx)
		require.Equal(t, c.query, query)
		require.Equal(t, c.args, args)
	} else {
		require.Error(t, err, idx)
		require.Contains(t, err.Error(), c.err, idx)
	}
}

func TestToMySQLQuery_Failed(t *testing.T) {
	cases := []TestToMySQLQueryCase{
		{
			filter: &FieldFilter{
				Field:     "gateid",
				CompareOp: Equal,
			},
			err: "malformed filter: empty values for field filter",
		},
		{
			filter: &LogicOpFilter{
				LogicOp: LogicAnd,
			},
			err: "malformed filter: empty args for logic operator",
		},
		{
			filter: &FieldFilter{
				Field:     "gateid",
				CompareOp: CompareOperator(-1),
				Values:    []string{"129"},
			},
			err: "malformed filter: unknown compare operator type '-1'",
		},
		{
			filter: &LogicOpFilter{
				LogicOp: LogicOperator(-1),
				Args: []FilterContainer{
					{
						&FieldFilter{
							Field:     "gateid",
							CompareOp: Equal,
							Values:    []string{"129"},
						},
					},
					{
						&FieldFilter{
							Field:     "mode",
							CompareOp: Contains,
							Values:    []string{"taxi"},
						},
					},
				},
			},
			err: "malformed filter: unknown logic operator '-1'",
		},
		{
			filter: &FieldFilter{
				Field:     "gateid2",
				CompareOp: Equal,
				Values:    []string{"129"},
			},
			err: "unexpected field 'gateid2'",
		},
	}

	for idx, c := range cases {
		c.run(t, idx)
	}
}

func TestToMySQLQuery_FieldFilter(t *testing.T) {
	cases := []TestToMySQLQueryCase{
		{
			filter: &FieldFilter{
				Field:     "gateid",
				CompareOp: Equal,
				Values:    []string{"129", "100500"},
			},
			query: `sqlgateid IN (?)`,
			args:  []interface{}{[]string{"129", "100500"}},
		},
		{
			filter: &FieldFilter{
				Field:     "mode",
				CompareOp: Contains,
				Values:    []string{"taxi"},
			},
			query: `sqlmode LIKE ?`,
			args:  []interface{}{"%taxi%"},
		},
		{
			filter: &FieldFilter{
				Field:     "mode",
				CompareOp: Contains,
				Values:    []string{"t_\\%"},
			},
			query: `sqlmode LIKE ?`,
			args:  []interface{}{"%t\\_\\\\\\%%"},
		},
		{
			filter: &FieldFilter{
				Field:     "destination",
				CompareOp: StartsWith,
				Values:    []string{"+7", "+20"},
			},
			query: `(sqldestination LIKE ? OR sqldestination LIKE ?)`,
			args:  []interface{}{"+7%", "+20%"},
		},
	}

	for idx, c := range cases {
		c.run(t, idx)
	}
}

func TestToMySQLQuery_LogicOpFilter(t *testing.T) {
	cases := []TestToMySQLQueryCase{
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
										Field:     "destination",
										CompareOp: StartsWith,
										Values:    []string{"+7", "+20"},
									},
								},
								{
									&FieldFilter{
										Field:     "gateid",
										CompareOp: Equal,
										Values:    []string{"129", "100500"},
									},
								},
							},
						},
					},
				},
			},
			query: `(sqlmode LIKE ? AND ((sqldestination LIKE ? OR sqldestination LIKE ?) OR sqlgateid IN (?)))`,
			args:  []interface{}{"%taxi%", "+7%", "+20%", []string{"129", "100500"}},
		},
	}

	for idx, c := range cases {
		c.run(t, idx)
	}
}
