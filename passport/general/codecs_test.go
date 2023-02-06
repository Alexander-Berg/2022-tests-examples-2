package tirole

import (
	"testing"

	"github.com/stretchr/testify/require"
)

var Brotli = mustDecodeBase64URL("GyMAAAR0Y6ku58ObclAQzDweUSUwbdqc5yOOKgI")
var Gzip = mustDecodeBase64URL("H4sIAAAAAAAA_yrOz01VKEstqkTGCpm5BflFJYl5JQpJOflJgAAAAP__MbeeiSQAAAA")
var Zstd = mustDecodeBase64URL("KLUv_QBY9AAAwHNvbWUgdmVyeSBpbXBvcnRhbnQgYmxvYgEAc-4IAQAA")
var EncodedText = "some veryveryveryvery important blob"

func TestGetCodec(t *testing.T) {
	cdc, err := getCodec("brotli")
	require.NoError(t, err)
	require.IsType(t, &brotliDecoder{}, cdc)

	cdc, err = getCodec("gzip")
	require.NoError(t, err)
	require.IsType(t, &gzipDecoder{}, cdc)

	cdc, err = getCodec("zstd")
	require.NoError(t, err)
	require.IsType(t, &zstdDecoder{}, cdc)

	_, err = getCodec("kek")
	require.EqualError(t, err, "unknown codec: 'kek'")
}

func TestBrotliDecode(t *testing.T) {
	d := brotliDecoder{}

	_, err := d.Decode(Gzip)
	require.Error(t, err)

	blob, err := d.Decode(Brotli)
	require.NoError(t, err)
	require.EqualValues(t, EncodedText, string(blob))
}

func TestGzipDecode(t *testing.T) {
	d := gzipDecoder{}

	_, err := d.Decode(Brotli)
	require.Error(t, err)

	blob, err := d.Decode(Gzip)
	require.NoError(t, err)
	require.EqualValues(t, EncodedText, string(blob))
}

func TestZstdDecode(t *testing.T) {
	d := zstdDecoder{}

	_, err := d.Decode(Brotli)
	require.Error(t, err)

	blob, err := d.Decode(Zstd)
	require.NoError(t, err)
	require.EqualValues(t, EncodedText, string(blob))
}
