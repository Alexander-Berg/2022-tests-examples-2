package eventlog

import (
	"bytes"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func newTrivialRepresentable(data []byte) *trivialRepresentable {
	ret := trivialRepresentable(data)
	return &ret
}

type trivialRepresentable []byte

func (r *trivialRepresentable) MarshalBinary() ([]byte, error) {
	return *r, nil
}

func (r *trivialRepresentable) NewFromBinary(bytes []byte) (*trivialRepresentable, error) {
	return newTrivialRepresentable(bytes), nil
}

func Test_frame(t *testing.T) {
	testKey := newTrivialRepresentable([]byte("some_key"))
	testData := []*trivialRepresentable{
		newTrivialRepresentable([]byte("first_data")),
		newTrivialRepresentable([]byte("second_data")),
	}
	frame := NewFrame[trivialRepresentable, *trivialRepresentable, trivialRepresentable, *trivialRepresentable](testKey)
	for _, data := range testData {
		frame.AddData(data)
	}
	binary, err := frame.MarshalBinary()
	require.NoError(t, err)
	frameFromBinary, err := NewFrameFromBinary[trivialRepresentable, *trivialRepresentable, trivialRepresentable, *trivialRepresentable](bytes.NewReader(binary), NewReadOptions())
	require.NoError(t, err)
	assert.Equal(t, testKey, frameFromBinary.GetKey())
	assert.Equal(t, testData, frameFromBinary.GetData())
}
