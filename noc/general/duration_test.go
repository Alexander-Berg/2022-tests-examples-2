package text_test

import (
	"testing"

	"a.yandex-team.ru/noc/puncher/lib/text"
)

func TestDuration(t *testing.T) {
	var tests = []struct {
		str string
		out int64
	}{
		{"1s", 1e9},
		{"1000ms", 1e9},
		{"500ms", 5e8},
		{"25ms", 25e6},
		{"0", 0},
	}
	for _, test := range tests {
		var d text.Duration
		err := d.UnmarshalText([]byte(test.str))
		if err != nil {
			t.Errorf("%s: %s", test.str, err)
			continue
		}
		if int64(d.Duration) != test.out {
			t.Errorf("%s: got %d, want %d", test.str, d.Duration, test.out)
			continue
		}
	}
}
