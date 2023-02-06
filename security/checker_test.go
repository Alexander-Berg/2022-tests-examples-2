package passutil_test

import (
	"fmt"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/security/skotty/skotty/internal/passutil"
)

func TestIsAlphanumeric(t *testing.T) {
	ok := []string{
		"AAAZZZ",
		"aaazzz",
		"123kek999",
		"123",
	}

	notOK := []string{
		"AAA!ZZZ",
		"#AAAZZZ",
		"AAAZZZ#",
		"#AAAZZZ#",
		"#",
	}

	checker := passutil.IsAlphanumeric("tst")
	t.Run("ok", func(t *testing.T) {
		for _, tc := range ok {
			require.NoError(t, checker(tc))
		}
	})

	t.Run("not_ok", func(t *testing.T) {
		for _, tc := range notOK {
			require.Error(t, checker(tc))
		}
	})
}

func TestIsConsecutivelyRepeated(t *testing.T) {
	ok := []string{
		"kek",
		"1A123",
		"avbcd",
	}

	notOK := []string{
		"123",
		"abcd",
	}

	checker := passutil.IsConsecutivelyRepeated("tst")
	t.Run("ok", func(t *testing.T) {
		for _, tc := range ok {
			require.NoError(t, checker(tc))
		}
	})

	t.Run("not_ok", func(t *testing.T) {
		for _, tc := range notOK {
			require.Error(t, checker(tc))
		}
	})
}

func TestIsSame(t *testing.T) {
	ok := []string{
		"abcd",
		"123",
	}

	notOK := []string{
		"111",
		"aaaa",
		"ZZZZ",
		"WWWW",
	}

	checker := passutil.IsSame("tst")
	t.Run("ok", func(t *testing.T) {
		for _, tc := range ok {
			require.NoError(t, checker(tc))
		}
	})

	t.Run("not_ok", func(t *testing.T) {
		for _, tc := range notOK {
			require.Error(t, checker(tc))
		}
	})
}

func TestCheckPassword(t *testing.T) {
	cases := []struct {
		checks []passutil.PassChecker
		ok     []string
		notOK  []string
	}{
		{
			checks: []passutil.PassChecker{
				passutil.IsSame("tst"),
				passutil.IsConsecutivelyRepeated("tst"),
				passutil.IsAlphanumeric("tst"),
			},
			ok: []string{
				"01052022",
				"LoLKekCheburek",
			},
			notOK: []string{
				"12345678",
				"abcd",
				"aaa",
			},
		},
		{
			checks: []passutil.PassChecker{
				passutil.IsSame("tst"),
			},
			ok: []string{
				"01052022",
				"LoLKekCheburek",
				"12345678",
				"abcd",
			},
			notOK: []string{
				"aaa",
			},
		},
	}

	for i, tc := range cases {
		t.Run(fmt.Sprint(i), func(t *testing.T) {
			t.Run("ok", func(t *testing.T) {
				for _, pass := range tc.ok {
					t.Run(pass, func(t *testing.T) {
						require.NoError(t, passutil.CheckPassword(pass, tc.checks...))
					})
				}
			})

			t.Run("not_ok", func(t *testing.T) {
				for _, pass := range tc.notOK {
					t.Run(pass, func(t *testing.T) {
						require.Error(t, passutil.CheckPassword(pass, tc.checks...))
					})
				}
			})
		})
	}
}
