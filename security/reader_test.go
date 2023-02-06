package bob_test

import (
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/security/gideon/gideon/internal/tracer/bob"
)

func TestReader_ReadUint8(t *testing.T) {
	cases := map[string]struct {
		in  []byte
		out uint8
		err bool
	}{
		"2": {
			in:  []byte{0x02},
			out: 2,
			err: false,
		},
		"240": {
			in:  []byte{0xf0},
			out: 240,
			err: false,
		},
		"240_extra": {
			in:  []byte{0xf0, 0xf1},
			out: 240,
			err: false,
		},
		"empty": {
			in:  []byte{},
			err: true,
		},
	}

	for name, tc := range cases {
		t.Run(name, func(t *testing.T) {
			r := bob.NewReader(tc.in)
			if !tc.err {
				out, err := r.ReadUint8()
				require.NoError(t, err)
				require.Equal(t, tc.out, out)
			} else {
				out, err := r.ReadUint8()
				require.Zero(t, out)
				require.Error(t, err)
			}
		})
	}
}

func TestReader_ReadInt8(t *testing.T) {
	cases := map[string]struct {
		in  []byte
		out int8
		err bool
	}{
		"100": {
			in:  []byte{0x64},
			out: 100,
			err: false,
		},
		"100_extra": {
			in:  []byte{0x64, 0xf1},
			out: 100,
			err: false,
		},
		"-100": {
			in:  []byte{0x9c},
			out: -100,
			err: false,
		},
		"empty": {
			in:  []byte{},
			err: true,
		},
	}

	for name, tc := range cases {
		t.Run(name, func(t *testing.T) {
			r := bob.NewReader(tc.in)
			if !tc.err {
				out, err := r.ReadInt8()
				require.NoError(t, err)
				require.Equal(t, tc.out, out)
			} else {
				out, err := r.ReadInt8()
				require.Zero(t, out)
				require.Error(t, err)
			}
		})
	}
}

func TestReader_ReadUint16(t *testing.T) {
	cases := map[string]struct {
		in  []byte
		out uint16
		err bool
	}{
		"65530": {
			in:  []byte{0xfa, 0xff},
			out: 65530,
			err: false,
		},
		"65530_extra": {
			in:  []byte{0xfa, 0xff, 0xff},
			out: 65530,
			err: false,
		},
		"empty": {
			in:  []byte{},
			err: true,
		},
		"eof": {
			in:  []byte{0x00},
			err: true,
		},
	}

	for name, tc := range cases {
		t.Run(name, func(t *testing.T) {
			r := bob.NewReader(tc.in)
			if !tc.err {
				out, err := r.ReadUint16()
				require.NoError(t, err)
				require.Equal(t, tc.out, out)
			} else {
				out, err := r.ReadUint16()
				require.Zero(t, out)
				require.Error(t, err)
			}
		})
	}
}

func TestReader_ReadInt16(t *testing.T) {
	cases := map[string]struct {
		in  []byte
		out int16
		err bool
	}{
		"-32000": {
			in:  []byte{0x00, 0x83},
			out: -32000,
			err: false,
		},
		"32000": {
			in:  []byte{0x00, 0x7d},
			out: 32000,
			err: false,
		},
		"32000_extra": {
			in:  []byte{0x00, 0x7d, 0xff, 0xff, 0xff},
			out: 32000,
			err: false,
		},
		"empty": {
			in:  []byte{},
			err: true,
		},
		"eof": {
			in:  []byte{0x00},
			err: true,
		},
	}

	for name, tc := range cases {
		t.Run(name, func(t *testing.T) {
			r := bob.NewReader(tc.in)
			if !tc.err {
				out, err := r.ReadInt16()
				require.NoError(t, err)
				require.Equal(t, tc.out, out)
			} else {
				out, err := r.ReadInt16()
				require.Zero(t, out)
				require.Error(t, err)
			}
		})
	}
}

