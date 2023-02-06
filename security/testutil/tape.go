package testutil

import (
	"sync"

	"a.yandex-team.ru/security/libs/go/boombox/tape"
)

var (
	KirbyTapePath = "kirby_e2e.bolt"
	KirbyTapeRo   = true
	kirbyTape     *tape.Tape
	kirbyTapeOnce sync.Once
)

func KirbyTape() *tape.Tape {
	kirbyTapeOnce.Do(func() {
		var opts []tape.Option
		if KirbyTapeRo {
			opts = append(opts, tape.WithReadOnly())
		}

		var err error
		kirbyTape, err = tape.NewTape(KirbyTapePath, opts...)
		if err != nil {
			panic(err)
		}
	})

	return kirbyTape
}
