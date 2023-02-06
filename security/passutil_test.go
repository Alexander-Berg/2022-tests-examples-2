package passutil

import (
	"math/rand"
	"reflect"
	"runtime"
	"strings"
	"testing"

	"github.com/stretchr/testify/require"
)

func TestPassword(t *testing.T) {
	tests := []func(t *testing.T){
		testPasswordWithCharset,
		testPassword,
		testPIN,
	}

	oldRand := randInt
	randInt = func(max int64) (int64, error) {
		return rand.Int63n(max), nil
	}

	for _, tc := range tests {
		t.Run(funcName(tc), tc)
	}

	randInt = oldRand
}

func funcName(fn func(t *testing.T)) string {
	name := runtime.FuncForPC(reflect.ValueOf(fn).Pointer()).Name()
	if idx := strings.LastIndexByte(name, '.'); idx > 0 {
		return name[idx+1:]
	}

	return name
}

func testPasswordWithCharset(t *testing.T) {
	cases := []struct {
		len  int
		pass string
	}{
		{
			len:  1,
			pass: "b",
		},
		{
			len:  6,
			pass: "adccdb",
		},
		{
			len:  18,
			pass: "abcaadcabdddaccbcc",
		},
	}

	rand.Seed(0)
	for _, tc := range cases {
		t.Run(tc.pass, func(t *testing.T) {
			pass, err := PasswordWithCharset(tc.len, "abcd")
			require.NoError(t, err)
			require.Equal(t, tc.pass, pass)
		})
	}
}

func testPassword(t *testing.T) {
	cases := []struct {
		len  int
		pass string
	}{
		{
			len:  1,
			pass: "h",
		},
		{
			len:  6,
			pass: "ehwu7Z",
		},
		{
			len:  18,
			pass: "GXyQSroCrRTVOOk3GI",
		},
	}

	rand.Seed(0)
	for _, tc := range cases {
		t.Run(tc.pass, func(t *testing.T) {
			pass, err := Password(tc.len)
			require.NoError(t, err)
			require.Equal(t, tc.pass, pass)
		})
	}
}

func testPIN(t *testing.T) {
	cases := []struct {
		len  int
		pass string
	}{
		{
			len:  1,
			pass: "5",
		},
		{
			len:  6,
			pass: "274233",
		},
		{
			len:  18,
			pass: "696689809519866906",
		},
	}

	rand.Seed(0)
	for _, tc := range cases {
		t.Run(tc.pass, func(t *testing.T) {
			pass, err := PIN(tc.len)
			require.NoError(t, err)
			require.Equal(t, tc.pass, pass)
		})
	}
}
