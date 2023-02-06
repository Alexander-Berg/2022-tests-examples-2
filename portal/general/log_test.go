package log2

import (
	"bytes"
	"encoding/json"
	"testing"

	"github.com/stretchr/testify/assert"
)

type bufferCloser struct {
	bytes.Buffer
}

func (bc *bufferCloser) Close() error {
	return nil
}
func (bc *bufferCloser) ReadJSONAndConvertToMap() (map[string]interface{}, error) {
	bytesSlice := make([]byte, bc.Len())
	if _, err := bc.Read(bytesSlice); err != nil {
		return nil, err
	}

	mapping := map[string]interface{}{}
	if err := json.Unmarshal(bytesSlice, &mapping); err != nil {
		return nil, err
	}
	return mapping, nil
}

func TestLogger(t *testing.T) {
	buffer := &bufferCloser{}
	backendInfo := LogItemBackend{
		Location:    "vla",
		Host:        "some-host.yandex.net",
		Language:    "go",
		Version:     "1.2.3",
		Environment: "test",
		Project:     "testProject",
	}
	logger, err := newLogger(WithWriteCloser(buffer), WithBackendInfo(backendInfo))
	if !assert.NoError(t, err) {
		assert.FailNowf(t, "an error occurred", "%w", err)
	}
	logger.Warn(
		"some_message",
		LogItemRequest{
			Message:   "__not_for_use__",
			IP:        "8.8.8.8",
			YandexUID: "1234567890123456789",
		},
	)

	actualJSON, err := buffer.ReadJSONAndConvertToMap()
	if err != nil {
		assert.FailNowf(t, "cannot unmarshal JSON from bytes buffer", "%#v", err)
	}

	for k, v := range map[string]interface{}{
		"project":   "testProject",
		"message":   "some_message",
		"host":      "some-host.yandex.net",
		"language":  "go",
		"dc":        "vla",
		"version":   "1.2.3",
		"env":       "test",
		"ip":        "8.8.8.8",
		"yandexuid": "1234567890123456789",
	} {
		assert.Equal(t, v, actualJSON[k], "key: %s", k)
	}
}
