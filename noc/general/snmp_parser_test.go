package snmp

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestMacAddressDecode(t *testing.T) {
	as := assert.New(t)
	var tests = []struct {
		n      []byte // input
		exp    string // expected result
		expErr string // expected error
	}{
		{[]byte{1, 255, 1, 255, 1, 100}, "01:ff:01:ff:01:64", ""},
		{[]byte{1, 1}, "", "unexpected data len 2"},
	}
	for _, test := range tests {
		res, err := FormatMAC(test.n)
		if len(test.expErr) > 0 {
			as.EqualError(err, test.expErr, "test %s", test.n)
		} else {
			as.NoError(err, "test %s", test.n)
		}
		as.Equal(res, test.exp, "test %s", test.n)
	}
}

func TestIPAddressDecode(t *testing.T) {
	as := assert.New(t)
	var tests = []struct {
		n      []byte
		exp    string
		expErr string
	}{
		{[]byte{1, 2, 3, 254}, "1.2.3.254", ""},
		{[]byte{0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}, "::", ""},
		{[]byte{1, 1}, "", "unsupported ip len 2"},
	}
	for _, test := range tests {
		res, err := FormatIP(test.n)
		if len(test.expErr) > 0 {
			as.EqualError(err, test.expErr, "test %s", test.n)
		} else {
			as.NoError(err, "test %s", test.n)
		}
		as.Equal(res, test.exp, "test %s", test.n)
	}
}

func TestOctetStringToByte(t *testing.T) {
	as := assert.New(t)
	var tests = []struct {
		n      string
		exp    byte
		expErr string
	}{
		{"0", 0, ""},
		{"1", 1, ""},
		{"255", 255, ""},
		{"256", 0, "strconv.ParseUint: parsing \"256\": value out of range"},
		{"-1", 0, "strconv.ParseUint: parsing \"-1\": invalid syntax"},
	}
	for _, test := range tests {
		res, err := OctetStringToByte(test.n)
		if len(test.expErr) > 0 {
			as.EqualError(err, test.expErr, "test %s", test.n)
		} else {
			as.NoError(err, "test %s", test.n)
		}
		as.Equal(res, test.exp, "test %s", test.n)
	}
}

func TestOctetStringsPartToByte(t *testing.T) {
	as := assert.New(t)
	var tests = []struct {
		n      []string
		exp    []byte
		expErr string
	}{
		{[]string{"1", "2"}, []byte{1, 2}, ""},
		{[]string{"-11", "2"}, nil, "strconv.ParseUint: parsing \"-11\": invalid syntax"},
	}
	for _, test := range tests {
		res, err := OctetStringsPartToByte(test.n)
		if len(test.expErr) > 0 {
			as.EqualError(err, test.expErr, "test %s", test.n)
		} else {
			as.NoError(err, "test %s", test.n)
		}
		as.Equal(res, test.exp, "test %s", test.n)
	}
}

func TestParseUnsigned32(t *testing.T) {
	as := assert.New(t)
	var tests = []struct {
		n      string
		exp    uint32
		expErr string
	}{
		{"4294967295", 4294967295, ""},
		{"0", 0, ""},
		{"4294967296", 0, "strconv.ParseUint: parsing \"4294967296\": value out of range"},
	}
	for _, test := range tests {
		res, err := ParseUnsigned32(test.n)
		if len(test.expErr) > 0 {
			as.EqualError(err, test.expErr, "test %s", test.n)
		} else {
			as.NoError(err, "test %s", test.n)
		}
		as.Equal(res, test.exp, "test %s", test.n)
	}
}

func TestParseInteger32(t *testing.T) {
	as := assert.New(t)
	var tests = []struct {
		n      string
		exp    int32
		expErr string
	}{
		{"-2147483648", -2147483648, ""},
		{"0", 0, ""},
		{"2147483647", 2147483647, ""},
		{"-2147483649", 0, "strconv.ParseInt: parsing \"-2147483649\": value out of range"},
		{"2147483648", 0, "strconv.ParseInt: parsing \"2147483648\": value out of range"},
	}
	for _, test := range tests {
		res, err := ParseInteger32(test.n)
		if len(test.expErr) > 0 {
			as.EqualError(err, test.expErr, "test %s", test.n)
		} else {
			as.NoError(err, "test %s", test.n)
		}
		as.Equal(res, test.exp, "test %s", test.n)
	}
}
