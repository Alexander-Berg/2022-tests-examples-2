package agent

import (
	"fmt"
	"testing"
	"time"

	"github.com/stretchr/testify/require"
	"golang.org/x/crypto/ssh"
	"golang.org/x/crypto/ssh/agent"

	"a.yandex-team.ru/security/skotty/robossh/internal/keystore"
	"a.yandex-team.ru/security/skotty/robossh/internal/testdata"
)

func checkTestKeys(t *testing.T, keys ...testdata.Key) {
	for i, k := range keys {
		require.NotNil(t, k.PrivateKey, fmt.Sprintf("key_%d", i))
		require.NotNil(t, k.Signer, fmt.Sprintf("key_%d", i))
	}
}

func TestHandlerAdd(t *testing.T) {
	keys := []testdata.Key{
		testdata.Keys["ecdsa"],
		testdata.Keys["rsa-sha2-256"],
		testdata.SSHCertificates["rsa-sha2-256"],
	}

	checkTestKeys(t, keys...)
	h := &Handler{
		keys: keystore.NewStore(),
	}

	for _, k := range keys {
		t.Run("add-"+k.Comment, func(t *testing.T) {
			err := h.Add(k.AddedKey)
			require.NoError(t, err)
		})
	}

	t.Run("check", func(t *testing.T) {
		agentKeys, err := h.List()
		require.NoError(t, err)
		require.Len(t, agentKeys, len(keys))

		expectedKeys := make([]*agent.Key, len(keys))
		for i, k := range keys {
			expectedKeys[i] = &agent.Key{
				Format:  k.Signer.PublicKey().Type(),
				Blob:    k.Signer.PublicKey().Marshal(),
				Comment: k.Comment,
			}
		}

		require.EqualValues(t, expectedKeys, agentKeys)
	})

	for _, k := range keys {
		t.Run("add-dup-"+k.Comment, func(t *testing.T) {
			err := h.Add(k.AddedKey)
			require.NoError(t, err)
		})
	}

	// must be a same keys after adding duplicated
	t.Run("check", func(t *testing.T) {
		agentKeys, err := h.List()
		require.NoError(t, err)
		require.Len(t, agentKeys, len(keys))
	})
}

func TestHandlerSign(t *testing.T) {
	keys := []testdata.Key{
		testdata.Keys["ecdsa"],
		testdata.Keys["rsa-sha2-256"],
		testdata.SSHCertificates["rsa-sha2-256"],
	}

	checkTestKeys(t, keys...)
	h := &Handler{
		keys: keystore.NewStore(),
	}

	for _, k := range keys {
		t.Run("add-"+k.Comment, func(t *testing.T) {
			err := h.Add(k.AddedKey)
			require.NoError(t, err)
		})
	}

	t.Run("check", func(t *testing.T) {
		agentKeys, err := h.List()
		require.NoError(t, err)
		require.Len(t, agentKeys, len(keys))

		for _, k := range agentKeys {
			agentKey := k
			t.Run(agentKey.Comment, func(t *testing.T) {
				buf := []byte("kek")
				t.Run("Sign", func(t *testing.T) {
					sig, err := h.Sign(agentKey, buf)
					require.NoError(t, err)

					err = agentKey.Verify(buf, sig)
					require.NoError(t, err)
				})

				switch agentKey.Format {
				case ssh.KeyAlgoRSA, ssh.CertAlgoRSAv01:
					t.Run("SignWithFlags", func(t *testing.T) {
						t.Run("sha256", func(t *testing.T) {
							sig, err := h.SignWithFlags(agentKey, buf, agent.SignatureFlagRsaSha256)
							require.NoError(t, err)

							require.Equal(t, ssh.KeyAlgoRSASHA256, sig.Format)
							err = agentKey.Verify(buf, sig)
							require.NoError(t, err)
						})

						t.Run("sha512", func(t *testing.T) {
							sig, err := h.SignWithFlags(agentKey, buf, agent.SignatureFlagRsaSha512)
							require.NoError(t, err)

							require.Equal(t, ssh.KeyAlgoRSASHA512, sig.Format)
							err = agentKey.Verify(buf, sig)
							require.NoError(t, err)
						})
					})
				default:
					t.Run("SignWithFlags", func(t *testing.T) {
						t.Run("zero", func(t *testing.T) {
							sig, err := h.SignWithFlags(agentKey, buf, 0)
							require.NoError(t, err)

							err = agentKey.Verify(buf, sig)
							require.NoError(t, err)
						})

						t.Run("sha256", func(t *testing.T) {
							sig, err := h.SignWithFlags(agentKey, buf, agent.SignatureFlagRsaSha256)
							require.Error(t, err)
							require.Nil(t, sig)
						})

						t.Run("sha512", func(t *testing.T) {
							sig, err := h.SignWithFlags(agentKey, buf, agent.SignatureFlagRsaSha512)
							require.Error(t, err)
							require.Nil(t, sig)
						})
					})
				}
			})
		}
	})
}

func TestHandlerExtension(t *testing.T) {
	h := &Handler{
		keys: keystore.NewStore(),
	}

	rsp, err := h.Extension("kek", []byte("cheburek"))
	require.Empty(t, rsp)
	require.Equal(t, agent.ErrExtensionUnsupported, err)
}

func TestHandlerSigners(t *testing.T) {
	h := &Handler{
		keys: keystore.NewStore(),
	}

	rsp, err := h.Signers()
	require.Empty(t, rsp)
	require.Error(t, err)
}

