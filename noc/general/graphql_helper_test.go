package rtmut_test

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/noc/cmdb/pkg/rtmut"
	"a.yandex-team.ru/noc/cmdb/pkg/types"
)

type UpdateFilter struct {
	CIDR string `graphql:"cidr"`
}

type UpdateInput struct {
	Name string `graphql:"name"`
}

type Update struct {
	Filter UpdateFilter `graphql:"filter"`
	Input  UpdateInput  `graphql:"input"`
}

func TestMethod_String(t *testing.T) {
	s, _, err := rtmut.Method{
		Alias: "update0",
		Name:  "update",
		Args: Update{
			Filter: UpdateFilter{
				CIDR: "",
			},
			Input: UpdateInput{
				Name: "",
			},
		},
	}.Variables()
	require.NoError(t, err)
	require.Equal(t, `update0:update(filter:{cidr:$update0CIDR},input:{name:$update0Name})`, s)
}

type InputIPNet struct {
	Name string `graphql:"name"`
}

type InputIPNetFilterOne struct {
	CIDR types.NetCIDR `graphql:"cidr"`
}

type UpdateIPNet struct {
	Filter InputIPNetFilterOne `graphql:"filter"`
	Input  InputIPNet          `graphql:"input"`
}

func (u UpdateIPNet) MethodName() string {
	return "update"
}

type Mutations struct {
	IPNet [][2]interface{} `graphql:"IPNet"`
}

type IPNet struct {
	CIDR string `graphql:"cidr"`
	Name string `graphql:"name"`
}

func TestPrepareMutations(t *testing.T) {
	key := UpdateIPNet{
		Filter: InputIPNetFilterOne{
			CIDR: "1.1.1.0/24",
		},
		Input: InputIPNet{
			Name: "dummy",
		},
	}
	m := Mutations{IPNet: [][2]interface{}{
		{key, IPNet{}},
	}}
	expected := Mutations{IPNet: [][2]interface{}{
		{"IPNetX0update:update(filter:{cidr:$IPNetX0updateCIDR},input:{name:$IPNetX0updateName})", IPNet{}},
	}}
	vars, err := rtmut.PrepareMutations(&m)
	require.NoError(t, err)
	assert.Equal(t, expected, m)
	assert.Equal(t, rtmut.Variables{
		"IPNetX0updateCIDR": types.NetCIDR("1.1.1.0/24"),
		"IPNetX0updateName": "dummy",
	}, vars)
}

func TestPrepareMutationsSlice(t *testing.T) {
	key := UpdateIPNet{
		Filter: InputIPNetFilterOne{
			CIDR: "1.1.1.0/24",
		},
		Input: InputIPNet{
			Name: "dummy",
		},
	}
	m := [][2]interface{}{{"IPNet", [][2]interface{}{
		{key, IPNet{}},
	}}}
	expected := [][2]interface{}{{"IPNet", [][2]interface{}{
		{"X0IPNetX0update:update(filter:{cidr:$X0IPNetX0updateCIDR},input:{name:$X0IPNetX0updateName})", IPNet{}},
	}}}
	vars, err := rtmut.PrepareMutations(&m)
	require.NoError(t, err)
	assert.Equal(t, expected, m)
	assert.Equal(t, rtmut.Variables{
		"X0IPNetX0updateCIDR": types.NetCIDR("1.1.1.0/24"),
		"X0IPNetX0updateName": "dummy",
	}, vars)
}
