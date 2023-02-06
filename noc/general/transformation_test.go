package core

import (
	"regexp"
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/noc/metridat/internal/container"
)

func TestTransform(t *testing.T) {
	tests := []struct {
		name      string
		data      container.Container
		expected  container.Container
		transform *transform
	}{
		{
			name:      "test string tag",
			data:      container.NewContainerFull("test", container.Tags{"test": "testtag"}, container.Values{"ololo": container.UIntToAny(123), "key": container.StringToAny("q")}, 0),
			expected:  container.NewContainerFull("test", container.Tags{"test": "testtag", "key": "q"}, container.Values{"ololo": container.UIntToAny(123)}, 0),
			transform: newTransform(true, newActions(), newActions(), ""),
		},
		{
			name:      "test values",
			data:      container.NewContainerFull("test", container.Tags{"test": "testtag"}, container.Values{"/a/b/ololo": container.UIntToAny(123)}, 0),
			expected:  container.NewContainerFull("test", container.Tags{"test": "testtag"}, container.Values{"ololo": container.UIntToAny(123)}, 0),
			transform: newTransform(true, newActions(newActionRenameMust("^/a/b/([ol]+)$", `$1`)), newActions(), ""),
		},
		{
			name: "drop value",
			data: container.NewContainerFull("test", container.Tags{"test": "testtag"},
				container.Values{"drop_me": container.UIntToAny(123), "not_drop_me": container.UIntToAny(321)}, 0),
			expected: container.NewContainerFull("test", container.Tags{"test": "testtag"},
				container.Values{"not_drop_me": container.UIntToAny(321)}, 0),
			transform: newTransform(true, newActions(newActionDropMust("^drop_me$")), newActions(), ""),
		},
		{
			name: "drop value expr",
			data: container.NewContainerFull("test", container.Tags{"test": "testtag"},
				container.Values{"/interfaces/state/drop_me": container.UIntToAny(123), "not_drop_me": container.UIntToAny(321)}, 0),
			expected: container.NewContainerFull("test", container.Tags{"test": "testtag"},
				container.Values{"not_drop_me": container.UIntToAny(321)}, 0),
			transform: newTransform(true, newActions(newActionDropMust("^/interfaces/state/.+")), newActions(), ""),
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			res, err := tt.transform.TransformContainer(tt.data)
			assert.NoError(t, err)
			resJSON, err := res.FormatJSON()
			assert.NoError(t, err)
			expJSON, err := tt.expected.FormatJSON()
			assert.NoError(t, err)
			assert.JSONEq(t, expJSON, resJSON)
		})
	}
}

func TestTransformError(t *testing.T) {
	tests := []struct {
		name        string
		data        container.Container
		expectedErr string
		transform   *transform
	}{
		{
			name:        "dups",
			data:        container.NewContainerFull("test", container.Tags{"test": "testtag"}, container.Values{"key1": container.UIntToAny(123), "key2": container.UIntToAny(321)}, 0),
			expectedErr: "duplicated new value key key[12] -> ololo",
			transform:   newTransform(true, newActions(newActionRenameMust("^.+$", `ololo`)), newActions(), ""),
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			res, err := tt.transform.TransformContainer(tt.data)
			assert.Regexp(t, regexp.MustCompile(tt.expectedErr), err)
			assert.Nil(t, res)
		})
	}
}
