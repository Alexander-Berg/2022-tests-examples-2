package maven_test

import (
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/security/yadi/libs/maven"
)

func TestParseRange(t *testing.T) {
	type tv struct {
		v string
		b bool
	}
	tests := []struct {
		i string
		t []tv
	}{
		// Simple expressions
		{"(1.2.3, )", []tv{
			{"1.2.2", false},
			{"1.2.3", false},
			{"1.2.4", true},
		}},
		{"[1.2.3, )", []tv{
			{"1.2.3", true},
			{"1.2.4", true},
			{"1.2.2", false},
		}},
		{"[0, 1.2.3)", []tv{
			{"1.2.2", true},
			{"1.2.3", false},
			{"1.2.4", false},
		}},
		{"(0, 1.2.3]", []tv{
			{"1.2.2", true},
			{"1.2.3", true},
			{"1.2.4", false},
		}},
		{"[1.2.3]", []tv{
			{"1.2.2", false},
			{"1.2.3", true},
			{"1.2.4", false},
		}},

		// Simple Expression errors
		{"(1.2.3)", nil},
		{"(1.2.3]", nil},
		{"1.0", nil},

		// Expressions
		{"(1.2.2, 1.2.4)", []tv{
			{"1.2.2", false},
			{"1.2.3", true},
			{"1.2.4", false},
		}},
		{"(1.2.2, 1.2.5), [1.2.6]", []tv{
			{"1.2.2", false},
			{"1.2.3", true},
			{"1.2.5", false},
			{"1.2.6", true},
		}},
		{"(1.2.2,1.2.5), (1.2.5,1.2.6]", []tv{
			{"1.2.2", false},
			{"1.2.3", true},
			{"1.2.5", false},
			{"1.2.6", true},
		}},
		// Qualifiers
		{
			"(1.2.3, 1.5.0-beta]", []tv{
				{"1.2.3a", false},
				{"1.2.3-sp2", true},
				{"1.5.0-alpha", true},
				{"1.5.0-rc3", false},
			}},
		{
			"(1.0.0-alpha,1.0.0-release), [1.5.0-release]", []tv{
				{"1.0.0", false},
				{"1.0.0-foobar", false},
				{"1.0.0-10", false},
				{"1.5.0-alpha", false},
				{"1.5.0-0", true},
			}},
	}

	for _, tc := range tests {
		t.Run(tc.i, func(t *testing.T) {
			r, err := maven.ParseRange(tc.i)
			if err != nil && tc.t == nil {
				return
			}
			require.NoError(t, err)
			for _, tvc := range tc.t {
				t.Run(tvc.v, func(t *testing.T) {
					v, err := maven.ParseVersion(tvc.v)
					require.NoError(t, err)
					if err != nil {
						return
					}
					resolution := r(v)
					require.Equal(t, tvc.b, resolution)
				})
			}
		})
	}
}
