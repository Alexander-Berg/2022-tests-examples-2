package vars

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestInputValidate(t *testing.T) {
	var err error

	// ok
	err = InputValidate(
		InputSchema{
			"object_id": Input{
				Name: "object_id",
				Type: IntType,
			},
		},
		VarMap{
			"input.object_id": NewInt(123),
		},
	)
	assert.NoError(t, err)

	// missing variable
	err = InputValidate(
		InputSchema{
			"object_id": Input{
				Name: "object_id",
				Type: IntType,
			},
		},
		VarMap{},
	)
	assert.ErrorIs(t, err, ErrorInputValidate)

	// invalid type
	err = InputValidate(
		InputSchema{
			"object_id": Input{
				Name: "object_id",
				Type: IntType,
			},
		},
		VarMap{
			"input.object_id": NewString("123"),
		},
	)
	assert.ErrorIs(t, err, ErrorInputValidate)

	// choices no error
	err = InputValidate(
		InputSchema{
			"object_id": Input{
				Name: "object_id",
				Type: IntType,
				Choices: []Var{
					NewInt(123),
				},
			},
		},
		VarMap{
			"input.object_id": NewInt(123),
		},
	)
	assert.NoError(t, err)

	// choices error
	err = InputValidate(
		InputSchema{
			"object_id": Input{
				Name: "object_id",
				Type: IntType,
				Choices: []Var{
					NewInt(789),
				},
			},
		},
		VarMap{
			"input.object_id": NewInt(123),
		},
	)
	assert.ErrorIs(t, err, ErrorInputValidate)
}

func TestInputFill(t *testing.T) {
	args := VarMap{}
	err := InputFill(
		InputSchema{
			"object_id": Input{
				Name:    "object_id",
				Type:    IntType,
				Default: NewInt(666),
			},
		},
		args,
	)
	assert.NoError(t, err)
	assert.Contains(t, args, "input.object_id")
	val, err := IntVal(args["input.object_id"])
	assert.NoError(t, err)
	assert.Equal(t, 666, val)
}
