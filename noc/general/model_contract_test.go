package model

import (
	"encoding/json"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/valid"
)

func Test_Contract_Ok(t *testing.T) {
	tests := []struct {
		name     string
		val      []byte
		expected Contract
	}{
		{"number", []byte(`{"number":"num1"}`), Contract{Number: "num1"}},
		{"owners", []byte(`{"number":"num2","business_owner":1,"technical_owner":2}`),
			Contract{Number: "num2", BusinessOwner: 1, TechnicalOwner: 2}},
		{"owners string", []byte(`{"number":"num2","business_owner":"1","technical_owner":"2"}`),
			Contract{Number: "num2", BusinessOwner: 1, TechnicalOwner: 2}},
		{"uuid", []byte(`{"number":"num3","object_uuid":"e75d3cfb-2c0f-4bea-8473-f19047a85e7c",` +
			`"parent_object_uuid":"0fae6f76-1afb-4b1f-9a83-d41a19df5741"}`),
			Contract{
				Number:           "num3",
				ObjectUUID:       "e75d3cfb-2c0f-4bea-8473-f19047a85e7c",
				ParentObjectUUID: "0fae6f76-1afb-4b1f-9a83-d41a19df5741"}},
		{"tickets", []byte(`{"number":"num4","st_tickets":["ST-1","ST-2"],"procu_ticket":"PROCU-2"}`),
			Contract{
				Number:      "num4",
				StTickets:   []string{"ST-1", "ST-2"},
				ProcuTicket: NewNullString("PROCU-2")}},
		{"dates", []byte(`{"number":"num5","start_date":"2022-02-02","finish_date":"2023-03-03"}`),
			Contract{
				Number:     "num5",
				StartDate:  NewNullTime("2022-02-02T00:00:00Z"),
				FinishDate: NewNullTime("2023-03-03T00:00:00Z")}},
		{"description", []byte(`{"number":"num6","description":"text1"}`), Contract{
			Number:      "num6",
			Description: NewNullString("text1")}},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			ctx := NewValidationCtx()
			var v Contract
			err := json.Unmarshal(test.val, &v)
			require.NoError(t, err)
			err = valid.Struct(ctx, v)
			require.NoError(t, err)
			require.Equal(t, test.expected, v)
		})
	}
}

func Test_ContractFromDBJson_ok(t *testing.T) {
	var tests = []struct {
		name     string
		j        string
		expected Contract
	}{
		{
			name: "nulls",
			j: `{"number": "number1", "object_id": "73f4294d-269a-4c7d-a393-13d63b68cdd4", ` +
				`"start_date": null, "description": null, "finish_date": null, ` +
				`"procu_ticket": null, "business_owner": 1, "st_tickets": null, ` +
				`"tags":[null],` +
				`"technical_owner": 2, "parent_object_id": "73f4294d-269a-4c7d-a393-13d63b68cdd3"}`,
			expected: Contract{
				"73f4294d-269a-4c7d-a393-13d63b68cdd4",
				"73f4294d-269a-4c7d-a393-13d63b68cdd3",
				"number1",
				1,
				2,
				nil,
				nil,
				nil,
				nil,
				nil,
				nil,
				&TreeInfo{},
			},
		},
		{
			name: "filled",
			j: `{"level": 2, "number": "number1", "object_id": "73f4294d-269a-4c7d-a393-13d63b68cdd4", ` +
				`"start_date": "2022-02-02T00:00:00Z", "child_count": 1, "description": "desc2", "finish_date": "2023-03-03T00:00:00Z", ` +
				`"procu_ticket": "PROCU-2", "business_owner": 1, "st_tickets": ["ST-1", "ST-2"], ` +
				`"technical_owner": 2, "parent_object_id": "73f4294d-269a-4c7d-a393-13d63b68cdd3",` +
				`"tags":[{"id": 2,"tag": "tag1", "color": "#ff1122", "parent_id": 1, "description": "test"}],` +
				`"child_count":5,"level":3}`,
			expected: Contract{
				"73f4294d-269a-4c7d-a393-13d63b68cdd4",
				"73f4294d-269a-4c7d-a393-13d63b68cdd3",
				"number1",
				1,
				2,
				[]string{"ST-1", "ST-2"},
				NewNullString("PROCU-2"),
				NewNullTime("2022-02-02T00:00:00Z"),
				NewNullTime("2023-03-03T00:00:00Z"),
				NewNullString("desc2"),
				[]Tag{
					{
						ID:          2,
						Tag:         "tag1",
						Color:       NewNullString("#ff1122"),
						ParentID:    NewCustom32Ref(1),
						Description: NewNullString("test"),
					},
				},
				&TreeInfo{5, 3},
			},
		},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			v, err := NewContractFromDBJson(test.j)
			require.NoError(t, err)
			require.Equal(t, test.expected, *v)
		})
	}
}

func Test_ContractFromDBJson_err(t *testing.T) {
	_, err := NewContractFromDBJson("")
	require.Error(t, err)
	require.Equal(t, "unexpected end of JSON input", err.Error())
}
