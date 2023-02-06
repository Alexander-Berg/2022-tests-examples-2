package config_test

import (
	"a.yandex-team.ru/metrika/go/pkg/config"
	"encoding/xml"
	"fmt"
)

type Config struct {
	config.Config
	VaultToken config.YavToken `xml:"vault_token"`
	Password   config.FromYav  `xml:"password"`
}

var (
	rawConfig = []byte(`
<yandex>
    <vault_token from-env="TOKEN"/>
    <password from-yav="ver-01e75qym4p04p4jscame9j4k04/old"/>
</yandex>
`)
)

func Example() {
	var cfg Config
	_ = xml.Unmarshal(rawConfig, &cfg)
	fmt.Printf("password: %s\n", cfg.Password)
}
