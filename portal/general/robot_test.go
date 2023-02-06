package models

import (
	"testing"

	"github.com/stretchr/testify/assert"

	mordadata "a.yandex-team.ru/portal/avocado/proto/morda_data"
)

func TestNewRobot(t *testing.T) {
	type args struct {
		robot *mordadata.Robot
	}
	tests := []struct {
		name string
		args args
		want *Robot
	}{
		{
			name: "nil robot",
			args: args{
				robot: nil,
			},
			want: nil,
		},
		{
			name: "true robot",
			args: args{
				robot: &mordadata.Robot{
					IsRobot: true,
				},
			},
			want: &Robot{IsRobot: true},
		},
		{
			name: "false robot",
			args: args{
				robot: &mordadata.Robot{
					IsRobot: false,
				},
			},
			want: &Robot{false},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			assert.Equal(t, tt.want, NewRobot(tt.args.robot))
		})
	}
}

func TestRobot_DTO(t *testing.T) {
	type fields struct {
		Value bool
	}
	tests := []struct {
		name   string
		fields fields
		want   *mordadata.Robot
	}{
		{
			name: "true robot",
			fields: fields{
				Value: true,
			},
			want: &mordadata.Robot{IsRobot: true},
		},
		{
			name: "false robot",
			fields: fields{
				Value: false,
			},
			want: &mordadata.Robot{IsRobot: false},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			r := &Robot{
				IsRobot: tt.fields.Value,
			}
			assert.Equal(t, tt.want, r.DTO())
		})
	}
}
