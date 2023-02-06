package keystore_test

import (
	"fmt"
	"testing"
	"time"

	"github.com/stretchr/testify/require"
	"golang.org/x/crypto/ssh"

	"a.yandex-team.ru/security/skotty/robossh/internal/agentkey"
	"a.yandex-team.ru/security/skotty/robossh/internal/keystore"
	"a.yandex-team.ru/security/skotty/robossh/internal/testdata"
)

type TestKey struct {
	name string
	fp   string
	key  *agentkey.Key
}

var keys []TestKey

func init() {
	addKey := func(name string, key testdata.Key) {
		ak, err := agentkey.NewKey(key.AddedKey)
		if err != nil {
			panic(fmt.Sprintf("unable to create agentkey for test key %s: %v", name, err))
		}

		keys = append(keys, TestKey{
			name: name,
			fp:   ssh.FingerprintSHA256(key.Signer.PublicKey()),
			key:  ak,
		})
	}

	for t, k := range testdata.Keys {
		addKey(t, k)
	}

	for t, k := range testdata.SSHCertificates {
		addKey(t+"-cert", k)
	}
}

func TestKeystore(t *testing.T) {
	ks := keystore.NewStore()
	require.Zero(t, ks.Len())

	t.Run("add", func(t *testing.T) {
		for _, k := range keys {
			t.Run(k.name, func(t *testing.T) {
				require.True(t, ks.Add(k.key))
			})
		}

		require.Equal(t, len(keys), ks.Len())
	})

	t.Run("add_dup", func(t *testing.T) {
		for _, k := range keys {
			t.Run(k.name, func(t *testing.T) {
				require.False(t, ks.Add(k.key))
			})
		}

		require.Equal(t, len(keys), ks.Len())
	})

	t.Run("check", func(t *testing.T) {
		t.Run("get", func(t *testing.T) {
			for _, k := range keys {
				t.Run(k.name, func(t *testing.T) {
					key, ok := ks.Get(k.fp)
					require.True(t, ok)
					require.NotNil(t, key)
					require.Equal(t, k.fp, key.Fingerprint())
				})
			}
		})

		t.Run("range", func(t *testing.T) {
			expected := map[string]TestKey{}
			for _, k := range keys {
				expected[k.fp] = k
			}

			ks.Range(func(key *agentkey.Key) bool {
				delete(expected, key.Fingerprint())
				return true
			})

			require.Empty(t, expected)
		})
	})

	t.Run("range", func(t *testing.T) {
		t.Run("all", func(t *testing.T) {
			calls := 0
			ks.Range(func(_ *agentkey.Key) bool {
				calls++
				return true
			})
			require.Equal(t, len(keys), calls)
		})

		t.Run("first", func(t *testing.T) {
			calls := 0
			ks.Range(func(_ *agentkey.Key) bool {
				calls++
				return false
			})
			require.Equal(t, 1, calls)
		})
	})

}

func TestKeystoreRemove(t *testing.T) {
	ks := keystore.NewStore()
	require.Zero(t, ks.Len())

	t.Run("add", func(t *testing.T) {
		for _, k := range keys {
			t.Run(k.name, func(t *testing.T) {
				require.True(t, ks.Add(k.key))
			})
		}

		require.Equal(t, len(keys), ks.Len())
	})

	t.Run("remove", func(t *testing.T) {
		for _, k := range keys {
			t.Run(k.name, func(t *testing.T) {
				require.True(t, ks.Remove(k.fp))
			})
		}
	})

	t.Run("remove_not_exists", func(t *testing.T) {
		for _, k := range keys {
			t.Run(k.name, func(t *testing.T) {
				require.False(t, ks.Remove(k.fp))
			})
		}
	})
}

func TestKeystoreRemoveAll(t *testing.T) {
	ks := keystore.NewStore()
	require.Zero(t, ks.Len())

	t.Run("add", func(t *testing.T) {
		for _, k := range keys {
			t.Run(k.name, func(t *testing.T) {
				require.True(t, ks.Add(k.key))
			})
		}

		require.Equal(t, len(keys), ks.Len())
	})

	ks.RemoveAll()
	require.Zero(t, ks.Len())

	t.Run("check_not_exists", func(t *testing.T) {
		for _, k := range keys {
			t.Run(k.name, func(t *testing.T) {
				require.False(t, ks.Remove(k.fp))
			})
		}
	})
}

func TestKeystoreRemoveExpired(t *testing.T) {
	ks := keystore.NewStore()
	require.Zero(t, ks.Len())

	ak, err := agentkey.NewKey(testdata.Keys["ecdsa"].AddedKey)
	require.NoError(t, err)
	require.True(t, ks.Add(ak))

	expiredKey := testdata.Keys["ecdsap256"].AddedKey
	expiredKey.LifetimeSecs = 1
	ak, err = agentkey.NewKey(expiredKey)
	require.NoError(t, err)
	require.True(t, ks.Add(ak))

	require.Equal(t, 2, ks.Len())
	time.Sleep(2 * time.Second)

	require.Equal(t, 1, ks.RemoveExpired())
	require.Equal(t, 1, ks.Len())
}

func TestKeystoreRemoveExpired_single(t *testing.T) {
	ks := keystore.NewStore()
	require.Zero(t, ks.Len())

	expiredKey := testdata.Keys["ecdsap256"].AddedKey
	expiredKey.LifetimeSecs = 1
	ak, err := agentkey.NewKey(expiredKey)
	require.NoError(t, err)
	require.True(t, ks.Add(ak))

	require.Equal(t, 1, ks.Len())
	time.Sleep(2 * time.Second)

	require.Equal(t, 1, ks.RemoveExpired())
	require.Equal(t, 0, ks.Len())
}

func TestKeystoreRemoveExpired_reset(t *testing.T) {
	t.Run("decrease", func(t *testing.T) {
		ks := keystore.NewStore()
		require.Zero(t, ks.Len())

		ak, err := agentkey.NewKey(testdata.Keys["ecdsa"].AddedKey)
		require.NoError(t, err)
		require.True(t, ks.Add(ak))

		expiredKey := testdata.Keys["ecdsa"].AddedKey
		expiredKey.LifetimeSecs = 1
		ak, err = agentkey.NewKey(expiredKey)
		require.NoError(t, err)
		require.False(t, ks.Add(ak))

		require.Equal(t, 1, ks.Len())
		time.Sleep(2 * time.Second)

		require.Equal(t, 1, ks.RemoveExpired())
		require.Equal(t, 0, ks.Len())
	})

	t.Run("increase", func(t *testing.T) {
		ks := keystore.NewStore()
		require.Zero(t, ks.Len())

		expiredKey := testdata.Keys["ecdsa"].AddedKey
		expiredKey.LifetimeSecs = 1
		ak, err := agentkey.NewKey(expiredKey)
		require.NoError(t, err)
		require.True(t, ks.Add(ak))

		ak, err = agentkey.NewKey(testdata.Keys["ecdsa"].AddedKey)
		require.NoError(t, err)
		require.False(t, ks.Add(ak))

		require.Equal(t, 1, ks.Len())
		time.Sleep(2 * time.Second)

		require.Equal(t, 0, ks.RemoveExpired())
		require.Equal(t, 1, ks.Len())
	})
}
