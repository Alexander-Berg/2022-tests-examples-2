package decoder

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/noc/snmptrapper/internal/snmp"
)

func TestMapGrep(t *testing.T) {
	as := require.New(t)
	testData := map[string]string{
		"test.0": "value",
	}
	postPref, value, err := snmp.MapGrep(testData, "test.")
	as.NoError(err)
	as.Equal(postPref, "0")
	as.Equal(value, "value")
}

func TestMapGrepErrDupFound(t *testing.T) {
	as := assert.New(t)
	testData := map[string]string{
		"test.0": "value",
		"test.1": "value",
	}
	postPref, value, err := snmp.MapGrep(testData, "test.")
	as.ErrorAs(err, &snmp.ErrDupFound)
	as.Equal(postPref, "")
	as.Equal(value, "")
}

func TestMapGrepErrNotFound(t *testing.T) {
	as := assert.New(t)
	testData := map[string]string{
		"test.1": "value",
	}
	postPref, value, err := snmp.MapGrep(testData, "atest.")
	as.ErrorAs(err, &snmp.ErrNotFound)
	as.Equal(postPref, "")
	as.Equal(value, "")
}