func TestReader_ReadUint32(t *testing.T) {
	cases := map[string]struct {
		in  []byte
		out uint32
		err bool
	}{
		"42e8": {
			in:  []byte{0x00, 0xea, 0x56, 0xfa},
			out: 42e8,
			err: false,
		},
		"42e8_extra": {
			in:  []byte{0x00, 0xea, 0x56, 0xfa, 0xff, 0xff},
			out: 42e8,
			err: false,
		},
		"empty": {
			in:  []byte{},
			err: true,
		},
		"one_byte": {
			in:  []byte{0x00},
			err: true,
		},
		"two_bytes": {
			in:  []byte{0x00, 0x01},
			err: true,
		},
		"three_bytes": {
			in:  []byte{0x00, 0x01, 0x02},
			err: true,
		},
	}

	for name, tc := range cases {
		t.Run(name, func(t *testing.T) {
			r := bob.NewReader(tc.in)
			if !tc.err {
				out, err := r.ReadUint32()
				require.NoError(t, err)
				require.Equal(t, tc.out, out)
			} else {
				out, err := r.ReadUint32()
				require.Zero(t, out)
				require.Error(t, err)
			}
		})
	}
}

func TestReader_ReadInt32(t *testing.T) {
	cases := map[string]struct {
		in  []byte
		out int32
		err bool
	}{
		"2e9": {
			in:  []byte{0x00, 0x94, 0x35, 0x77},
			out: 2e9,
			err: false,
		},
		"2e9_extra": {
			in:  []byte{0x00, 0x94, 0x35, 0x77, 0xff},
			out: 2e9,
			err: false,
		},
		"-2e9": {
			in:  []byte{0x00, 0x6c, 0xca, 0x88},
			out: -2e9,
			err: false,
		},
		"empty": {
			in:  []byte{},
			err: true,
		},
		"one_byte": {
			in:  []byte{0x00},
			err: true,
		},
		"two_bytes": {
			in:  []byte{0x00, 0x01},
			err: true,
		},
		"three_bytes": {
			in:  []byte{0x00, 0x01, 0x02},
			err: true,
		},
	}

	for name, tc := range cases {
		t.Run(name, func(t *testing.T) {
			r := bob.NewReader(tc.in)
			if !tc.err {
				out, err := r.ReadInt32()
				require.NoError(t, err)
				require.Equal(t, tc.out, out)
			} else {
				out, err := r.ReadInt32()
				require.Zero(t, out)
				require.Error(t, err)
			}
		})
	}
}

func TestReader_ReadUint64(t *testing.T) {
	cases := map[string]struct {
		in  []byte
		out uint64
		err bool
	}{
		"1e12": {
			in:  []byte{0x00, 0x10, 0xa5, 0xd4, 0xe8, 0x00, 0x00, 0x00},
			out: 1e12,
			err: false,
		},
		"1e12_extra": {
			in:  []byte{0x00, 0x10, 0xa5, 0xd4, 0xe8, 0x00, 0x00, 0x00, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff},
			out: 1e12,
			err: false,
		},
		"empty": {
			in:  []byte{},
			err: true,
		},
		"one_byte": {
			in:  []byte{0x00},
			err: true,
		},
		"two_bytes": {
			in:  []byte{0x00, 0x01},
			err: true,
		},
		"three_bytes": {
			in:  []byte{0x00, 0x01, 0x02},
			err: true,
		},
		"four_bytes": {
			in:  []byte{0x00, 0x01, 0x02, 0x03},
			err: true,
		},
		"five_bytes": {
			in:  []byte{0x00, 0x01, 0x02, 0x03, 0x04},
			err: true,
		},
		"six_bytes": {
			in:  []byte{0x00, 0x01, 0x02, 0x03, 0x04, 0x05},
			err: true,
		},
		"seven_bytes": {
			in:  []byte{0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06},
			err: true,
		},
	}

	for name, tc := range cases {
		t.Run(name, func(t *testing.T) {
			r := bob.NewReader(tc.in)
			if !tc.err {
				out, err := r.ReadUint64()
				require.NoError(t, err)
				require.Equal(t, tc.out, out)
			} else {
				out, err := r.ReadUint64()
				require.Zero(t, out)
				require.Error(t, err)
			}
		})
	}
}

