package graph

import (
	"strings"
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/noc/nalivkin/internal/vars"
)

func TestLoadFromYaml(t *testing.T) {
	text := `
name: Some name
description: Some descr
inputs:
  - var: some_param
    name: Some param
    type: int
    default: 666
    choices:
      - 1
      - 2
      - 3
      - 666
    help: |
      Some variable to do some stuff
stages:
    - label: Stage 1
      steps:
        - label: start
          action: start
          outputs:
              # id устройства которое будет наливаться
              - var: object_id
                type: int
              # имя объекта предполагаемое для наливки
              - var: input_object_name
                type: str
          next:
              - racktables object name alloc
          onfail_delay: 5

        - label: racktables object name alloc
          action: racktables_object_name_alloc
          args:
              object_id: "{{ object_id }}"
              object_name: "{{ input_object_name }}"
              int_var: 123
              string_var: hello there
          next:
              - finish

        - label: finish
          action: finish
`
	template, err := LoadTemplateFromYaml(strings.NewReader(text), "myslug")
	assert.NoError(t, err)
	assert.Equal(t, []Input{
		{
			Var:     "some_param",
			Name:    "Some param",
			Type:    "int",
			Default: 666,
			Choices: []InputValue{1, 2, 3, 666},
			Help:    "Some variable to do some stuff\n",
		},
	}, template.Inputs)
	assert.Equal(t, 3, len(template.Stages[0].Steps))
	assert.Equal(
		t,
		map[string]vars.ReferenceVar{
			"int_var":     vars.NewReferenceVar(vars.NewInt(123)),
			"object_id":   vars.NewRef("object_id"),
			"object_name": vars.NewRef("input_object_name"),
			"string_var":  vars.NewReferenceVar(vars.NewString("hello there")),
		},
		template.Stages[0].Steps[1].Args(),
	)
}
