package porto_test

import (
	"fmt"
	"testing"
	"time"

	"github.com/gofrs/uuid"
	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/security/libs/go/porto"
)

var (
	uuidGen = uuid.NewGen()
)

func TestContainer(t *testing.T) {
	if !isPortoAllowed(t) {
		return
	}

	t.Run("Create", testCreateContainer)
	t.Run("List", testListContainer)
	t.Run("Get", testGetContainer)
}

func testCreateContainer(t *testing.T) {
	api, err := porto.NewAPI(nil)
	if !assert.NoError(t, err) {
		return
	}

	defer func() {
		err := api.Close()
		assert.NoError(t, err)
	}()

	containerName := genContainerName()
	container, err := api.CreateWeakContainer(containerName)
	if !assert.NoError(t, err) {
		return
	}

	err = container.SetProperty("command", "ls -la /")
	if !assert.NoError(t, err) {
		return
	}

	err = container.Start()
	if !assert.NoError(t, err) {
		return
	}

	ok, err := container.Wait(10 * time.Second)
	if !assert.NoError(t, err) {
		return
	}

	if !assert.True(t, ok) {
		return
	}
}

func testListContainer(t *testing.T) {
	api, err := porto.NewAPI(nil)
	if !assert.NoError(t, err) {
		return
	}

	defer func() {
		err := api.Close()
		assert.NoError(t, err)
	}()

	containerName := genContainerName()
	container, err := api.CreateContainer(containerName)
	if !assert.NoError(t, err) {
		return
	}

	defer func() {
		err := container.Destroy()
		assert.NoError(t, err)
	}()

	err = container.SetProperty("command", "sleep 86400")
	if !assert.NoError(t, err) {
		return
	}

	err = container.Start()
	if !assert.NoError(t, err) {
		return
	}

	list, err := api.ListContainers()
	if !assert.NoError(t, err) {
		return
	}

	found := false
	for _, c := range list {
		if c.GetName() == containerName {
			found = true
			break
		}
	}

	assert.True(t, found, "container %s not present in list", containerName)
}

func testGetContainer(t *testing.T) {
	api, err := porto.NewAPI(nil)
	if !assert.NoError(t, err) {
		return
	}

	defer func() {
		err := api.Close()
		assert.NoError(t, err)
	}()

	containerName := genContainerName()
	expectedContainer, err := api.CreateContainer(containerName)
	if !assert.NoError(t, err) {
		return
	}

	defer func() {
		err := expectedContainer.Destroy()
		assert.NoError(t, err)
	}()

	err = expectedContainer.SetProperty("command", "sleep 86400")
	if !assert.NoError(t, err) {
		return
	}

	err = expectedContainer.Start()
	if !assert.NoError(t, err) {
		return
	}

	actualContainer, err := api.GetContainer(containerName)
	if !assert.NoError(t, err) {
		return
	}

	assert.Equal(t, expectedContainer.GetName(), actualContainer.GetName())
	actualCommand, err := actualContainer.GetProperty("command")
	if !assert.NoError(t, err) {
		return
	}
	assert.Equal(t, "sleep 86400", actualCommand)
}

func genContainerName() string {
	rnd, _ := uuidGen.NewV4()
	return fmt.Sprintf("container-%s", rnd)
}
