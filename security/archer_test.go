package archer_test

import (
	"io"
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/security/libs/go/archer"
)

func TestWalkers_ok(t *testing.T) {
	type TestCase struct {
		filename string
		once     bool
		patterns []archer.WalkPattern
	}

	cases := []string{
		"testdata.zip",
		"testdata.whl",
		"testdata.egg",
		"testdata.tar",
		"testdata.tar.gz",
		"testdata.tgz",
		"testdata.tar.bz2",
		"testdata.tbz",
		"testdata.tbz2",
	}

	patterns := []archer.WalkPattern{
		{
			ID:      0,
			Marker:  "test",
			Pattern: "lol/kek/*.test",
		},
		{
			ID:      1,
			Marker:  "lala",
			Pattern: "test.lala",
		},
	}

	tester := func(tc TestCase) func(t *testing.T) {
		return func(t *testing.T) {
			walker, err := archer.WalkerFor(tc.filename)
			require.NoError(t, err)

			patternsCount := map[int]int{}
			err = walker.FileWalk(
				tc.filename,
				archer.FileWalkOpts{
					Once:     tc.once,
					Patterns: tc.patterns,
				},
				func(targetPath string, patternID int, reader archer.SizeReader) error {
					patternsCount[patternID]++

					switch patternID {
					case 0:
						switch targetPath {
						case "lol/kek/cheburek.test":
							out, err := io.ReadAll(reader)
							require.NoError(t, err)
							require.Equal(t, "cheburek\n", string(out))
						case "lol/kek/lala.test":
							out, err := io.ReadAll(reader)
							require.NoError(t, err)
							require.Equal(t, "lala\n", string(out))
						default:
							require.Fail(t, "unknown target %q for pattern %d", targetPath, patternID)
						}
					case 1:
						require.Equal(t, "test.lala", targetPath)
						out, err := io.ReadAll(reader)
						require.NoError(t, err)
						require.Equal(t, "lala\n", string(out))
					default:
						require.Fail(t, "unknown pattern: %d", patternID)
					}
					return nil
				},
			)

			require.NoError(t, err)
			if tc.once {
				for patternID, calls := range patternsCount {
					require.Equal(t, 1, calls, "pattern %d called more than one time", patternID)
				}
			}
		}
	}

	for _, tc := range cases {
		t.Run(tc+"_all", tester(TestCase{
			filename: filepath.Join("./arches/", tc),
			once:     false,
			patterns: patterns,
		}))

		t.Run(tc+"_once", tester(TestCase{
			filename: filepath.Join("./arches/", tc),
			once:     true,
			patterns: patterns,
		}))
	}
}

func TestWalkers_stoppable(t *testing.T) {
	type TestCase struct {
		filename string
		patterns []archer.WalkPattern
	}

	cases := []string{
		"testdata.zip",
		"testdata.whl",
		"testdata.egg",
		"testdata.tar",
		"testdata.tar.gz",
		"testdata.tgz",
		"testdata.tar.bz2",
		"testdata.tbz",
		"testdata.tbz2",
	}

	patterns := []archer.WalkPattern{
		{
			ID:      0,
			Marker:  "test",
			Pattern: "lol/kek/*.test",
		},
	}

	tester := func(tc TestCase) func(t *testing.T) {
		return func(t *testing.T) {
			walker, err := archer.WalkerFor(tc.filename)
			require.NoError(t, err)

			patternsCount := map[int]int{}
			err = walker.FileWalk(
				tc.filename,
				archer.FileWalkOpts{
					Once:     false,
					Patterns: tc.patterns,
				},
				func(targetPath string, patternID int, reader archer.SizeReader) error {
					patternsCount[patternID]++
					return archer.ErrStop
				},
			)

			require.NoError(t, err)
			for patternID, calls := range patternsCount {
				require.Equal(t, 1, calls, "pattern %d called more than one time", patternID)
			}
		}
	}

	for _, tc := range cases {
		t.Run(tc, tester(TestCase{
			filename: filepath.Join("./arches/", tc),
			patterns: patterns,
		}))

	}
}

func TestWalkers_errs(t *testing.T) {
	cases := []string{
		"lol.kek",
		"cheburek.tar.blah",
	}

	for _, tc := range cases {
		t.Run(tc, func(t *testing.T) {
			walker, err := archer.WalkerFor(tc)
			require.EqualError(t, err, "unknown archive format")
			require.Nil(t, walker)
		})

	}
}
