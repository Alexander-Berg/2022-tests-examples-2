package tacacs_test

import (
	"fmt"
	"testing"
	"time"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/noc/nocauth/pkg/tacacs"
)

func TestOTPasswordManager_Generate(t *testing.T) {
	type args struct {
		username   string
		deviceName string
	}
	tests := []struct {
		args     args
		expected string
		hasError bool
	}{
		{
			args: args{
				username:   "vladstar",
				deviceName: "noc-sas",
			},
			expected: "nfl3oaMdI|1Cntza",
			hasError: false,
		},
		{
			args: args{
				username:   "diman",
				deviceName: "noc-sas",
			},
			expected: "8sD7Gt7lc|1Cntza",
			hasError: false,
		},
		{
			args: args{
				username:   "diman~",
				deviceName: "noc-sas",
			},
			expected: "",
			hasError: true,
		},
	}

	frozenTime, err := time.Parse("2006-01-02", "2017-01-01")
	require.NoError(t, err)

	m := tacacs.NewOTPasswordManagerWithNow([]byte("secret"), func() time.Time {
		return frozenTime
	})

	for _, tt := range tests {
		t.Run(
			fmt.Sprintf("%s_%s", tt.args.username, tt.args.deviceName),
			func(t *testing.T) {
				actual, err := m.Generate(tt.args.username, tt.args.deviceName)
				if tt.hasError {
					require.Error(t, err)
					return
				}
				require.Equal(t, tt.expected, actual)
			})
	}
}

func TestOTPasswordManager_Validate(t *testing.T) {
	type args struct {
		username   string
		deviceName string
	}
	tests := []struct {
		args     args
		password string
	}{
		{
			args: args{
				username:   "vladstar",
				deviceName: "noc-sas",
			},
			password: "nfl3oaMdI|1Cntza",
		},
		{
			args: args{
				username:   "diman",
				deviceName: "noc-sas",
			},
			password: "8sD7Gt7lc|1Cntza",
		},
	}

	frozenTime, err := time.Parse("2006-01-02", "2017-01-01")
	require.NoError(t, err)

	m := tacacs.NewOTPasswordManagerWithNow([]byte("secret"), func() time.Time {
		return frozenTime
	})

	for _, tt := range tests {
		t.Run(
			fmt.Sprintf("%s_%s_%s", tt.args.username, tt.args.deviceName, tt.password),
			func(t *testing.T) {
				err := m.Validate(tt.args.username, tt.args.deviceName, tt.password)
				require.NoError(t, err)
			})
	}
}
