package prompt_test

import (
	"bytes"
	"io"
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/security/libs/go/prompt"
)

func TestAsk(t *testing.T) {
	cases := []struct {
		opts      prompt.AskOptions
		userInput io.Reader
		expect    string
	}{
		{
			opts: prompt.AskOptions{
				Query: "Foo?",
			},
			userInput: bytes.NewBufferString("Foo\n"),
			expect:    "Foo",
		},

		{
			opts: prompt.AskOptions{
				Query:   "Bar?",
				Default: "Bar",
			},
			userInput: bytes.NewBufferString("\n"),
			expect:    "Bar",
		},
	}

	for _, c := range cases {
		ui, err := prompt.NewUI(prompt.UIOptions{
			Writer: io.Discard,
			Reader: c.userInput,
		})
		assert.NoError(t, err)

		actual, err := ui.Ask(c.opts)
		assert.NoError(t, err)
		assert.Equal(t, c.expect, actual)
	}
}
