package hashreader_test

import (
	"bytes"
	"encoding/hex"
	"fmt"
	"io"
	"testing"

	"github.com/stretchr/testify/require"
	"golang.org/x/crypto/blake2b"

	"a.yandex-team.ru/security/libs/go/hashreader"
)

func Test_hash(t *testing.T) {
	expected := []byte{'K', 'E', 'K'}

	hasher, err := hashreader.NewHashReader(bytes.NewReader(expected))
	require.NoError(t, err)

	var actual bytes.Buffer
	n, err := io.Copy(&actual, hasher)
	require.NoError(t, err)
	require.Equal(t, int(n), hasher.Size())
	require.Equal(t, expected, actual.Bytes())
	require.Equal(t, "45194e341c096a4598faad5bfa148d38e0ccea01c418f5b8cfcad311b1c06f88", hasher.Sum())
	require.Equal(t, "b2s:45194e341c096a4598faad5bfa148d38e0ccea01c418f5b8cfcad311b1c06f88", hasher.Hash())

	blake2Hash := blake2b.Sum256(expected)
	expectedBlake2Hash := fmt.Sprintf("b2s:%s", hex.EncodeToString(blake2Hash[:]))
	require.Equal(t, expectedBlake2Hash, hasher.Hash())
}

func Test_hashCustom(t *testing.T) {
	expected := []byte{'K', 'E', 'K'}

	hasher, err := hashreader.NewHashReader(bytes.NewReader(expected), hashreader.WithSha1Hash())
	require.NoError(t, err)

	var actual bytes.Buffer
	n, err := io.Copy(&actual, hasher)
	require.NoError(t, err)
	require.Equal(t, int(n), hasher.Size())
	require.Equal(t, expected, actual.Bytes())
	require.Equal(t, "2a4c23bfb79b5dabe474cb7b1b3e604645d6f9c6", hasher.Sum())
	require.Equal(t, "sha1:2a4c23bfb79b5dabe474cb7b1b3e604645d6f9c6", hasher.Hash())
}
