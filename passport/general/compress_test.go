package compressor

import (
	"encoding/base64"
	"testing"

	"github.com/stretchr/testify/require"
)

func TestDecompress(t *testing.T) {
	type TestCase struct {
		Decoded string
		Encoded map[CompressionCodecType]string
	}

	// Сжатые данные получены утилитами для сжатия из daemon/lbchdb (C++):
	cases := []TestCase{
		{
			Decoded: "",
			Encoded: map[CompressionCodecType]string{
				GZip:   "H4sIAAAAAAAAAwMAAAAAAAAAAAA=",
				Brotli: "awAD",
				ZStd:   "KLUv/SAAAQAA",
			},
		},
		{
			Decoded: "some string to compress",
			Encoded: map[CompressionCodecType]string{
				GZip:   "H4sIAAAAAAAAAyvOz01VKC4pysxLVyjJV0jOzy0oSi0uBgDd3n7BFwAAAA==",
				Brotli: "CwsAAARUOdKyL8Ol8Bcrs1TGOVd65iXOMQAD",
				ZStd:   "KLUv/QBYuQAAc29tZSBzdHJpbmcgdG8gY29tcHJlc3M=",
			},
		},
		{
			Decoded: "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
			Encoded: map[CompressionCodecType]string{
				GZip:   "H4sIAAAAAAAAA0tMpB4AAEeAUz5MAAAA",
				Brotli: "iyUAACTCArFAigED",
				ZStd:   "KLUv/QBYRQAAEGFhAQCHAiw=",
			},
		},
	}

	for _, testCase := range cases {
		for codec, encoded := range testCase.Encoded {
			compressed, err := base64.StdEncoding.DecodeString(encoded)
			require.NoError(t, err, testCase.Decoded, codec)

			decompressed, err := Decompress(uint64(len(testCase.Decoded)), compressed, codec)
			require.NoError(t, err, testCase.Decoded, codec)

			require.Equal(t, testCase.Decoded, string(decompressed), codec)
		}
	}
}

func TestCompress(t *testing.T) {
	for _, str := range []string{"", "some string to compress", "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"} {
		for _, codec := range []CompressionCodecType{GZip, Brotli, ZStd} {
			compressed, err := Compress([]byte(str), codec)
			require.NoError(t, err, str, codec)

			decompressed, err := Decompress(uint64(len(str)), compressed, codec)
			require.NoError(t, err, str, codec)

			require.Equal(t, str, string(decompressed), codec)
		}
	}
}
