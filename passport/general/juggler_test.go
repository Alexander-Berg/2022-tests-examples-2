package juggler

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestNewStatus(t *testing.T) {
	s := NewStatus(Critical, "asdf %d fdsa", 435)
	require.Equal(t, "2;asdf 435 fdsa", s.String())
	s = NewStatus(Ok, "OK")
	require.Equal(t, NewStatusOk().String(), s.String())
	s = NewStatus(Warning, "Keys are about to expire (%v): %s", []string{"key1", "key2", "key3"}, "something")
	require.Equal(t, "1;Keys are about to expire ([key1 key2 key3]): something", s.String())
}

func TestStatus_Update(t *testing.T) {
	s := NewStatusOk()
	s.Update(NewStatus(Warning, "asdf%d", 1))
	require.Equal(t, "1;asdf1", s.String())
	s.Update(NewStatus(Warning, "asdf%d", 2))
	require.Equal(t, "1;asdf2", s.String())
	s.Update(NewStatus(Ok, "asdf%d", 3))
	require.Equal(t, "1;asdf2", s.String())
	s.Update(NewStatus(Critical, "asdf%d", 4))
	require.Equal(t, "2;asdf4", s.String())
	s.Update(NewStatus(Warning, "asdf%d", 5))
	require.Equal(t, "2;asdf4", s.String())
	s.Update(NewStatus(Ok, "asdf%d", 6))
	require.Equal(t, "2;asdf4", s.String())
}
