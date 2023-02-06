package testdata

import (
	"fmt"

	"golang.org/x/crypto/ssh"
	"golang.org/x/crypto/ssh/agent"
)

type Key struct {
	agent.AddedKey
	Signer ssh.Signer
}

var Keys = make(map[string]Key)
var SSHCertificates = make(map[string]Key)
var ExpiredSSHCertificates = make(map[string]Key)

func init() {
	parseKey := func(typ string, key []byte) (interface{}, ssh.Signer) {
		priv, err := ssh.ParseRawPrivateKey(key)
		if err != nil {
			panic(fmt.Sprintf("unable to parse test key %s: %v", typ, err))
		}

		signer, err := ssh.NewSignerFromKey(priv)
		if err != nil {
			panic(fmt.Sprintf("unable to create signer for test key %s: %v", typ, err))
		}
		return priv, signer
	}

	for t, k := range PEMBytes {
		if t == "ca" {
			continue
		}

		priv, signer := parseKey(t, k)
		Keys[t] = Key{
			Signer: signer,
			AddedKey: agent.AddedKey{
				PrivateKey: priv,
				Comment:    t,
			},
		}
	}

	parseCert := func(typ string, certBytes []byte) Key {
		sshPub, _, _, _, err := ssh.ParseAuthorizedKey(certBytes)
		if err != nil {
			panic(fmt.Sprintf("unable to parse ssh pub key %s: %v", typ, err))
		}

		sshCert, ok := sshPub.(*ssh.Certificate)
		if !ok {
			panic(fmt.Sprintf("not cert pub key: %s", typ))
		}

		priv, signer := parseKey(typ, PEMBytes[typ])
		signer, err = ssh.NewCertSigner(sshCert, signer)
		if err != nil {
			panic(fmt.Sprintf("unable to create cert signer %s: %v", typ, err))
		}

		return Key{
			Signer: signer,
			AddedKey: agent.AddedKey{
				PrivateKey:  priv,
				Certificate: sshCert,
				Comment:     typ + "-cert",
			},
		}
	}

	for t, c := range SSHCertificateBytes {
		SSHCertificates[t] = parseCert(t, c)
	}

	for t, c := range ExpiredSSHCertificateBytes {
		ExpiredSSHCertificates[t] = parseCert(t, c)
	}
}
