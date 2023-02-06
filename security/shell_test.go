package parsers

import (
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/security/osquery/osquery-sender/syslogparsing/formats"
)

func TestSudoOk(t *testing.T) {
	var logLine = "<85>Dec 22 21:04:45 kms-data-vla-1 sudo:   ferran : TTY=pts/1 ; PWD=/home/ferran ; USER=root ; COMMAND=/bin/systemctl restart rsyslog.service"
	name := "Shell"
	event := parseLog(logLine, Shell, name)
	expectedTime, _ := formats.ParseStandardFormatDate("Dec 22 21:04:45")
	expectedData := map[string]interface{}{
		"name": name,
		ColumnsDataKey: map[string]interface{}{
			"time":         float64(expectedTime.Unix()),
			"hostname":     "kms-data-vla-1",
			"process":      "sudo",
			"username":     "ferran",
			"sudo_TTY":     "pts/1",
			"sudo_PWD":     "/home/ferran",
			"sudo_USER":    "root",
			"sudo_COMMAND": "/bin/systemctl restart rsyslog.service",
			"priority":     85.0,
			"severity":     5.0,
			"facility":     10.0,
		},
	}
	require.Equal(t, expectedData, event.Data)
}

func TestSudoNotInSudoers(t *testing.T) {
	var logLine = "<81>Dec 27 09:14:13 kms-data-vla-1 sudo:    games : user NOT in sudoers ; TTY=pts/0 ; PWD=/home/ferran ; USER=root ; COMMAND=/bin/ls"
	name := "Shell"
	event := parseLog(logLine, Shell, name)
	expectedTime, _ := formats.ParseStandardFormatDate("Dec 27 09:14:13")
	expectedData := map[string]interface{}{
		"name": name,
		ColumnsDataKey: map[string]interface{}{
			"time":         float64(expectedTime.Unix()),
			"hostname":     "kms-data-vla-1",
			"process":      "sudo",
			"username":     "games",
			"message":      "user NOT in sudoers",
			"sudo_TTY":     "pts/0",
			"sudo_PWD":     "/home/ferran",
			"sudo_USER":    "root",
			"sudo_COMMAND": "/bin/ls",
			"priority":     81.0,
			"severity":     1.0,
			"facility":     10.0,
		},
	}
	require.Equal(t, expectedData, event.Data)
}

func TestSshdAcceptedRsaCert(t *testing.T) {
	var logLine = "<38>Dec 22 21:04:42 kms-data-vla-1 sshd[448159]: Accepted publickey for ferran from 2a02:6b8:bf00:2005:526b:4bff:fedb:7a41 port 51024 ssh2: RSA-CERT ID type=session;requester=ferran; (serial 14477456656239810445) CA RSA SHA256:xQdCsb6SvRtPo9XvY5DYNhYGjq+J3PBE5HGRcwUZKv0"
	name := "Shell"
	event := parseLog(logLine, Shell, name)
	expectedTime, _ := formats.ParseStandardFormatDate("Dec 22 21:04:42")
	expectedData := map[string]interface{}{
		"name": name,
		ColumnsDataKey: map[string]interface{}{
			"time":            float64(expectedTime.Unix()),
			"hostname":        "kms-data-vla-1",
			"process":         "sshd",
			"proc_id":         "448159",
			"auth_result":     "Accepted",
			"auth_type":       "RSA-CERT",
			"username":        "ferran",
			"source_ip":       "2a02:6b8:bf00:2005:526b:4bff:fedb:7a41",
			"source_port":     "51024",
			"cert_id":         "type=session;requester=ferran",
			"cert_serial":     "14477456656239810445",
			"rsa_fingerprint": "CA RSA SHA256:xQdCsb6SvRtPo9XvY5DYNhYGjq+J3PBE5HGRcwUZKv0",
			"priority":        38.0,
			"severity":        6.0,
			"facility":        4.0,
		},
	}
	require.Equal(t, expectedData, event.Data)
}

