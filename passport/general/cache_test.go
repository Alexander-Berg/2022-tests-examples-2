package cache

import (
	"os"
	"testing"

	"github.com/gofrs/flock"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/test/yatest"
	"a.yandex-team.ru/passport/infra/daemons/tvmcert/internal/utils"
)

var cacheFile = yatest.OutputPath("cache_test.json")
var cacheFileLock = yatest.OutputPath("cache_test.json.lock")

func cleanup() {
	_ = os.Remove(cacheFile)
	_ = os.Remove(cacheFileLock)
}

func TestNewManager(t *testing.T) {
	defer utils.SkipYaTest(t)
	cleanup()

	_, err := NewManager("./asdf1/cache.json")
	require.Error(t, err)
	_, err = NewManager("/asdf2/cache.json")
	require.Error(t, err)
	_, err = NewManager(yatest.OutputPath("cache_test.json"))
	require.NoError(t, err)
}

func TestManager_TryReadWrite(t *testing.T) {
	defer utils.SkipYaTest(t)
	cleanup()

	manager, err := NewManager(cacheFile)
	require.NoError(t, err)
	require.NoError(t, manager.TryWrite([]byte("some cachable data")))
	data, err := manager.TryRead()
	require.NoError(t, err)
	require.Equal(t, []byte("some cachable data"), data)
}

func TestManager_TryReadWrite2(t *testing.T) {
	defer utils.SkipYaTest(t)
	cleanup()

	manager, err := NewManager(cacheFile)
	require.NoError(t, err)
	require.NoError(t, manager.TryWrite([]byte("some cachable data")))

	lock := flock.New(cacheFileLock)
	ok, err := lock.TryLock()
	require.NoError(t, err)
	require.True(t, ok)

	require.Error(t, manager.TryWrite([]byte("some cachable data 2")))
	_, err = manager.TryRead()
	require.Error(t, err)

	err = lock.Unlock()
	require.NoError(t, err)
	require.True(t, ok)

	data, err := manager.TryRead()
	require.NoError(t, err)
	require.Equal(t, []byte("some cachable data"), data)
}
