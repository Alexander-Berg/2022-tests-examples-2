package tracer

import "a.yandex-team.ru/security/gideon/gideon/pkg/events"

func ParseSessionInfo(proctitle, env string) (events.SessionKind, map[string]string) {
	return parseSessionInfo(proctitle, env)
}
