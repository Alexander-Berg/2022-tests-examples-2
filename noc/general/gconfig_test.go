package gconfig

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestMerge(t *testing.T) {
	file1 := "olo: 123"
	file2 := "olo2: 321"
	res, err := MergeValues([]string{}, []byte(file1), []byte(file2))
	require.NoError(t, err)
	exp := `olo: 123
olo2: 321
`
	require.Equal(t, exp, string(res))
}

func TestMerge2(t *testing.T) {
	file1 := "olo: [ 1 ]\na: 3"
	file2 := "olo: [ 2 ]\nb: 4"
	res, err := MergeValues([]string{"olo"}, []byte(file1), []byte(file2))
	require.NoError(t, err)
	exp := "olo: [ 1 , 2 ]\na: 3\nb: 4"
	require.YAMLEq(t, exp, string(res))
}

func TestMerge3(t *testing.T) {
	file1 := "olo: { 'a': 'a' }"
	file2 := "olo: { 'b': 'b' }"
	res, err := MergeValues([]string{"olo"}, []byte(file1), []byte(file2))
	require.NoError(t, err)
	exp := "olo: { 'a': 'a' , 'b': 'b' }"
	require.YAMLEq(t, exp, string(res))
}

func TestMergeError(t *testing.T) {
	file1 := "olo: [ 1 ]\na: 3"
	file2 := "olo: false"
	res, err := MergeValues([]string{"olo"}, []byte(file1), []byte(file2))
	require.Error(t, err)
	require.YAMLEq(t, "", string(res))
}

func TestClash(t *testing.T) {
	file1 := "olo: 123"
	file2 := "olo: 321"
	res, err := MergeValues([]string{}, []byte(file1), []byte(file2))
	assert.Error(t, err)
	assert.Equal(t, "", string(res))
}