func TestSshdFailedRsaCert(t *testing.T) {
	var logLine = "<38>Dec 22 21:05:33 kms-data-vla-1 sshd[448497]: Failed publickey for root from 2a02:6b8:bf00:2005:526b:4bff:fedb:7a41 port 51796 ssh2: RSA-CERT ID type=session;requester=ferran; (serial 14477456656239810445) CA RSA SHA256:xQdCsb6SvRtPo9XvY5DYNhYGjq+J3PBE5HGRcwUZKv0"
	name := "Shell"
	event := parseLog(logLine, Shell, name)
	expectedTime, _ := formats.ParseStandardFormatDate("Dec 22 21:05:33")
	expectedData := map[string]interface{}{
		"name": name,
		ColumnsDataKey: map[string]interface{}{
			"time":            float64(expectedTime.Unix()),
			"hostname":        "kms-data-vla-1",
			"process":         "sshd",
			"proc_id":         "448497",
			"auth_result":     "Failed",
			"auth_type":       "RSA-CERT",
			"username":        "root",
			"source_ip":       "2a02:6b8:bf00:2005:526b:4bff:fedb:7a41",
			"source_port":     "51796",
			"cert_id":         "type=session;requester=ferran",
			"cert_serial":     "14477456656239810445",
			"rsa_fingerprint": "CA RSA SHA256:xQdCsb6SvRtPo9XvY5DYNhYGjq+J3PBE5HGRcwUZKv0",
			"priority":        38.0,
			"severity":        6.0,
			"facility":        4.0,
		},
	}
	require.Equal(t, expectedData, event.Data)
}

func TestSshdAcceptedRsa(t *testing.T) {
	var logLine = "<38>Dec 23 07:17:29 kms-data-vla-1 sshd[637312]: Accepted publickey for ferran from ::1 port 52846 ssh2: RSA SHA256:udikdpEgscSvJAUEeiId+906lrQ4G+SqKEbuzrq1wlY"
	name := "Shell"
	event := parseLog(logLine, Shell, name)
	expectedTime, _ := formats.ParseStandardFormatDate("Dec 23 07:17:29")
	expectedData := map[string]interface{}{
		"name": name,
		ColumnsDataKey: map[string]interface{}{
			"time":            float64(expectedTime.Unix()),
			"hostname":        "kms-data-vla-1",
			"process":         "sshd",
			"proc_id":         "637312",
			"auth_result":     "Accepted",
			"auth_type":       "RSA",
			"username":        "ferran",
			"source_ip":       "::1",
			"source_port":     "52846",
			"rsa_fingerprint": "SHA256:udikdpEgscSvJAUEeiId+906lrQ4G+SqKEbuzrq1wlY",
			"priority":        38.0,
			"severity":        6.0,
			"facility":        4.0,
		},
	}
	require.Equal(t, expectedData, event.Data)
}

func TestSshdFailedRsa(t *testing.T) {
	var logLine = "<38>Dec 23 07:18:31 kms-data-vla-1 sshd[637665]: Failed publickey for root from ::1 port 52908 ssh2: RSA SHA256:udikdpEgscSvJAUEeiId+906lrQ4G+SqKEbuzrq1wlY"
	name := "Shell"
	event := parseLog(logLine, Shell, name)
	expectedTime, _ := formats.ParseStandardFormatDate("Dec 23 07:18:31")
	expectedData := map[string]interface{}{
		"name": name,
		ColumnsDataKey: map[string]interface{}{
			"time":            float64(expectedTime.Unix()),
			"hostname":        "kms-data-vla-1",
			"process":         "sshd",
			"proc_id":         "637665",
			"auth_result":     "Failed",
			"auth_type":       "RSA",
			"username":        "root",
			"source_ip":       "::1",
			"source_port":     "52908",
			"rsa_fingerprint": "SHA256:udikdpEgscSvJAUEeiId+906lrQ4G+SqKEbuzrq1wlY",
			"priority":        38.0,
			"severity":        6.0,
			"facility":        4.0,
		},
	}
	require.Equal(t, expectedData, event.Data)
}

