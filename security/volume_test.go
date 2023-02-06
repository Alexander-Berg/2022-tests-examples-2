package porto_test

import (
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/security/libs/go/porto"
)

func TestVolume(t *testing.T) {
	if !isPortoAllowed(t) {
		return
	}

	t.Run("Create", testCreateVolume)
}

func testCreateVolume(t *testing.T) {
	api, err := porto.NewAPI(nil)
	if !assert.NoError(t, err) {
		return
	}

	defer func() {
		err := api.Close()
		assert.NoError(t, err)
	}()

	volume, err := api.CreateVolume("", nil)
	if !assert.NoError(t, err) {
		return
	}

	defer func() {
		err := volume.Destroy()
		assert.NoError(t, err)
	}()

	assert.NotEmpty(t, volume.Path())
}
