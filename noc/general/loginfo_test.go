package inputs

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"golang.org/x/xerrors"
)

func TestLogInfoArgsParsing(t *testing.T) {
	cases := []struct {
		in   string
		out  LogInfoArgs
		err  error
		part string
	}{
		{" f1.c,HEAD,NONE,1.1 f2.c,HEAD,1.10,1.11", LogInfoArgs{Directory: "", Entity: "files", Files: []File{
			{"f1.c", "add", "HEAD", "NONE", "1.1"},
			{"f2.c", "change", "HEAD", "1.10", "1.11"},
		}}, nil, ""},
		{"dir f1 with spaces.c,HEAD,1.1,1.2 f2.c,tag-1.patch.1,1.10,1.11", LogInfoArgs{Directory: "dir", Entity: "files", Files: []File{
			{"f1 with spaces.c", "change", "HEAD", "1.1", "1.2"},
			{"f2.c", "change", "tag-1.patch.1", "1.10", "1.11"},
		}}, nil, ""},
		{"new/dir - New directory", LogInfoArgs{Directory: "new/dir", Entity: "dir", Files: []File{
			{"", "add", "HEAD", "NONE", "NONE"},
		}}, nil, ""},
		{"new/source - Imported sources", LogInfoArgs{Directory: "new/source", Entity: "source", Files: []File{
			{"", "add", "HEAD", "NONE", "NONE"},
		}}, nil, ""},
		{" f1,HEAD,,1.2 f2.c,tag-1.patch.1,1.10,1.11", LogInfoArgs{},
			ErrUnmatchedPart, " f1,HEAD,,1.2"},

		{" f1,HEAD,1,1.2 f2.c,tag-1.patch.1,1.10,1.11", LogInfoArgs{},
			ErrUnmatchedPart, " f1,HEAD,1,1.2"},

		{" f1,HEAD,1.1,1.2 f2.c,tag-1.patch,NON,1.11", LogInfoArgs{},
			ErrUnmatchedPart, " f2.c,tag-1.patch,NON,1.11"},
		{"f1,HEAD,1.1,1.2 f2.c,tag-1.patch,NONE,1.11", LogInfoArgs{},
			ErrFullMatch, ""},
		{"f1,HEAD,1.1,1.2", LogInfoArgs{}, ErrFullMatch, ""},
	}

	for _, c := range cases {
		t.Run(c.in, func(t *testing.T) {
			out := &LogInfoArgs{}
			err := out.FromString(c.in)
			t.Logf("%v", out)
			if c.err != nil {
				if assert.Error(t, err) && assert.ErrorIs(t, err, c.err) {
					if c.err != ErrFullMatch {
						assert.Equal(t, errUnmatchedPart(c.part).Error(), xerrors.Unwrap(err).Error())
					}
				}
			} else if assert.NoError(t, err) {
				assert.Equal(t, &c.out, out)
			}

		})
	}

}
