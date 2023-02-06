package versions

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestParseDpkgLine(t *testing.T) {
	cfg := map[string]interface{}{
		"yandex-passport-blackbox":            nil,
		"passport-sezam-front-fastcgi-config": nil,
	}

	type resType struct {
		pkg   string
		ver   string
		found bool
	}

	res := map[string]resType{
		"ii  yandex-passport-blackbox-grants-checker         1.0.0                                      all          https://st.yandex-team.ru/PASSP-21615": {
			"", "", false,
		},
		"ii  yandex-passport-blackbox                        2.37.0                                     all          blackbox": {
			"yandex-passport-blackbox", "2.37.0", true,
		},
		"ii  passport-sezam-front-fastcgi-config             1.401                                      all          Configs for Blackbox and MDA fastcgi modules": {
			"passport-sezam-front-fastcgi-config", "1.401", true,
		},
	}

	for line, v := range res {
		pkg, ver, found := parseDpkgLine(cfg, line)
		require.Equal(t, v, resType{pkg, ver, found})
	}
}