func TestSshdFailedRsaNoPriority(t *testing.T) {
	var logLine = "Dec 22 15:40:31 vla04-s15-37.cloud.yandex.net sshd[659105]: Failed publickey for andrei-vlg from 2a02:6b8:b081:8125::1:33 port 59285 ssh2: RSA SHA256:c1Upcl9iP5FYE9y79qAazlBbDPv0Pr7FkcDXR4QN/T4"
	name := "Shell"
	event := parseLog(logLine, Shell, name)
	expectedTime, _ := formats.ParseStandardFormatDate("Dec 22 15:40:31")
	expectedData := map[string]interface{}{
		"name": name,
		ColumnsDataKey: map[string]interface{}{
			"time":            float64(expectedTime.Unix()),
			"hostname":        "vla04-s15-37.cloud.yandex.net",
			"process":         "sshd",
			"proc_id":         "659105",
			"auth_result":     "Failed",
			"auth_type":       "RSA",
			"username":        "andrei-vlg",
			"source_ip":       "2a02:6b8:b081:8125::1:33",
			"source_port":     "59285",
			"rsa_fingerprint": "SHA256:c1Upcl9iP5FYE9y79qAazlBbDPv0Pr7FkcDXR4QN/T4",
		},
	}
	require.Equal(t, expectedData, event.Data)
}

// Just in case we get unexpected info after "ssh2: "
func TestSshdAcceptedPublicKeyUnexpectedInfo(t *testing.T) {
	var logLine = "<38>Dec 23 07:17:29 kms-data-vla-1 sshd[637312]: Accepted publickey for ferran from ::1 port 52846 ssh2: some unexpected info"
	name := "Shell"
	event := parseLog(logLine, Shell, name)
	expectedTime, _ := formats.ParseStandardFormatDate("Dec 23 07:17:29")
	expectedData := map[string]interface{}{
		"name": name,
		ColumnsDataKey: map[string]interface{}{
			"time":        float64(expectedTime.Unix()),
			"hostname":    "kms-data-vla-1",
			"process":     "sshd",
			"proc_id":     "637312",
			"auth_result": "Accepted",
			"auth_type":   "publickey",
			"username":    "ferran",
			"source_ip":   "::1",
			"source_port": "52846",
			"message":     "some unexpected info",
			"priority":    38.0,
			"severity":    6.0,
			"facility":    4.0,
		},
	}
	require.Equal(t, expectedData, event.Data)
}

func TestSshdAcceptedPassword(t *testing.T) {
	var logLine = "<38>Dec 27 14:32:41 kms-data-vla-1 sshd[452454]: Accepted password for ferran-test from ::1 port 44092 ssh2"
	name := "Shell"
	event := parseLog(logLine, Shell, name)
	expectedTime, _ := formats.ParseStandardFormatDate("Dec 27 14:32:41")
	expectedData := map[string]interface{}{
		"name": name,
		ColumnsDataKey: map[string]interface{}{
			"time":        float64(expectedTime.Unix()),
			"hostname":    "kms-data-vla-1",
			"process":     "sshd",
			"proc_id":     "452454",
			"auth_result": "Accepted",
			"auth_type":   "password",
			"username":    "ferran-test",
			"source_ip":   "::1",
			"source_port": "44092",
			"priority":    38.0,
			"severity":    6.0,
			"facility":    4.0,
		},
	}
	require.Equal(t, expectedData, event.Data)
}

func TestSshdFailedPassword(t *testing.T) {
	var logLine = "<38>Dec 27 13:30:56 kms-data-vla-1 sshd[433262]: Failed password for games from ::1 port 41216 ssh2"
	name := "Shell"
	event := parseLog(logLine, Shell, name)
	expectedTime, _ := formats.ParseStandardFormatDate("Dec 27 13:30:56")
	expectedData := map[string]interface{}{
		"name": name,
		ColumnsDataKey: map[string]interface{}{
			"time":        float64(expectedTime.Unix()),
			"hostname":    "kms-data-vla-1",
			"process":     "sshd",
			"proc_id":     "433262",
			"auth_result": "Failed",
			"auth_type":   "password",
			"username":    "games",
			"source_ip":   "::1",
			"source_port": "41216",
			"priority":    38.0,
			"severity":    6.0,
			"facility":    4.0,
		},
	}
	require.Equal(t, expectedData, event.Data)
}

