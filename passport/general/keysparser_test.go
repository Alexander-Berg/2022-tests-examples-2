package tvmcontext

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestParseKeys(t *testing.T) {
	keys, err := ParseKeys(getGoodKeys(t))
	if err != nil {
		t.Fatal(err)
	}

	// TODO(prime@): turn this back on, once protobuf upgrade is complete
	//if len(keys.XXX_unrecognized) != 0 {
	//	t.Fatal(errors.New("protobuf decoding error"))
	//}
	if l := len(keys.Bb); l != 10 {
		t.Fatalf("Unexpected bb keys count: %d", l)
	}
	if l := len(keys.Tvm); l != 2 {
		t.Fatalf("Unexpected tvm keys count: %d", l)
	}

	if _, err := ParseKeys("1:2:3"); err != ErrorInvalidKeysFormat {
		t.Fatalf("ParseKeys requires 2 fields: %s", err)
	}
	if _, err := ParseKeys("1"); err != ErrorInvalidKeysFormat {
		t.Fatalf("ParseKeys requires 2 fields: %s", err)
	}

	if _, err := ParseKeys("2:123123"); err != errorUnsupportedKeysVersion {
		t.Fatalf("ParseKeys supports only ver=1: %s", err)
	}
	if _, err := ParseKeys("1:1"); err != errorInvalidKeysBase64 {
		t.Fatalf("ParseKeys expects valid base64: %s", err)
	}

	if _, err := ParseKeys("1:aaaa"); err != ErrorInvalidKeysProtobuf {
		t.Fatalf("ParseKeys expects valid protobuf: %s", err)
	}
}

func TestCountourMismatch(t *testing.T) {
	err := checkKeyEnvironmentMismatch(16, 1000)
	require.EqualError(t, err, "You are trying to use tickets from 'unittest'-mode with keys from TVM-API production. Key id: 16")

	err = checkKeyEnvironmentMismatch(1000, 16)
	require.EqualError(t, err, "You are trying to use tickets from TVM-API production with keys from 'unittest'-mode. Key id: 1000")

	err = checkKeyEnvironmentMismatch(1000, 100000)
	require.NoError(t, err)

	err = checkKeyEnvironmentMismatch(16, 19)
	require.NoError(t, err)
}
