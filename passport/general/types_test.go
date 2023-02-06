package tvmtypes

import (
	"testing"

	"a.yandex-team.ru/library/go/yandex/tvm"
)

func TestBlackboxEnvToString(t *testing.T) {
	tst := func(e tvm.BlackboxEnv, expected string) {
		res := EnvToString(e)
		if res != expected {
			t.Fatalf("Unexpected str for end=%d: expected '%s', got '%s'", int(e), expected, res)
		}
	}
	tst(tvm.BlackboxProd, "Prod")
	tst(tvm.BlackboxTest, "Test")
	tst(tvm.BlackboxProdYateam, "ProdYaTeam")
	tst(tvm.BlackboxTestYateam, "TestYaTeam")
	tst(tvm.BlackboxStress, "Stress")
	tst(tvm.BlackboxEnv(5), "Unknown")
}
