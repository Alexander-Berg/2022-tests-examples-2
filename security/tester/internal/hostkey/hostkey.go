package hostkey

import (
	"encoding/json"
	"fmt"
	"os"

	"golang.org/x/crypto/ssh"
)

const defKey = `
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAaAAAABNlY2RzYS
1zaGEyLW5pc3RwMjU2AAAACG5pc3RwMjU2AAAAQQSez1VqzXg9ZNoG8Cduikrl2tO6/Ayu
ORQtXhudo8YASgvhPOpKTrMGAuEsWuOJqUKt6qVVKA54yxJU6ifoPPyGAAAAsCMwW7YjMF
u2AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBJ7PVWrNeD1k2gbw
J26KSuXa07r8DK45FC1eG52jxgBKC+E86kpOswYC4Sxa44mpQq3qpVUoDnjLElTqJ+g8/I
YAAAAgN0+qOuY01RBwtPU+FoKNmrGl9cUCrBFqxmuINWJjVqQAAAARYnVnbGxvY0BiaWct
YnVnZ3kBAgMEBQYH
-----END OPENSSH PRIVATE KEY-----
`

var PrivateKeys = func() []ssh.Signer {
	var out []ssh.Signer
	addKey := func(in string) {
		s, err := ssh.ParsePrivateKey([]byte(in))
		if err != nil {
			panic(fmt.Sprintf("failed to parse host private key: %v. Key:\n:%s", err, in))
		}

		out = append(out, s)
	}

	envKeys, ok := os.LookupEnv("HOST_KEYS")
	if !ok {
		addKey(defKey)
		return out
	}

	var keys []string
	if err := json.Unmarshal([]byte(envKeys), &keys); err != nil {
		panic(fmt.Sprintf("failed to parse host private keys from env: %v", err))
	}

	for _, k := range keys {
		addKey(k)
	}

	return out
}()
