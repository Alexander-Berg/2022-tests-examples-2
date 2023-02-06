package compare

import (
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/portal/avocado/libs/utils/blackbox"
)

func Test_authComparator_compareAuthInfo(t *testing.T) {
	type args struct {
		expected blackbox.AuthInfo
		got      blackbox.AuthInfo
	}
	tests := []struct {
		name    string
		args    args
		wantErr bool
	}{
		{
			name: "both empty",
			args: args{
				expected: blackbox.AuthInfo{},
				got:      blackbox.AuthInfo{},
			},
			wantErr: false,
		},
		{
			name: "equal AuthInfo",
			args: args{
				expected: blackbox.AuthInfo{
					AuthUser: blackbox.AuthUser{
						UID:   "test",
						Login: "-",
					},
					Logged: 1,
				},
				got: blackbox.AuthInfo{
					AuthUser: blackbox.AuthUser{
						Login: "-",
						UID:   "test",
					},
					Logged: 1,
				},
			},
			wantErr: false,
		},
		{
			name: "not equal",
			args: args{
				expected: blackbox.AuthInfo{
					AuthUser: blackbox.AuthUser{
						Login: "-",
						UID:   "test",
					},
					Logged: 1,
				},
				got: blackbox.AuthInfo{
					AuthUser: blackbox.AuthUser{
						Login: "-",
						UID:   "test",
					},
					Logged: 0,
				},
			},
			wantErr: true,
		},
		{
			name: "got empty",
			args: args{
				expected: blackbox.AuthInfo{
					AuthUser: blackbox.AuthUser{
						Login: "-",
						UID:   "test",
					},
					Logged: 1,
				},
				got: blackbox.AuthInfo{},
			},
			wantErr: true,
		},
		{
			name: "expected empty",
			args: args{
				expected: blackbox.AuthInfo{},
				got: blackbox.AuthInfo{
					AuthUser: blackbox.AuthUser{
						Login: "-",
						UID:   "test",
					},
					Logged: 1,
				},
			},
			wantErr: true,
		},
		{
			name: "nil and empty slice",
			args: args{
				expected: blackbox.AuthInfo{
					Users: nil,
				},
				got: blackbox.AuthInfo{
					Users: []blackbox.AuthUser{},
				},
			},
			wantErr: false,
		},
		{
			name: "nil and empty map",
			args: args{
				expected: blackbox.AuthInfo{
					AuthUser: blackbox.AuthUser{
						Sids: nil,
					},
					Users: []blackbox.AuthUser{{
						Sids: map[string]blackbox.Suid{},
					}},
				},
				got: blackbox.AuthInfo{
					AuthUser: blackbox.AuthUser{
						Sids: map[string]blackbox.Suid{},
					},
					Users: []blackbox.AuthUser{{
						Sids: nil,
					}},
				},
			},
			wantErr: false,
		},
		{
			name: "669 sid with empty value",
			args: args{
				expected: blackbox.AuthInfo{
					AuthUser: blackbox.AuthUser{
						Sids: map[string]blackbox.Suid{
							"669": {},
						},
					},
				},
				got: blackbox.AuthInfo{
					AuthUser: blackbox.AuthUser{
						Sids: map[string]blackbox.Suid{},
					},
				},
			},
			wantErr: false,
		},
		{
			name: "669 sid with not empty value",
			args: args{
				expected: blackbox.AuthInfo{
					AuthUser: blackbox.AuthUser{
						Sids: map[string]blackbox.Suid{
							"669": {Suid: "1"},
						},
					},
				},
				got: blackbox.AuthInfo{
					AuthUser: blackbox.AuthUser{
						Sids: map[string]blackbox.Suid{},
					},
				},
			},
			wantErr: true,
		},
		{
			name: "669 sid with empty value and nil map",
			args: args{
				expected: blackbox.AuthInfo{
					AuthUser: blackbox.AuthUser{
						Sids: map[string]blackbox.Suid{
							"669": {},
						},
					},
				},
				got: blackbox.AuthInfo{
					AuthUser: blackbox.AuthUser{
						Sids: nil,
					},
				},
			},
			wantErr: false,
		},
		{
			name: "669 sid with not empty value and nil map",
			args: args{
				expected: blackbox.AuthInfo{
					AuthUser: blackbox.AuthUser{
						Sids: map[string]blackbox.Suid{
							"669": {Suid: "1"},
						},
					},
				},
				got: blackbox.AuthInfo{
					AuthUser: blackbox.AuthUser{
						Sids: nil,
					},
				},
			},
			wantErr: true,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			c := &authComparator{}
			err := c.compareAuthInfo(tt.args.expected, tt.args.got)

			if tt.wantErr {
				require.Error(t, err)
			} else {
				require.NoError(t, err)
			}
		})
	}
}
