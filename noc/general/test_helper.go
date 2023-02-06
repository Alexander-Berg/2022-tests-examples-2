package core

import (
	"context"

	"a.yandex-team.ru/library/go/core/log"
)

func makeTestApp() *App {
	jtiConf := JTIConfigs{
		"ds": {},
	}
	conf := CollectorConfig{
		Pollers:  PollerConfigs{JTI: &jtiConf},
		Loglevel: log.DebugLevel,
	}
	ctx := context.Background()
	app, _ := MakeApp(ctx, "testhostname", &conf)
	return app
}
