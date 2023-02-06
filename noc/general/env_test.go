package inputs

import (
	"os"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestConfitaEvn(t *testing.T) {
	sshConnString := "2a02:6b8::1 47144 2a02:6b8:c0e:87:0:675:2bff:5693 22"
	assert.NoError(t, os.Setenv("SSH_CONNECTION", sshConnString))
	assert.NoError(t, os.Setenv("USER", "user1"))
	assert.NoError(t, os.Setenv("CVSROOT", "/cvs/root/"))

	environ := Environment{}
	assert.NoError(t, environ.Load())
	expectedEnv := Environment{
		User:          "user1",
		SSHConnection: sshConnString,
		CVSRoot:       "/cvs/root/",
	}
	assert.Equal(t, expectedEnv, environ)

	assert.NoError(t, os.Unsetenv("SSH_CONNECTION"))
	newEnviron := Environment{}
	assert.NoError(t, newEnviron.Load())
	assert.Equal(t, newEnviron.SSHConnection, "unknown")
}
