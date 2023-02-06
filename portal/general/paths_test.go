package paths

import (
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/portal/avocado/libs/utils/common"
)

func Test_Provider_ExportPaths(t *testing.T) {
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
			s := NewProvider(tt.fields.env, tt.fields.hostname, tt.dir)
			got := s.ExportsPaths(tt.export)

			assert.Equal(t, tt.want, got)
		})
	}
}
