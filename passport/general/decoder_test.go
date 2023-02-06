package tirole

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestDecode(t *testing.T) {
	blob, err := decode([]byte("kek"), "")
	require.NoError(t, err)
	require.EqualValues(t, "kek", string(blob))

	_, err = decode([]byte("kek"), "lol")
	require.EqualError(t, err, "failed to parse codec info from tirole: 'lol'. unknown codec format version; known: 1")

	_, err = decode([]byte("kek"), `1:lol:98:2B0236B8E83B41F1ABD9042406A42D7E6728644904550ED914380FEA95F2F529`)
	require.EqualError(t, err, "failed to get codec for roles from tirole: '1:lol:98:2B0236B8E83B41F1ABD9042406A42D7E6728644904550ED914380FEA95F2F529'. unknown codec: 'lol'")

	_, err = decode([]byte("kek"), `1:brotli:42:2B0236B8E83B41F1ABD9042406A42D7E6728644904550ED914380FEA95F2F529`)
	require.Error(t, err)
	require.Contains(t, err.Error(), "failed to decode roles from tirole: '1:brotli:42:2B0236B8E83B41F1ABD9042406A42D7E6728644904550ED914380FEA95F2F529'. brotli:")

	_, err = decode(ValidRolesBlob, `1:brotli:42:2B0236B8E83B41F1ABD9042406A42D7E6728644904550ED914380FEA95F2F529`)
	require.EqualError(t, err, "decoded size is unexpected: actual=98 vs expected=42")

	blob, err = decode(ValidRolesBlob, ValidRolesCodec)
	require.NoError(t, err)
	require.EqualValues(t, ValidRoles, string(blob))
}

func TestParseCodecInfo(t *testing.T) {
	type Case struct {
		name string
		in   string
		out  *codecInfo
		err  string
	}
	cases := []Case{
		{
			name: "empty codec",
			err:  "unknown codec format version; known: 1",
		},
		{
			name: "bad version",
			in:   "2",
			err:  "unknown codec format version; known: 1",
		},
		{
			name: "inllegal fields count",
			in:   "1:foo",
			err:  "malformed codec",
		},
		{
			name: "bad decoded size",
			in:   "1:foo:asd:keko",
			err:  "decoded blob size is not number",
		},
		{
			name: "bad sha256 format",
			in:   "1:foo:123:keko",
			err:  "sha256 of decoded blob has invalid length: expected 64, got 4",
		},
		{
			name: "correct",
			in:   ValidRolesCodec,
			out: &codecInfo{
				Type:   "brotli",
				Size:   98,
				Sha256: "2B0236B8E83B41F1ABD9042406A42D7E6728644904550ED914380FEA95F2F529",
			},
		},
	}

	for _, c := range cases {
		info, err := parseCodecInfo(c.in)

		if c.err == "" {
			require.NoError(t, err, c.name)
			require.EqualValues(t, c.out, info, c.name)
		} else {
			require.EqualError(t, err, c.err, c.name)
			require.Nil(t, info)
		}
	}
}

func TestVerifyDecodedResult(t *testing.T) {
	require.EqualError(t,
		verifyDecodedResult([]byte("kek"), &codecInfo{Size: 17}),
		"decoded size is unexpected: actual=3 vs expected=17",
	)
	require.EqualError(t,
		verifyDecodedResult([]byte("kek"), &codecInfo{Size: 3, Sha256: "ASDF"}),
		"decoded blob has bad sha256: expected=asdf, actual=b794385f2d1ef7ab4d9273d1906381b44f2f6f2588a3efb96a49188331984753",
	)
	require.NoError(t,
		verifyDecodedResult([]byte("kek"), &codecInfo{Size: 3, Sha256: "B794385F2d1ef7ab4d9273d1906381b44f2f6f2588a3efb96a49188331984753"}),
	)
}

func TestVerifySize(t *testing.T) {
	require.EqualError(t,
		verifySize([]byte("kek"), 17),
		"decoded size is unexpected: actual=3 vs expected=17",
	)
	require.NoError(t, verifySize([]byte("kek"), 3))
}

func TestVerifySha256(t *testing.T) {
	require.EqualError(t,
		verifySha256([]byte("kek"), "asd"),
		"decoded blob has bad sha256: expected=asd, actual=b794385f2d1ef7ab4d9273d1906381b44f2f6f2588a3efb96a49188331984753",
	)
	require.NoError(t,
		verifySha256([]byte("kek"),
			"b794385f2d1ef7ab4d9273d1906381b44f2f6f2588a3efb96a49188331984753"),
	)
}
