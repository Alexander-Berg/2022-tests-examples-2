package laas

import (
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
)

func TestNewHint(t *testing.T) {
	type args struct {
		appInfo models.AppInfo
		ip      string
	}

	tests := []struct {
		name    string
		args    args
		want    uint64
		wantErr assert.ErrorAssertionFunc
	}{
		{
			name: "uuid hint",
			args: args{
				appInfo: models.AppInfo{
					UUID: "1111",
				},
				ip: "127.0.0.1",
			},
			want:    1627347513391462713,
			wantErr: assert.NoError,
		},
		{
			name: "ip hint",
			args: args{
				ip: "127.0.0.1",
			},
			want:    12302425093482026174,
			wantErr: assert.NoError,
		},
		{
			name:    "empty hint error",
			args:    args{},
			want:    0,
			wantErr: assert.Error,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := NewHint(tt.args.appInfo, tt.args.ip)
			assert.Equal(t, tt.want, got)
			tt.wantErr(t, err)
		})
	}
}
