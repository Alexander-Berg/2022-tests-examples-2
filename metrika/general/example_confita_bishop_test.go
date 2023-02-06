package config_test

import (
	"a.yandex-team.ru/metrika/go/pkg/config"
	"context"
	"fmt"
	"github.com/heetch/confita"
	"github.com/heetch/confita/backend/flags"
)

type ExampleBishopConfig struct {
	Master struct {
		SleepTimeout uint32 `config:"sleep_timeout" yaml:"sleep_timeout"`
	} `config:"master" yaml:"master"`
}

func ExampleBishopBackend() {
	loader := confita.NewLoader(
		config.NewBishopBackend("haproxy-runner", "metrika.deploy.infra.haproxy.testing", ""),
		flags.NewBackend(),
	)
	cfg := ExampleBishopConfig{}
	err := loader.Load(context.Background(), &cfg)
	if err != nil {
		panic(err)
	}
	fmt.Printf("CONFIG\n")
	fmt.Printf("%+v\n", cfg)
}
