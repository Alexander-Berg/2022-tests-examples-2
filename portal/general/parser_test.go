package blackbox

import (
	"testing"

	"github.com/stretchr/testify/require"

	protoanswers "a.yandex-team.ru/apphost/lib/proto_answers"
	"a.yandex-team.ru/portal/morda-go/pkg/dto"
)

func Test_parser_Parse(t *testing.T) {
	type args struct {
		rawProto *protoanswers.THttpResponse
	}
	tests := []struct {
		name    string
		args    args
		want    dto.Auth
		wantErr bool
	}{
		{
			name: "Got empty raw request",
			args: args{
				rawProto: nil,
			},
			want: dto.Auth{Valid: false},
		},
		{
			name: "Got uid in uid.Value",
			args: args{
				rawProto: &protoanswers.THttpResponse{
					Content: []byte(`
						{
							"status": {
								"value": "VALID"
							},
							"error": "OK",
							"uid": {
								"value": "11249"
							}
						}
					`),
				},
			},
			want: dto.Auth{
				Valid: true,
				UID:   "11249",
			},
		},
		{
			name: "Got invalid status",
			args: args{
				rawProto: &protoanswers.THttpResponse{
					Content: []byte(`
						{
							"status": {
								"value": "DISABLED"
							},
							"error": "OK",
							"uid": {
								"value": "11249"
							}
						}
					`),
				},
			},
			want:    dto.Auth{Valid: false},
			wantErr: false,
		},
		{
			name: "Got unknown error",
			args: args{
				rawProto: &protoanswers.THttpResponse{
					Content: []byte(`
						{
							"status": {
								"value": "DISABLED"
							},
							"error": "some kind of error from blackbox",
							"uid": {
								"value": "11249"
							}
						}
					`),
				},
			},
			want:    dto.Auth{Valid: false},
			wantErr: false,
		},
		{
			name: "Got known error",
			args: args{
				rawProto: &protoanswers.THttpResponse{
					Content: []byte(`
						{
							"status": {
								"value": "NEED_RESET"
							},
							"error": "session logged out",
							"uid": {
								"value": "11249"
							}
						}
					`),
				},
			},
			want: dto.Auth{Valid: false},
		},
		{
			name: "Got default_uid instead uid object",
			args: args{
				rawProto: &protoanswers.THttpResponse{
					Content: []byte(`
						{
							"status": {
								"value": "VALID"
							},
							"error": "OK",
							"default_uid": "99250"
						}
					`),
				},
			},
			want: dto.Auth{Valid: true, UID: "99250"},
		},
		{
			name: "Got uid string instead of object",
			args: args{
				rawProto: &protoanswers.THttpResponse{
					Content: []byte(`
						{
							"status": {
								"value": "VALID"
							},
							"error": "OK",
							"uid": "99250"
						}
					`),
				},
			},
			want: dto.Auth{Valid: true, UID: "99250"},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			p := NewParser()

			got, err := p.Parse(tt.args.rawProto)

			if tt.wantErr {
				require.Error(t, err)
			} else {
				require.NoError(t, err)
				require.Equal(t, tt.want, got)
			}
		})
	}
}
