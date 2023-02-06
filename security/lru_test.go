package rescache

import (
	"container/list"
	"io/ioutil"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"go.uber.org/zap/zaptest"

	"a.yandex-team.ru/library/go/core/log/zap"
)

func TestCacheRelease(t *testing.T) {
	cc := Cache{
		maxSize: 1024,
		list:    list.New(),
		items:   make(map[string]*list.Element),
		log:     &zap.Logger{L: zaptest.NewLogger(t)},
	}

	tmpDir, err := ioutil.TempDir("", "")
	require.NoError(t, err)

	defer func() {
		_ = os.RemoveAll(tmpDir)
	}()

	for i := 0; i < 2048; i++ {
		uri := strconv.Itoa(i)
		l, err := cc.Fetch(uri, func() (*Resource, error) {
			targetPath := filepath.Join(tmpDir, uri)
			err = ioutil.WriteFile(targetPath, []byte{'A'}, 0o600)
			if err != nil {
				return nil, err
			}

			return &Resource{
				ID:    uri,
				Path:  targetPath,
				Bytes: 1,
			}, nil
		})

		assert.NotNil(t, l)
		assert.NoError(t, err)
		l.Release()
	}

	files, err := ioutil.ReadDir(tmpDir)
	if err != nil {
		require.NoError(t, err)
	}

	require.Len(t, files, 1024)
	for _, f := range files {
		i, err := strconv.Atoi(f.Name())
		assert.NoError(t, err)
		assert.GreaterOrEqual(t, i, 1024)
		assert.LessOrEqual(t, i, 2048)
	}
}

func TestCacheCleanup(t *testing.T) {
	cc := Cache{
		maxSize: 20,
		list:    list.New(),
		items:   make(map[string]*list.Element),
		log:     &zap.Logger{L: zaptest.NewLogger(t)},
	}

	tmpDir, err := ioutil.TempDir("", "")
	require.NoError(t, err)

	defer func() {
		_ = os.RemoveAll(tmpDir)
	}()

	for i := 0; i < 20; i++ {
		uri := "s_" + strconv.Itoa(i)
		l, err := cc.Fetch(uri, func() (*Resource, error) {
			targetPath := filepath.Join(tmpDir, uri)
			err = ioutil.WriteFile(targetPath, []byte{'A'}, 0o600)
			if err != nil {
				return nil, err
			}

			return &Resource{
				ID:    uri,
				Path:  targetPath,
				Bytes: 1,
			}, nil
		})

		assert.NotNil(t, l)
		assert.NoError(t, err)
		l.Release()
	}

	for i := 0; i < 5; i++ {
		uri := "h_" + strconv.Itoa(i)
		l, err := cc.Fetch(uri, func() (*Resource, error) {
			targetPath := filepath.Join(tmpDir, uri)
			err = ioutil.WriteFile(targetPath, []byte{'A', 'A', 'A', 'A'}, 0o600)
			if err != nil {
				return nil, err
			}

			return &Resource{
				ID:    uri,
				Path:  targetPath,
				Bytes: 4,
			}, nil
		})

		assert.NotNil(t, l)
		assert.NoError(t, err)
		l.Release()
	}

	files, err := ioutil.ReadDir(tmpDir)
	if err != nil {
		require.NoError(t, err)
	}

	require.Len(t, files, 5)

	for _, f := range files {
		t.Logf("file: %s\n", f.Name())

		parts := strings.Split(f.Name(), "_")
		prefix, idx := parts[0], parts[1]
		if !assert.Equal(t, "h", prefix) {
			continue
		}

		i, err := strconv.Atoi(idx)
		assert.NoError(t, err)
		assert.GreaterOrEqual(t, i, 0)
		assert.LessOrEqual(t, i, 5)
	}
}

func TestAutofix(t *testing.T) {
	cc := Cache{
		maxSize: 20,
		list:    list.New(),
		items:   make(map[string]*list.Element),
		log:     &zap.Logger{L: zaptest.NewLogger(t)},
	}

	tmpDir, err := ioutil.TempDir("", "")
	require.NoError(t, err)

	defer func() {
		_ = os.RemoveAll(tmpDir)
	}()

	createItems := func() {
		for i := 0; i < 20; i++ {
			uri := strconv.Itoa(i)
			l, err := cc.Fetch(uri, func() (*Resource, error) {
				targetPath := filepath.Join(tmpDir, uri)
				err = ioutil.WriteFile(targetPath, []byte{'A'}, 0o600)
				if err != nil {
					return nil, err
				}

				return &Resource{
					ID:    uri,
					Path:  targetPath,
					Bytes: 1,
				}, nil
			})

			assert.NotNil(t, l)
			assert.NoError(t, err)
			l.Release()
		}
	}

	createItems()

	err = os.RemoveAll(tmpDir)
	require.NoError(t, err)

	err = os.MkdirAll(tmpDir, 0o700)
	require.NoError(t, err)

	createItems()

	files, err := ioutil.ReadDir(tmpDir)
	if err != nil {
		require.NoError(t, err)
	}

	require.Len(t, files, 20)
	for _, f := range files {
		t.Logf("file: %s\n", f.Name())

		idx, err := strconv.Atoi(f.Name())
		assert.NoError(t, err)
		assert.GreaterOrEqual(t, idx, 0)
		assert.LessOrEqual(t, idx, 20)
	}
}
