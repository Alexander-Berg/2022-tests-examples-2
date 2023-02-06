package app

import (
	"a.yandex-team.ru/library/go/core/log"
	"a.yandex-team.ru/security/skotty/tester/internal/staff"
)

type Option func(*App)

func WithLogger(l log.Logger) Option {
	return func(app *App) {
		app.l = l
	}
}

func WithStaffClient(staffc *staff.Client) Option {
	return func(app *App) {
		app.staffc = staffc
	}
}