func TestReader_ReadInt64(t *testing.T) {
	cases := map[string]struct {
		in  []byte
		out int64
		err bool
	}{
		"9e12": {
			in:  []byte{0x00, 0x90, 0xcd, 0x79, 0x2f, 0x08, 0x00, 0x00},
			out: 9e12,
			err: false,
		},
		"9e12_extra": {
			in:  []byte{0x00, 0x90, 0xcd, 0x79, 0x2f, 0x08, 0x00, 0x00, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff},
			out: 9e12,
			err: false,
		},
		"-9e12": {
			in:  []byte{0x00, 0x70, 0x32, 0x86, 0xd0, 0xf7, 0xff, 0xff},
			out: -9e12,
			err: false,
		},
		"empty": {
			in:  []byte{},
			err: true,
		},
		"one_byte": {
			in:  []byte{0x00},
			err: true,
		},
		"two_bytes": {
			in:  []byte{0x00, 0x01},
			err: true,
		},
		"three_bytes": {
			in:  []byte{0x00, 0x01, 0x02},
			err: true,
		},
		"four_bytes": {
			in:  []byte{0x00, 0x01, 0x02, 0x03},
			err: true,
		},
		"five_bytes": {
			in:  []byte{0x00, 0x01, 0x02, 0x03, 0x04},
			err: true,
		},
		"six_bytes": {
			in:  []byte{0x00, 0x01, 0x02, 0x03, 0x04, 0x05},
			err: true,
		},
		"seven_bytes": {
			in:  []byte{0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06},
			err: true,
		},
	}

	for name, tc := range cases {
		t.Run(name, func(t *testing.T) {
			r := bob.NewReader(tc.in)
			if !tc.err {
				out, err := r.ReadInt64()
				require.NoError(t, err)
				require.Equal(t, tc.out, out)
			} else {
				out, err := r.ReadInt64()
				require.Zero(t, out)
				require.Error(t, err)
			}
		})
	}
}

func TestReader_ReadBytes(t *testing.T) {
	cases := map[string]struct {
		in  []byte
		len int
		out []byte
		err bool
	}{
		"lol": {
			in: []byte{
				0x6c, 0x6f, 0x6c, // lol
			},
			len: 3,
			out: []byte("lol"),
			err: false,
		},
		"lol_extra": {
			in: []byte{
				0x6c, 0x6f, 0x6c, // lol
				0xff, 0xff, // some another data
			},
			len: 3,
			out: []byte("lol"),
			err: false,
		},
		"zero": {
			in: []byte{
				0xfa, 0xfb,
			},
			len: 0,
			out: nil,
			err: false,
		},
		"empty": {
			in:  []byte{},
			len: 0,
			out: nil,
			err: false,
		},
		"empty_eof": {
			in:  []byte{0xff},
			len: 2,
			err: true,
		},
		"one_byte_eof": {
			in:  []byte{0xff},
			len: 2,
			err: true,
		},
	}

	for name, tc := range cases {
		t.Run(name, func(t *testing.T) {
			r := bob.NewReader(tc.in)
			if !tc.err {
				out, err := r.ReadBytes(tc.len)
				require.NoError(t, err)
				require.Equal(t, tc.out, out)
			} else {
				out, err := r.ReadBytes(tc.len)
				require.Zero(t, out)
				require.Error(t, err)
			}
		})
	}
}

