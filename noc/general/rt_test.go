package types_test

import (
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/noc/nocauth/pkg/types"
)

func TestSlugify(t *testing.T) {
	tests := []struct {
		s    string
		want string
	}{
		{s: "aaa", want: "aaa"},
		{s: " aaa--", want: "aaa"},
		{s: "aaa bbb, ccc", want: "aaa-bbb-ccc"},
	}
	for _, tt := range tests {
		t.Run("", func(t *testing.T) {
			require.Equal(t, tt.want, types.Slugify(tt.s))
		})
	}
}