func TestHandlerRemove(t *testing.T) {
	keys := []testdata.Key{
		testdata.Keys["ecdsa"],
		testdata.Keys["rsa-sha2-256"],
		testdata.SSHCertificates["rsa-sha2-256"],
	}

	checkTestKeys(t, keys...)
	h := &Handler{
		keys: keystore.NewStore(),
	}

	for _, k := range keys {
		t.Run("add-"+k.Comment, func(t *testing.T) {
			err := h.Add(k.AddedKey)
			require.NoError(t, err)
		})
	}

	t.Run("check", func(t *testing.T) {
		agentKeys, err := h.List()
		require.NoError(t, err)
		require.Len(t, agentKeys, len(keys))

		expectedKeys := make([]*agent.Key, len(keys))
		for i, k := range keys {
			expectedKeys[i] = &agent.Key{
				Format:  k.Signer.PublicKey().Type(),
				Blob:    k.Signer.PublicKey().Marshal(),
				Comment: k.Comment,
			}
		}

		require.EqualValues(t, expectedKeys, agentKeys)

		t.Run("valid", func(t *testing.T) {
			for _, key := range agentKeys {
				t.Run(key.Comment, func(t *testing.T) {
					err := h.Remove(key)
					require.NoError(t, err)
				})
			}
		})

		t.Run("check_empty", func(t *testing.T) {
			agentKeys, err := h.List()
			require.NoError(t, err)
			require.Empty(t, agentKeys)
		})

		t.Run("invalid", func(t *testing.T) {
			for _, key := range agentKeys {
				t.Run(key.Comment, func(t *testing.T) {
					err := h.Remove(key)
					require.Error(t, err)
				})
			}
		})
	})
}

func TestHandlerRemoveAll(t *testing.T) {
	keys := []testdata.Key{
		testdata.Keys["ecdsa"],
		testdata.Keys["rsa-sha2-256"],
		testdata.SSHCertificates["rsa-sha2-256"],
	}

	checkTestKeys(t, keys...)
	h := &Handler{
		keys: keystore.NewStore(),
	}

	for _, k := range keys {
		t.Run("add-"+k.Comment, func(t *testing.T) {
			err := h.Add(k.AddedKey)
			require.NoError(t, err)
		})
	}

	t.Run("check", func(t *testing.T) {
		agentKeys, err := h.List()
		require.NoError(t, err)
		require.Len(t, agentKeys, len(keys))

		expectedKeys := make([]*agent.Key, len(keys))
		for i, k := range keys {
			expectedKeys[i] = &agent.Key{
				Format:  k.Signer.PublicKey().Type(),
				Blob:    k.Signer.PublicKey().Marshal(),
				Comment: k.Comment,
			}
		}

		require.EqualValues(t, expectedKeys, agentKeys)
	})

	err := h.RemoveAll()
	require.NoError(t, err)

	agentKeys, err := h.List()
	require.NoError(t, err)
	require.Empty(t, agentKeys)
}

func TestHandlerLockUnlock(t *testing.T) {
	h := &Handler{
		keys: keystore.NewStore(),
	}

	err := h.Add(testdata.SSHCertificates["rsa-sha2-256"].AddedKey)
	require.NoError(t, err)

	agentKeys, err := h.List()
	require.NoError(t, err)
	require.Len(t, agentKeys, 1)
	existedKey := agentKeys[0]

	passphrase := []byte("lol")
	err = h.Lock(passphrase)
	require.NoError(t, err)

	err = h.Lock(passphrase)
	require.Error(t, err, "already locked agent must fail")

	err = h.Unlock([]byte("kek"))
	require.Error(t, err, "unlock w/ invalid passphrase must fail")

	agentKeys, err = h.List()
	require.NoError(t, err)
	require.Empty(t, agentKeys, "locked agent List will empty an empty list.")

	err = h.Add(testdata.Keys["rsa-sha2-256"].AddedKey)
	require.Error(t, err, "locked agent must not accept new keys")

	err = h.Remove(existedKey)
	require.Error(t, err, "locked agent must not remove any keys")

	err = h.RemoveAll()
	require.Error(t, err, "locked agent can't be cleared")

	_, err = h.Sign(existedKey, []byte("data"))
	require.Error(t, err, "locked agent can't sign anything")

	_, err = h.SignWithFlags(existedKey, []byte("data"), 0)
	require.Error(t, err, "locked agent can't sign anything")

	err = h.Unlock(passphrase)
	require.NoError(t, err)

	agentKeys, err = h.List()
	require.NoError(t, err)
	require.Len(t, agentKeys, 1)

	err = h.Add(testdata.Keys["rsa-sha2-256"].AddedKey)
	require.NoError(t, err)

	agentKeys, err = h.List()
	require.NoError(t, err)
	require.Len(t, agentKeys, 2)
	lastAgentKey := agentKeys[1]

	_, err = h.Sign(existedKey, []byte("data"))
	require.NoError(t, err)

	_, err = h.SignWithFlags(existedKey, []byte("data"), 0)
	require.NoError(t, err)

	err = h.Remove(existedKey)
	require.NoError(t, err)

	_, err = h.Sign(lastAgentKey, []byte("data"))
	require.NoError(t, err)

	_, err = h.SignWithFlags(lastAgentKey, []byte("data"), 0)
	require.NoError(t, err)
}

func TestHandlerExpires(t *testing.T) {
	h := &Handler{
		keys: keystore.NewStore(),
	}

	checkList := func(counts int) {
		agentKeys, err := h.List()
		require.NoError(t, err)
		require.Len(t, agentKeys, counts)
	}

	require.NoError(t, h.Add(testdata.Keys["ecdsa"].AddedKey))
	expiredKey := testdata.Keys["rsa-sha2-256"].AddedKey
	expiredKey.LifetimeSecs = 1
	require.NoError(t, h.Add(expiredKey))

	checkList(2)
	time.Sleep(5 * time.Second)
	checkList(1)
}
