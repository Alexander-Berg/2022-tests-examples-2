package sshagent_test

import (
	"errors"
	"testing"

	"github.com/stretchr/testify/require"
	"go.uber.org/zap/zaptest"
	"golang.org/x/crypto/ssh"
	"golang.org/x/crypto/ssh/agent"

	"a.yandex-team.ru/library/go/core/log/zap"
	"a.yandex-team.ru/security/skotty/libs/sshagent"
)

var _ agent.ExtendedAgent = (*CountedHandler)(nil)

type CountedHandler struct {
	RetErr             error
	ListCalls          int
	SignCalls          int
	AddCalls           int
	RemoveCalls        int
	RemoveAllCalls     int
	LockCalls          int
	UnlockCalls        int
	SignersCalls       int
	SignWithFlagsCalls int
	ExtensionCalls     int
}

func (h *CountedHandler) List() ([]*agent.Key, error) {
	h.ListCalls++
	return nil, h.RetErr
}

func (h *CountedHandler) Sign(_ ssh.PublicKey, _ []byte) (*ssh.Signature, error) {
	h.SignCalls++
	return nil, h.RetErr
}

func (h *CountedHandler) Add(_ agent.AddedKey) error {
	h.AddCalls++
	return h.RetErr
}

func (h *CountedHandler) Remove(_ ssh.PublicKey) error {
	h.RemoveCalls++
	return h.RetErr
}

func (h *CountedHandler) RemoveAll() error {
	h.RemoveAllCalls++
	return h.RetErr
}

func (h *CountedHandler) Lock(_ []byte) error {
	h.LockCalls++
	return h.RetErr
}

func (h *CountedHandler) Unlock(_ []byte) error {
	h.UnlockCalls++
	return h.RetErr
}

func (h *CountedHandler) SignWithFlags(_ ssh.PublicKey, _ []byte, _ agent.SignatureFlags) (*ssh.Signature, error) {
	h.SignWithFlagsCalls++
	return nil, h.RetErr
}

func (h *CountedHandler) Extension(_ string, _ []byte) ([]byte, error) {
	h.ExtensionCalls++
	return nil, h.RetErr
}

func (h *CountedHandler) Signers() ([]ssh.Signer, error) {
	h.SignersCalls++
	return nil, h.RetErr
}

func TestHandlerLog(t *testing.T) {
	testHandler := func(t *testing.T, expectedErr error) {
		ch := &CountedHandler{
			RetErr: expectedErr,
		}
		h := &sshagent.LoggableHandler{
			Handler: ch,
			Log:     &zap.Logger{L: zaptest.NewLogger(t)},
		}

		t.Run("List", func(t *testing.T) {
			_, err := h.List()
			require.Equal(t, expectedErr, err)
			require.Equal(t, 1, ch.ListCalls)
		})

		t.Run("Sign", func(t *testing.T) {
			_, err := h.Sign(nil, nil)
			require.Equal(t, expectedErr, err)
			require.Equal(t, 1, ch.SignCalls)
		})

		t.Run("Add", func(t *testing.T) {
			err := h.Add(agent.AddedKey{})
			require.Equal(t, expectedErr, err)
			require.Equal(t, 1, ch.AddCalls)
		})

		t.Run("Remove", func(t *testing.T) {
			err := h.Remove(nil)
			require.Equal(t, expectedErr, err)
			require.Equal(t, 1, ch.RemoveCalls)
		})

		t.Run("RemoveAll", func(t *testing.T) {
			err := h.RemoveAll()
			require.Equal(t, expectedErr, err)
			require.Equal(t, 1, ch.RemoveAllCalls)
		})

		t.Run("Lock", func(t *testing.T) {
			err := h.Lock(nil)
			require.Equal(t, expectedErr, err)
			require.Equal(t, 1, ch.LockCalls)
		})

		t.Run("Unlock", func(t *testing.T) {
			err := h.Unlock(nil)
			require.Equal(t, expectedErr, err)
			require.Equal(t, 1, ch.UnlockCalls)
		})

		t.Run("Signers", func(t *testing.T) {
			_, err := h.Signers()
			require.Equal(t, expectedErr, err)
			require.Equal(t, 1, ch.SignersCalls)
		})

		t.Run("SignWithFlags", func(t *testing.T) {
			_, err := h.SignWithFlags(nil, nil, 0)
			require.Equal(t, expectedErr, err)
			require.Equal(t, 1, ch.SignWithFlagsCalls)
		})

		t.Run("Extension", func(t *testing.T) {
			_, err := h.Extension("", nil)
			require.Equal(t, expectedErr, err)
			require.Equal(t, 1, ch.ExtensionCalls)
		})
	}

	t.Run("wo_err", func(t *testing.T) {
		testHandler(t, nil)
	})

	t.Run("w_err", func(t *testing.T) {
		testHandler(t, errors.New("some err"))
	})
}