func TestSshdFailedPasswordInvalidUser(t *testing.T) {
	var logLine = "Feb 21 08:35:22 localhost sshd[5774]: Failed password for invalid user dummy from 116.31.116.24 port 29160 ssh2"
	name := "Shell"
	event := parseLog(logLine, Shell, name)
	expectedTime, _ := formats.ParseStandardFormatDate("Feb 21 08:35:22")
	expectedData := map[string]interface{}{
		"name": name,
		ColumnsDataKey: map[string]interface{}{
			"time":        float64(expectedTime.Unix()),
			"hostname":    "localhost",
			"process":     "sshd",
			"proc_id":     "5774",
			"auth_result": "Failed",
			"auth_type":   "password",
			"username":    "dummy",
			"source_ip":   "116.31.116.24",
			"source_port": "29160",
		},
	}
	require.Equal(t, expectedData, event.Data)
}

func TestSshdInvalidUser(t *testing.T) {
	var logLine = "<38>Dec 22 21:05:13 kms-data-vla-1 sshd[448401]: Invalid user wrong from 2a02:6b8:bf00:110b:526b:4bff:fedb:6de9"
	name := "Shell"
	event := parseLog(logLine, Shell, name)
	expectedTime, _ := formats.ParseStandardFormatDate("Dec 22 21:05:13")
	expectedData := map[string]interface{}{
		"name": name,
		ColumnsDataKey: map[string]interface{}{
			"time":        float64(expectedTime.Unix()),
			"hostname":    "kms-data-vla-1",
			"process":     "sshd",
			"proc_id":     "448401",
			"auth_result": "Failed",
			"username":    "wrong",
			"source_ip":   "2a02:6b8:bf00:110b:526b:4bff:fedb:6de9",
			"priority":    38.0,
			"severity":    6.0,
			"facility":    4.0,
		},
	}
	require.Equal(t, expectedData, event.Data)
}

func TestSshdNotLogin(t *testing.T) {
	var logLine = "<38>Dec 22 21:04:42 kms-data-vla-1 sshd[448159]: Accepted certificate ID \"type=session;requester=ferran;\" (serial 14477456656239810445) signed by RSA CA SHA256:xQdCsb6SvRtPo9XvY5DYNhYGjq+J3PBE5HGRcwUZKv0 via /home/ferran/.ssh/authorized_keys"
	name := "Shell"
	event := parseLog(logLine, Shell, name)
	expectedTime, _ := formats.ParseStandardFormatDate("Dec 22 21:04:42")
	expectedData := map[string]interface{}{
		"name": name,
		ColumnsDataKey: map[string]interface{}{
			"time":     float64(expectedTime.Unix()),
			"hostname": "kms-data-vla-1",
			"process":  "sshd",
			"proc_id":  "448159",
			"message":  "Accepted certificate ID \"type=session;requester=ferran;\" (serial 14477456656239810445) signed by RSA CA SHA256:xQdCsb6SvRtPo9XvY5DYNhYGjq+J3PBE5HGRcwUZKv0 via /home/ferran/.ssh/authorized_keys",
			"priority": 38.0,
			"severity": 6.0,
			"facility": 4.0,
		},
	}
	require.Equal(t, expectedData, event.Data)
}

func TestSshdNotSshdLog(t *testing.T) {
	var logLine = "<86>Dec 22 21:04:45 kms-data-vla-1 sudo: pam_unix(sudo:session): session opened for user root by ferran(uid=0)"
	name := "Shell"
	event := parseLog(logLine, Shell, name)
	expectedTime, _ := formats.ParseStandardFormatDate("Dec 22 21:04:45")
	expectedData := map[string]interface{}{
		"name": name,
		ColumnsDataKey: map[string]interface{}{
			"time":     float64(expectedTime.Unix()),
			"hostname": "kms-data-vla-1",
			"process":  "sudo",
			"message":  "pam_unix(sudo:session): session opened for user root by ferran(uid=0)",
			"priority": 86.0,
			"severity": 6.0,
			"facility": 10.0,
		},
	}
	require.Equal(t, expectedData, event.Data)
}

func TestStrangeMessage(t *testing.T) {
	var logLine = "strange message"
	_, err := parseLogLine(Shell.Format, logLine)
	require.Equal(t, "regexp didn't match for log: strange message", err.Error())
}
