package tracer_test

import (
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/security/gideon/gideon/internal/tracer"
	"a.yandex-team.ru/security/gideon/gideon/pkg/events"
)

func TestParseSessionInfo(t *testing.T) {
	cases := []struct {
		title string
		env   string
		info  map[string]string
		kind  events.SessionKind
	}{
		{
			title: "lala",
			info:  nil,
		},
		{
			title: "something",
			env:   "KEK=LALA\x00YT_SHELL_ID\x00",
			info:  nil,
		},
		{
			title: "yt-jobshell",
			env:   "KEK=LALA\x00YT_SHELL_ID=blah-blah",
			kind:  events.SessionKind_SK_YT_JOBSHELL,
			info: map[string]string{
				"session": "blah-blah",
			},
		},
		{
			title: "yt-jobshell",
			env:   "YT_SHELL_ID=blah-blah\x00KEK=LALA",
			kind:  events.SessionKind_SK_YT_JOBSHELL,
			info: map[string]string{
				"session": "blah-blah",
			},
		},
		{
			title: "sessionleader: portoshell-session",
			kind:  events.SessionKind_SK_PORTOSHELL,
			info:  map[string]string{},
		},
		{
			title: "sessionleader: portoshell-session[]",
			kind:  events.SessionKind_SK_PORTOSHELL,
			info:  map[string]string{},
		},
		{
			title: "sessionleader: portoshell-session []",
			kind:  events.SessionKind_SK_PORTOSHELL,
			info:  map[string]string{},
		},
		{
			title: "sessionleader: portoshell-session [user=tst",
			kind:  events.SessionKind_SK_PORTOSHELL,
			info:  map[string]string{},
		},
		{
			title: "sessionleader: portoshell-session user=tst]",
			kind:  events.SessionKind_SK_PORTOSHELL,
			info:  map[string]string{},
		},
		{
			title: "sessionleader: portoshell-session [user=lala]",
			kind:  events.SessionKind_SK_PORTOSHELL,
			info: map[string]string{
				"user": "lala",
			},
		},
		{
			title: "sessionleader: portoshell-session [user=lala] [session=blah-blah]",
			kind:  events.SessionKind_SK_PORTOSHELL,
			info: map[string]string{
				"user":    "lala",
				"session": "blah-blah",
			},
		},
		{
			title: "sessionleader: portoshell-session [user=lala][session=blah-blah]    ",
			kind:  events.SessionKind_SK_PORTOSHELL,
			info: map[string]string{
				"user":    "lala",
				"session": "blah-blah",
			},
		},
		{
			title: "sessionleader: portoshell-session [user=lala] [session=blah-blah] [foo=bar]",
			kind:  events.SessionKind_SK_PORTOSHELL,
			info: map[string]string{
				"user":    "lala",
				"session": "blah-blah",
				"foo":     "bar",
			},
		},
	}

	for _, tc := range cases {
		t.Run(tc.title, func(t *testing.T) {
			kind, info := tracer.ParseSessionInfo(tc.title, tc.env)
			require.Equal(t, tc.kind.String(), kind.String())
			require.EqualValues(t, tc.info, info)
		})
	}
}
