package cookies

import (
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
)

func Test_parserMy_Parser(t *testing.T) {
	type args struct {
		cookieMy string
	}
	tests := []struct {
		name    string
		args    args
		want    models.MyCookie
		wantErr bool
	}{
		{
			name: "Empty",
			args: args{
				cookieMy: "YwA=",
			},
			want: models.MyCookie{
				Parsed: map[uint32][]int32{},
			},
		},
		{
			name: "Forced mobile",
			args: args{
				cookieMy: "YywBAAA=",
			},
			want: models.MyCookie{
				Parsed: map[uint32][]int32{
					44: {0},
				},
			},
		},
		{
			name: "Several languages, forced mobile",
			args: args{
				cookieMy: "YycCAAMsAQAA",
			},
			want: models.MyCookie{
				Parsed: map[uint32][]int32{
					39: {0, 3},
					44: {0},
				},
			},
		},
		{
			name: "Big number in value",
			args: args{
				cookieMy: "YywBwIeiOAA=",
			},
			want: models.MyCookie{
				Parsed: map[uint32][]int32{
					44: {8888888},
				},
			},
		},
		{
			name: "Base64 decode fail",
			args: args{
				cookieMy: "Тест",
			},
			wantErr: true,
		},
		{
			name: "No end symbol",
			args: args{
				cookieMy: "Yw==",
			},
			wantErr: true,
		},
		{
			name: "Start symbol incorrect",
			args: args{
				cookieMy: "AA==",
			},
			wantErr: true,
		},
		{
			name: "Wrong count of values",
			args: args{
				cookieMy: "YywAwIeiOAA=",
			},
			wantErr: true,
		},
		{
			name: "Value is 255",
			args: args{
				cookieMy: "YywBgP8A",
			},
			want: models.MyCookie{
				Parsed: map[uint32][]int32{
					44: {255},
				},
			},
		},
		{
			name: "Value is 254",
			args: args{
				cookieMy: "YywBgP4A",
			},
			want: models.MyCookie{
				Parsed: map[uint32][]int32{
					44: {254},
				},
			},
		},
		{
			name: "Value is 127",
			args: args{
				cookieMy: "YywBfwA=",
			},
			want: models.MyCookie{
				Parsed: map[uint32][]int32{
					44: {127},
				},
			},
		},
		{
			name: "Value is 128",
			args: args{
				cookieMy: "YywBgIAA",
			},
			want: models.MyCookie{
				Parsed: map[uint32][]int32{
					44: {128},
				},
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			p := &parserMy{}

			got, err := p.Parse(tt.args.cookieMy)

			if tt.wantErr {
				require.Error(t, err)
			} else {
				require.NoError(t, err)
				require.Equal(t, tt.want, got)
			}
		})
	}
}

func Test_fifo_pop(t *testing.T) {
	type fields struct {
		b []byte
	}
	tests := []struct {
		name    string
		fields  fields
		want    byte
		wantErr bool
	}{
		{
			name: "Got first",
			fields: fields{
				b: []byte{2, 8},
			},
			want:    2,
			wantErr: false,
		},
		{
			name: "Go error while zero slice",
			fields: fields{
				b: []byte{},
			},
			want:    0,
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			f := &fifo{
				b: tt.fields.b,
			}

			got, err := f.pop()

			if tt.wantErr {
				require.Error(t, err)
			} else {
				require.NoError(t, err)
				require.Equal(t, tt.want, got)
			}
		})
	}
}
