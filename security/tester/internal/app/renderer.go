package app

import (
	"bytes"
	_ "embed"
	"fmt"
	"io"
	"strings"
	"time"

	"golang.org/x/crypto/ssh"
	"golang.org/x/crypto/ssh/agent"

	"a.yandex-team.ru/security/skotty/skotty/pkg/sshutil"
)

func (a *App) renderClientInfo(cl *ClientInfo) ([]byte, error) {
	formatBool := func(b bool) string {
		if b {
			return "yes"
		}
		return "no"
	}

	staffedKey := func(key ssh.PublicKey) string {
		if cl.StaffkeysErr != nil {
			return fmt.Sprintf("unble to check: %s", cl.StaffkeysErr)
		}

		var target string
		if cert, ok := key.(*ssh.Certificate); ok {
			target = ssh.FingerprintSHA256(cert.SignatureKey)
		} else {
			target = ssh.FingerprintSHA256(key)
		}

		for _, sk := range cl.StaffKeys {
			if sk == target {
				return formatBool(true)
			}
		}

		return formatBool(false)
	}

	formatKey := func(out io.Writer, in ssh.PublicKey) {
		writeCertInfo := func(key ssh.PublicKey) {
			crt, ok := key.(*ssh.Certificate)
			if !ok {
				return
			}

			_, _ = fmt.Fprintf(out, "      - revoked: %s\n", formatBool(a.krl.IsRevoked(crt)))
			_, _ = fmt.Fprintf(out, "      - principals: %s\n", strings.Join(crt.ValidPrincipals, ","))
			_, _ = fmt.Fprintf(out, "      - valid before: %s\n", time.Unix(int64(crt.ValidBefore), 0).Format("2006-01-02T15:04"))
			_, _ = fmt.Fprintf(out, "      - ca fingerprint: %s\n", sshutil.Fingerprint(crt.SignatureKey))
			_, _ = fmt.Fprintf(out, "      - serial: %d\n", crt.Serial)
			_, _ = fmt.Fprintf(out, "      - key id: %s\n", crt.KeyId)
		}

		writeKeyInfo := func(key ssh.PublicKey) {
			_, _ = fmt.Fprintf(out, "    * %s\n", sshutil.Fingerprint(key))
			_, _ = fmt.Fprintf(out, "      - type: %s\n", key.Type())
			_, _ = fmt.Fprintf(out, "      - present on staff: %s\n", staffedKey(key))
			writeCertInfo(key)
		}

		switch v := in.(type) {
		case *agent.Key:
			sshKey, err := ssh.ParsePublicKey(v.Marshal())
			if err != nil {
				break
			}

			writeKeyInfo(sshKey)
			_, _ = fmt.Fprintf(out, "      - comment: %s\n", v.Comment)
		default:
			writeKeyInfo(v)
		}
	}

	var out bytes.Buffer
	_, _ = fmt.Fprint(&out, "Welcome to the Skotty Validation server!\n\n")

	if cl.ClientCompatNotice != "" {
		_, _ = fmt.Fprintln(&out, cl.ClientCompatNotice)
	}
	_, _ = fmt.Fprintln(&out, "Info about your connection:")
	_, _ = fmt.Fprintf(&out, "  - Client version: %s\n", cl.ClientVersion)
	_, _ = fmt.Fprintf(&out, "  - Username: %s\n", cl.Username)
	_, _ = fmt.Fprintf(&out, "  - Auth keys: %d\n", len(cl.AuthKeys))
	for _, key := range cl.AuthKeys {
		formatKey(&out, key)
	}

	if cl.AgentForwarded {
		_, _ = fmt.Fprintln(&out, "  - Agent forwarded: yes")
		_, _ = fmt.Fprintf(&out, "  - Agent support sudo: %s\n", formatBool(cl.SudoAvailable))
		_, _ = fmt.Fprintf(&out, "  - Agent keys: %d\n", len(cl.AgentKeys))
		for _, key := range cl.AgentKeys {
			formatKey(&out, key)
		}
	} else {
		_, _ = fmt.Fprintln(&out, "  - Agent forwarded: no")
	}

	_ = out.WriteByte('\n')
	_, _ = out.WriteString("Have a great day! ;)\n")
	return out.Bytes(), nil
}
