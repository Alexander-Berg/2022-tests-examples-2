package inputs

import (
	"strings"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestStdinLogMessageParsing(t *testing.T) {
	stdin := strings.NewReader(`Update of /data/CVSROOT/b
In directory vla-skacheev.net.yandex.net:/tmp/cvs-serv5171/b

Modified Files:
        new_file_b.txt

Log Message:
merge all branch
`)
	parser := LogInfoStdin{}
	err := parser.GetLogMessage(stdin)
	assert.NoError(t, err)
	assert.Equal(t, "merge all branch", parser.Message)
	assert.Equal(t, stdin.Len(), 0, "stdin must be fully read")

	stdin2 := strings.NewReader(`Update of /data/CVSROOT/a
In directory vla-skacheev.net.yandex.net:/tmp/cvs-serv46547/a

Modified Files:
        d e g.txt

Log Message:
long commit message
multiline

with empty lines.

And $CVSROOT env vars,
but not expanded.

with last empty line


`)
	parser = LogInfoStdin{}
	err = parser.GetLogMessage(stdin2)
	assert.NoError(t, err)
	assert.Equal(t, `long commit message
multiline

with empty lines.

And $CVSROOT env vars,
but not expanded.

with last empty line`, parser.Message)
	assert.Equal(t, stdin2.Len(), 0, "stdin must be fully read")
}
