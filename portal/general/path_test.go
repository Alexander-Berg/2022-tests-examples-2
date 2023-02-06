package paths

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/portal/avocado/libs/utils/common"
	"a.yandex-team.ru/portal/avocado/libs/utils/fs"
)

func Test_pathSearcher_getOptionsPath(t *testing.T) {
	type fields struct {
		env common.Environment
	}
	type args struct {
		dir string
	}
	tests := []struct {
		name    string
		fields  fields
		args    args
		want    string
		wantErr bool
	}{
		{
			name: "Got not empty dir in params",
			fields: fields{
				env: common.Development,
			},
			args: args{
				dir: "testdata/madm",
			},
			want: "testdata/madm/options.json",
		},
		{
			name: "Got not empty dir in params, but file didn't exists",
			fields: fields{
				env: common.Development,
			},
			args: args{
				dir: "/Users/Alice/madm",
			},
			want:    "/Users/Alice/madm/options.json",
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			s := &pathSearcher{
				env: tt.fields.env,
				fs:  fs.NewFileSystemProxy(),
			}

			got, err := s.getOptionsPath(tt.args.dir)

			require.Equal(t, tt.want, got)
			if tt.wantErr {
				require.Error(t, err)
			} else {
				require.NoError(t, err)
			}
		})
	}
}

func Test_pathSearcher_getExportPath(t *testing.T) {
	type fields struct {
		env common.Environment
	}
	type args struct {
		dir        string
		exportName string
	}
	tests := []struct {
		name   string
		fields fields
		args   args
		want   string
	}{
		{
			name: "Got dir in args",
			fields: fields{
				env: common.Development,
			},
			args: args{
				dir:        "/Users/Alice/madm",
				exportName: "options",
			},
			want: "/Users/Alice/madm/options.json",
		},
		{
			name: "Got dir for prod",
			fields: fields{
				env: common.Development,
			},
			args: args{
				exportName: "options",
			},
			want: "/opt/www/bases/madm/production_ready/options.json",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			s := &pathSearcher{
				env: tt.fields.env,
				fs:  fs.NewFileSystemProxy(),
			}

			got := s.getExportPath(tt.args.dir, tt.args.exportName)

			require.Equal(t, tt.want, got)
		})
	}
}

func Test_pathSearcher_getTestingSubDir(t *testing.T) {
	type fields struct {
		env      common.Environment
		hostname string
	}
	tests := []struct {
		name   string
		fields fields
		want   string
	}{
		{
			name: "Got dev hostname",
			fields: fields{
				env:      common.Development,
				hostname: "morda-dev-v195.sas.yp-c.yandex.net",
			},
			want: "-v195d0/testing_ready",
		},
		{
			name: "Got not dev hostname",
			fields: fields{
				env:      common.Development,
				hostname: "stable-portal-mordago-13.sas.yp-c.yandex.net",
			},
			want: "testing_ready",
		},
		{
			name: "Env is testing",
			fields: fields{
				env:      common.Testing,
				hostname: "morda-dev-v195.sas.yp-c.yandex.net",
			},
			want: "testing_ready",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			s := &pathSearcher{
				env:      tt.fields.env,
				fs:       fs.NewFileSystemProxy(),
				hostname: tt.fields.hostname,
			}
			got := s.getTestingSubDir()

			require.Equal(t, tt.want, got)
		})
	}
}

func Test_pathsProvider_getExportPaths(t *testing.T) {
	type fields struct {
		env      common.Environment
		hostname string
	}
	tests := []struct {
		name   string
		fields fields
		dir    string
		export string
		want   []string
	}{
		{
			name: "Dev with hostname, default dir",
			fields: fields{
				env:      common.Development,
				hostname: "morda-dev-v195.sas.yp-c.yandex.net",
			},
			dir:    "",
			export: "test",
			want: []string{
				"/opt/www/bases/madm/production_ready/test.json",
				"/opt/www/bases/madm/testing_ready/test.json",
				"/opt/www/bases/madm/-v195d0/production_ready/test.json",
				"/opt/www/bases/madm/-v195d0/testing_ready/test.json",
			},
		},
		{
			name: "Dev with hostname, nondefault dir",
			fields: fields{
				env:      common.Development,
				hostname: "morda-dev-v195.sas.yp-c.yandex.net",
			},
			dir:    "/testdir",
			export: "test",
			want: []string{
				"/testdir/production_ready/test.json",
				"/testdir/testing_ready/test.json",
				"/testdir/-v195d0/production_ready/test.json",
				"/testdir/-v195d0/testing_ready/test.json",
			},
		},
		{
			name: "Dev without non-dev hostname",
			fields: fields{
				env:      common.Development,
				hostname: "stable-portal-mordago-13.sas.yp-c.yandex.net",
			},
			dir:    "/opt/www/bases/madm",
			export: "test",
			want: []string{
				"/opt/www/bases/madm/production_ready/test.json",
				"/opt/www/bases/madm/testing_ready/test.json",
			},
		},
		{
			name: "Production",
			fields: fields{
				env:      common.Production,
				hostname: "stable-portal-mordago-13.sas.yp-c.yandex.net",
			},
			dir:    "/opt/www/bases/madm",
			export: "test",
			want: []string{
				"/opt/www/bases/madm/production_ready/test.json",
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			s := NewPathsProvider(tt.fields.env, tt.fields.hostname)
			got := s.getExportPaths(tt.dir, tt.export)

			assert.Equal(t, tt.want, got)
		})
	}
}
