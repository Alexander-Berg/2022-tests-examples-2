package config

import (
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/portal/avocado/libs/utils/apphost"
	"a.yandex-team.ru/portal/avocado/libs/utils/common"
)

func TestLoad(t *testing.T) {
	type args struct {
		args []string
	}
	tests := []struct {
		name    string
		args    args
		want    Config
		wantErr bool
	}{
		{
			name: "No args",
			args: args{
				args: []string{},
			},
			want:    Config{},
			wantErr: true,
		},
		{
			name: "Only port & default config",
			args: args{
				args: []string{"-apphost=20700"},
			},
			want: Config{
				Service: Service{
					Environment: common.Development,
				},
				Apphost: apphost.Config{
					Port: 20700,
				},
			},
			wantErr: false,
		},
		{
			name: "Get data from file",
			args: args{
				args: []string{"-config=testdata/config.yaml"},
			},
			want: Config{
				Log: Log{
					WriteToSyslog: true,
				},
				Service: Service{
					Location:     "MAN",
					BuildVersion: "0.0.1",
					Environment:  common.Testing,
					MaxProcs:     2,
					PprofPort:    1234,
				},
				Apphost: apphost.Config{
					Port: 8888,
				},
			},
			wantErr: false,
		},
		{
			name: "Overwrite from flags",
			args: args{
				args: []string{"-config=testdata/config.yaml", "-apphost=20700", "-buildver=1.0.0", "-pprof_port=4321"},
			},
			want: Config{
				Log: Log{
					WriteToSyslog: true,
				},
				Service: Service{
					Location:     "MAN",
					BuildVersion: "1.0.0",
					Environment:  common.Testing,
					MaxProcs:     2,
					PprofPort:    4321,
				},
				Apphost: apphost.Config{
					Port: 20700,
				},
			},
			wantErr: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := Load(tt.args.args)

			if tt.wantErr {
				require.Error(t, err)
			} else {
				require.NoError(t, err)
				require.Equal(t, tt.want, got)
			}
		})
	}
}
