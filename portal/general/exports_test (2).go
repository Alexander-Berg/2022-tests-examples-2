package exports

import (
	"bytes"
	"fmt"
	"io"
	"testing"

	"github.com/stretchr/testify/assert"
)

var (
	testJSONA = []byte(`{"goods": [
		"apple",
		"banana",
		"cherry"
	]}`)
	testJSONB = []byte(`{"numbers": [4, 8, 15, 16, 23, 42]}`)
)

// Заглушка для юнит-теста, чтобы не лезть в файловую систему.
func mockExportReader(exportName string) (io.Reader, error) {

	jsonD := []byte(`{damaged_json}`)
	jsonE := []byte(``)
	switch exportName {
	case "A":
		return bytes.NewReader(testJSONA), nil
	case "B":
		return bytes.NewReader(testJSONB), nil
	case "D":
		return bytes.NewReader(jsonD), nil
	case "E":
		return bytes.NewReader(jsonE), nil
	default:
		return nil, fmt.Errorf("export %s not found", exportName)
	}
}

func TestLocalFilesystemExportsClient(t *testing.T) {
	client := CreateLocalFilesystemExportsClient()
	client.SetReader(mockExportReader)

	assert := assert.New(t)

	t.Run("Valid exports", func(t *testing.T) {
		resultA, err := client.Get("A")
		if assert.NoError(err) {
			assert.Equal(resultA.Get("goods").GetStringBytes("0"), []byte("apple"))
			assert.Equal(resultA.Get("goods").GetStringBytes("1"), []byte("banana"))
			assert.Equal(resultA.Get("goods").GetStringBytes("2"), []byte("cherry"))
		}
		resultB, err := client.Get("B")
		if assert.NoError(err) {
			assert.Equal(resultB.Get("numbers").GetInt("1"), 8)
			assert.Equal(resultB.Get("numbers").GetInt("4"), 23)
		}
	})

	suits := []struct {
		name   string
		export string
	}{
		{"Non-existent export", "C"},
		{"Empty export", "D"},
		{"Broken export", "E"},
	}

	for _, suit := range suits {
		t.Run(suit.name, func(t *testing.T) {
			result, err := client.Get(suit.export)
			assert.Nil(result)
			assert.Error(err)
		})
	}
}