func TestReader_ReadByteSlice(t *testing.T) {
	cases := map[string]struct {
		in  []byte
		out []byte
		err bool
	}{
		"empty": {
			in: []byte{
				0x00, 0x00, // len
				0x6c, 0x6f, 0x6c, // some another data
			},
			out: nil,
			err: false,
		},
		"lol": {
			in: []byte{
				0x03, 0x00, // len
				0x6c, 0x6f, 0x6c, // lol
			},
			out: []byte("lol"),
			err: false,
		},
		"lol_extra": {
			in: []byte{
				0x03, 0x00, // len
				0x6c, 0x6f, 0x6c, // lol
				0xff, 0xff, // some another data
			},
			out: []byte("lol"),
			err: false,
		},
		"eof": {
			in:  []byte{},
			err: true,
		},
		"too_big": {
			in: []byte{
				0xff, 0xff, 0xff,
			},
			err: true,
		},
		"invalid_len": {
			in: []byte{
				0x02, 0x00, // len
				0xff,
			},
			err: true,
		},
	}

	for name, tc := range cases {
		t.Run(name, func(t *testing.T) {
			r := bob.NewReader(tc.in)
			if !tc.err {
				out, err := r.ReadByteSlice()
				require.NoError(t, err)
				require.Equal(t, tc.out, out)
			} else {
				out, err := r.ReadByteSlice()
				require.Zero(t, out)
				require.Error(t, err)
			}
		})
	}
}

func TestReader_ReadString(t *testing.T) {
	cases := map[string]struct {
		in  []byte
		out string
		err bool
	}{
		"empty": {
			in: []byte{
				0x00, 0x00, // len
				0x6c, 0x6f, 0x6c, // some another data
			},
			out: "",
			err: false,
		},
		"lol": {
			in: []byte{
				0x03, 0x00, // len
				0x6c, 0x6f, 0x6c, // lol
			},
			out: "lol",
			err: false,
		},
		"lol_extra": {
			in: []byte{
				0x03, 0x00, // len
				0x6c, 0x6f, 0x6c, // lol
				0xff, 0xff, // some another data
			},
			out: "lol",
			err: false,
		},
		"eof": {
			in:  []byte{},
			err: true,
		},
		"too_big": {
			in: []byte{
				0xff, 0xff, 0xff,
			},
			err: true,
		},
		"invalid_len": {
			in: []byte{
				0x02, 0x00, // len
				0xff,
			},
			err: true,
		},
	}

	for name, tc := range cases {
		t.Run(name, func(t *testing.T) {
			r := bob.NewReader(tc.in)
			if !tc.err {
				out, err := r.ReadString()
				require.NoError(t, err)
				require.Equal(t, tc.out, out)
			} else {
				out, err := r.ReadString()
				require.Zero(t, out)
				require.Error(t, err)
			}
		})
	}
}

func TestReader_ReadStreamFull(t *testing.T) {
	in := []byte{
		0xf0,                                           // uint8(240)
		0x00, 0x10, 0xa5, 0xd4, 0xe8, 0x00, 0x00, 0x00, // uint64(1e12),
		0x03, 0x00, 0x6c, 0x6f, 0x6c, // string("lol"),
		0xf1, 0xf2, 0xf3, // some bytes
	}

	r := bob.NewReader(in)

	u8, err := r.ReadUint8()
	require.NoError(t, err)
	require.Equal(t, uint8(240), u8)

	u64, err := r.ReadUint64()
	require.NoError(t, err)
	require.Equal(t, uint64(1e12), u64)

	s, err := r.ReadString()
	require.NoError(t, err)
	require.Equal(t, "lol", s)

	b, err := r.ReadBytes(3)
	require.NoError(t, err)
	require.Equal(t, []byte{0xf1, 0xf2, 0xf3}, b)
}

func TestReader_ReadStreamExtra(t *testing.T) {
	in := []byte{
		0xf0,                                           // uint8(240)
		0x00, 0x10, 0xa5, 0xd4, 0xe8, 0x00, 0x00, 0x00, // uint64(1e12),
		0x03, 0x00, 0x6c, 0x6f, 0x6c, // string("lol"),
		0xfa, 0xfb, // some another data
	}

	r := bob.NewReader(in)
	u8, err := r.ReadUint8()
	require.NoError(t, err)
	require.Equal(t, uint8(240), u8)

	u64, err := r.ReadUint64()
	require.NoError(t, err)
	require.Equal(t, uint64(1e12), u64)

	s, err := r.ReadString()
	require.NoError(t, err)
	require.Equal(t, "lol", s)

	rest, err := r.Rest()
	require.NoError(t, err)
	require.Equal(t, []byte{0xfa, 0xfb}, rest)
}
