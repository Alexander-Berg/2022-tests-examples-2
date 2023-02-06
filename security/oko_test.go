package server_test

import (
	"bytes"
	"context"
	"encoding/json"
	"io/ioutil"
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/security/libs/go/simplelog"
	"a.yandex-team.ru/security/yadi/yaudit/internal/config"
	"a.yandex-team.ru/security/yadi/yaudit/internal/server"
)

func buildPkgLockReq(t testing.TB, withDev bool) []byte {
	pkgData, err := ioutil.ReadFile(filepath.Join("testdata", "oko", "package.json"))
	require.NoError(t, err)

	lockData, err := ioutil.ReadFile(filepath.Join("testdata", "oko", "package-lock.json"))
	require.NoError(t, err)

	out, err := json.Marshal(struct {
		WithDev         bool            `json:"with_dev"`
		PackageJSON     json.RawMessage `json:"package"`
		PackageLockJSON json.RawMessage `json:"package_lock"`
	}{
		WithDev:         withDev,
		PackageJSON:     pkgData,
		PackageLockJSON: lockData,
	})
	require.NoError(t, err)
	return out
}

func buildYarnLockReq(t testing.TB, withDev bool) []byte {
	pkgData, err := ioutil.ReadFile(filepath.Join("testdata", "oko", "package.json"))
	require.NoError(t, err)

	lockData, err := ioutil.ReadFile(filepath.Join("testdata", "oko", "yarn.lock"))
	require.NoError(t, err)

	out, err := json.Marshal(struct {
		WithDev     bool            `json:"with_dev"`
		PackageJSON json.RawMessage `json:"package"`
		YarnLock    string          `json:"yarn_lock"`
	}{
		WithDev:     withDev,
		PackageJSON: pkgData,
		YarnLock:    string(lockData),
	})
	require.NoError(t, err)
	return out
}

func newSrv(t testing.TB) *server.Server {
	feedPath, err := filepath.Abs(filepath.Join("testdata", "{lang}-fixed-feed.json.gz"))
	require.NoError(t, err)

	manifestPath, err := filepath.Abs(filepath.Join("testdata", "manifest.json"))
	require.NoError(t, err)

	srv, err := server.New(config.Config{
		WithDev:         false,
		Debug:           true,
		FeedPath:        feedPath,
		WatcherCronSpec: "0 0 1 1 *",
		ManifestPath:    manifestPath,
	})
	require.NoError(t, err)
	return srv
}

func TestOkoPkgLock(t *testing.T) {
	body := bytes.NewReader(buildPkgLockReq(t, false))
	issues, err := newSrv(t).DoOko(context.Background(), body)
	require.NoError(t, err)

	found := false
	for _, issue := range issues {
		if issue.ID == "YADI-NODEJS-QS-10019" {
			found = true
			break
		}
	}

	require.True(t, found, "issue YADI-NODEJS-QS-10019 must exists")
}

func TestOkoYarnLock(t *testing.T) {
	body := bytes.NewReader(buildYarnLockReq(t, false))
	issues, err := newSrv(t).DoOko(context.Background(), body)
	require.NoError(t, err)

	found := false
	for _, issue := range issues {
		if issue.ID == "YADI-NODEJS-QS-10019" {
			found = true
			break
		}
	}

	require.True(t, found, "issue YADI-NODEJS-QS-10019 must exists")
}

func benchOkoPkgLock(b *testing.B, withDev bool) {
	simplelog.SetLevel(simplelog.WarnLevel)

	srv := newSrv(b)
	rawBody := buildPkgLockReq(b, withDev)
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_, err := srv.DoOko(context.Background(), bytes.NewReader(rawBody))
		require.NoError(b, err)
	}
}

func BenchmarkOkoPkgLock(b *testing.B) {
	benchOkoPkgLock(b, false)
}

func BenchmarkOkoPkgLockDev(b *testing.B) {
	benchOkoPkgLock(b, true)
}
