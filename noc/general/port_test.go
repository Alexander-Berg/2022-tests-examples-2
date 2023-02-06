package models

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestNewPort(t *testing.T) {
	tests := []struct {
		In  string
		Out *Port
	}{
		{
			In: "80",
			Out: &Port{
				Text:  "80",
				First: 80,
				Last:  80,
			},
		},
		{
			In: "1024-65535",
			Out: &Port{
				Text:  "1024-65535",
				First: 1024,
				Last:  65535,
			},
		},
		{
			In:  "65536",
			Out: nil,
		},
		{
			In:  "007",
			Out: nil,
		},
		{
			In:  "1-007",
			Out: nil,
		},
		{
			In:  "65535-1024",
			Out: nil,
		},
	}

	for _, test := range tests {
		port, err := NewPort(test.In)
		if test.Out == nil {
			assert.Error(t, err)
		} else {
			assert.NoError(t, err)
			assert.Equal(t, port, *test.Out)
		}
	}
}

func TestMergePorts(t *testing.T) {
	tests := []struct {
		P1       []Port
		P2       []Port
		Expected []Port
	}{
		{
			P1: nil,
			P2: []Port{{
				Text:  "1",
				First: 1,
				Last:  1,
			}},
			Expected: []Port{{
				Text:  "1",
				First: 1,
				Last:  1,
			}},
		},
		{
			P1: []Port{{
				Text:  "1",
				First: 1,
				Last:  1,
			}},
			P2: []Port{{
				Text:  "1",
				First: 1,
				Last:  1,
			}},
			Expected: []Port{{
				Text:  "1",
				First: 1,
				Last:  1,
			}},
		},
		{
			P1: []Port{{
				Text:  "1",
				First: 1,
				Last:  1,
			}},
			P2: []Port{{
				Text:  "2",
				First: 2,
				Last:  2,
			}},
			Expected: []Port{
				{
					Text:  "1",
					First: 1,
					Last:  1,
				},
				{
					Text:  "2",
					First: 2,
					Last:  2,
				},
			},
		},
		{
			P1: []Port{{
				Text:  "1-3",
				First: 1,
				Last:  3,
			}},
			P2: []Port{{
				Text:  "2",
				First: 2,
				Last:  2,
			}},
			Expected: []Port{{
				Text:  "1-3",
				First: 1,
				Last:  3,
			}},
		},
		{
			P1: []Port{
				{
					Text:  "1",
					First: 1,
					Last:  1,
				},
				{
					Text:  "2",
					First: 2,
					Last:  2,
				},
				{
					Text:  "3",
					First: 3,
					Last:  3,
				},
				{
					Text:  "12",
					First: 12,
					Last:  12,
				},
			},
			P2: []Port{{
				Text:  "2-10",
				First: 2,
				Last:  10,
			}},
			Expected: []Port{
				{
					Text:  "1",
					First: 1,
					Last:  1,
				},
				{
					Text:  "2-10",
					First: 2,
					Last:  10,
				},
				{
					Text:  "12",
					First: 12,
					Last:  12,
				},
			},
		},
	}

	for _, test := range tests {
		assert.Equal(t, test.Expected, MergePorts(test.P1, test.P2))
	}
}
