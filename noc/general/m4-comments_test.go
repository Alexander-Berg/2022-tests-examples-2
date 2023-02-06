package app

import (
	"strings"
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/noc/puncher/models"
)

func assertCommentSplit(t *testing.T, long string, split string, limit int) {
	comment := splitComment(long, limit)

	assert.Equal(t, split, splitComment(long, limit))
	for _, line := range strings.Split(comment, "\n") {
		assert.True(t, len(line) <= limit, "Line '%s' length(%d) is longer than limit (%d)", line, len(line), limit)
	}
}

func TestMultilineComment(t *testing.T) {
	comment := `Comment line 1
Comment line 2`
	assert.Equal(t,
		`# Comment line 1
# Comment line 2
`, getComment(models.Rule{Comment: comment}, true))
}

func TestLargeComment_ascii(t *testing.T) {
	assertCommentSplit(t,
		"\nAlice was beginning to get very tired of sitting by her sister on the bank, and"+
			" of having nothing to do: once or twice she had peeped into the book her sister was reading,"+
			" but it had no pictures or conversations in it, 'and_what_is_the_use_of_a_book,' thought"+
			" Alice_'without_pictures_or_conversations?'",
		`
Alice was beginning to get very tired
of sitting by her sister on the bank,
and of having nothing to do: once or
twice she had peeped into the book her
sister was reading, but it had no
pictures or conversations in it,
'and_what_is_the_use_of_a_book,'
thought
Alice_'without_pictures_or_conversati-
ons?'`, 38)
}

func TestLargeComment_utf8(t *testing.T) {
	assertCommentSplit(t,
		"\nАлиса сидела со старшей сестрой на берегу и маялась: делать ей было совершенно нечего,"+
			" а сидеть без дела, сами знаете, дело нелегкое; раз-другой она, правда, сунула нос в книгу,"+
			" которую сестра читала, но там не оказалось ни картинок, ни стишков. 'Кому_нужны_книжки_без_картинок.-"+
			" или хоть стишков, не понимаю!' - думала Алиса.",
		`
Алиса сидела со
старшей сестрой на
берегу и маялась:
делать ей было
совершенно нечего, а
сидеть без дела, сами
знаете, дело
нелегкое; раз-другой
она, правда, сунула
нос в книгу, которую
сестра читала, но там
не оказалось ни
картинок, ни стишков.
'Кому_нужны_книжки_б-
ез_картинок.- или
хоть стишков, не
понимаю!' - думала
Алиса.`, 38)
}

func TestQuotedComment(t *testing.T) {
	comment := "That's what I'm talk`ing about!"
	rule := models.Rule{Comment: comment}
	assert.Equal(t,
		"# That’s what I’m talk’ing about!\n",
		getComment(rule, true))
}
