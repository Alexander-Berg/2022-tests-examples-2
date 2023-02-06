package marshaller

import (
	"io/ioutil"
	"os"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"gopkg.in/yaml.v2"

	"a.yandex-team.ru/library/go/test/yatest"
)

// do some tests in cycle so that we don't depend on map traversing order
const iterNum = 10

func TestMarshalM4Empty(t *testing.T) {
	data := map[string][]string{}

	bytes := MarshalM4(data)
	require.Nil(t, bytes)
}

func TestMarshalYAMLEmpty(t *testing.T) {
	data := map[string][]string{}

	bytes := MarshalYaml(data)
	require.Nil(t, bytes)
}

func TestMarshalM4(t *testing.T) {
	data := map[string][]string{
		"a": {"b", "c", "d"},
		"s": {},
	}

	expectedStringFirst := "" +
		"# This file was generated automatically. Do not edit!" +
		"\n" +
		"\n" +
		"define(" +
		"\n  `a', dnl" +
		"\n  `b or dnl" +
		"\n   c or dnl" +
		"\n   d'" +
		"\n)" +
		"\n" +
		"\n" +
		"define(" +
		"\n  `s', dnl" +
		"\n  `240.0.0.0/32'" +
		"\n)" +
		"\n" +
		"\n"

	expectedStringSecond :=
		"" +
			"# This file was generated automatically. Do not edit!" +
			"\n" +
			"\n" +
			"define(" +
			"\n  `s', dnl" +
			"\n  `240.0.0.0/32'" +
			"\n)" +
			"\n" +
			"\n" +
			"define(" +
			"\n  `a', dnl" +
			"\n  `b or dnl" +
			"\n   c or dnl" +
			"\n   d'" +
			"\n)" +
			"\n" +
			"\n"

	for i := 0; i < iterNum; i++ {
		bytes := MarshalM4(data)
		assert.Contains(t, []string{expectedStringFirst, expectedStringSecond}, string(bytes))
	}
}

func TestMarshalYAML(t *testing.T) {
	data := map[string][]string{
		"a": {"b", "c", "d"},
		"s": {"d", "f", "g"},
		"t": {},
	}

	bytes := MarshalYaml(data)

	res := map[string][]string{}
	_ = yaml.Unmarshal(bytes, &res)
	require.Equal(t, data, res)
}

func TestExport(t *testing.T) {
	getDir := func() (ret string) {
		defer func() {
			if err := recover(); err != nil {
				ret = "./gotest/test-expand"
			}
		}()

		return yatest.WorkPath("./test-expand")
	}
	dir := getDir()
	dataPath := dir + "/a/b/c/data.txt"

	data := "Lorem ipsum dolor sit amet"
	bytes := []byte(data)

	err := Export(bytes, dataPath)
	require.NoError(t, err)

	resBytes, err := ioutil.ReadFile(dataPath)
	require.NoError(t, err)
	require.Equal(t, bytes, resBytes)

	err = os.RemoveAll(dir)
	require.NoError(t, err)
}
