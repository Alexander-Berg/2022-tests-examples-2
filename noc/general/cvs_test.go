package vcs

import (
	"reflect"
	"testing"
)

func TestParseCvsRoot(t *testing.T) {
	type args struct {
		cvsroot string
	}
	tests := []struct {
		name    string
		args    args
		want    *CVSRoot
		wantErr bool
	}{
		{
			name: "puncher",
			args: args{
				cvsroot: "robot-user@tree.y-t.ru:/opt/PATH",
			},
			want: &CVSRoot{
				method: "ext",
				user:   "robot-user",
				host:   "tree.y-t.ru",
				path:   "/opt/PATH",
				full:   "robot-user@tree.y-t.ru:/opt/PATH",
			},
			wantErr: false,
		},
		{
			name: "malformed",
			args: args{
				cvsroot: ":/opt/PATH",
			},
			want:    nil,
			wantErr: true,
		},
		{
			name: "full",
			args: args{
				cvsroot: ":ext:robot-user@tree.y-t.ru:/opt/PATH",
			},
			want: &CVSRoot{
				method: "ext",
				user:   "robot-user",
				host:   "tree.y-t.ru",
				path:   "/opt/PATH",
				full:   ":ext:robot-user@tree.y-t.ru:/opt/PATH",
			},
			wantErr: false,
		},
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := ParseCvsRoot(tt.args.cvsroot)
			if (err != nil) != tt.wantErr {
				t.Errorf("ParseCvsRoot() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if !reflect.DeepEqual(got, tt.want) {
				t.Errorf("ParseCvsRoot() got = %v, want %v", got, tt.want)
			}
		})
	}
}
