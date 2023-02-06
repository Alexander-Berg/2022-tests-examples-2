package mordacommon

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	protoanswers "a.yandex-team.ru/apphost/lib/proto_answers"
	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
)

func Test_CheckRedirect(t *testing.T) {
	type testCase struct {
		name         string
		host         string
		isHTTPS      bool
		path         string
		wantRedirect bool
		wantNewHost  string
	}

	cases := []testCase{
		{
			name:         "no host header",
			host:         "",
			path:         "/",
			wantRedirect: false,
			wantNewHost:  "",
		},
		{
			name:         "regular https",
			host:         "yandex.ru",
			isHTTPS:      true,
			path:         "/",
			wantRedirect: false,
			wantNewHost:  "",
		},
		{
			name:         "regular http",
			host:         "yandex.ru",
			isHTTPS:      false,
			path:         "/",
			wantRedirect: true,
			wantNewHost:  "yandex.ru",
		},
		{
			name:         "regular https to national TLD-domain",
			host:         "yandex.by",
			isHTTPS:      true,
			path:         "/",
			wantRedirect: false,
			wantNewHost:  "",
		},
		{
			name:         "chrome NTP",
			host:         "yandex.ru",
			path:         "/portal/api/data?some_arg=value",
			wantRedirect: false,
			wantNewHost:  "",
		},
		{
			name:         "starts with www",
			host:         "www.yandex.ru",
			path:         "/",
			wantRedirect: true,
			wantNewHost:  "yandex.ru",
		},
		{
			name:         "ends with dot",
			host:         "yandex.ru.",
			path:         "/",
			wantRedirect: true,
			wantNewHost:  "yandex.ru",
		},
		{
			name:         "ends with dot and starts with www",
			host:         "www.yandex.kz.",
			path:         "/",
			wantRedirect: true,
			wantNewHost:  "yandex.kz",
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			var headers []*protoanswers.THeader
			if tt.host != "" {
				headers = []*protoanswers.THeader{
					{
						Name:  "Host",
						Value: tt.host,
					},
				}
			}
			if tt.isHTTPS {
				headers = append(headers, &protoanswers.THeader{
					Name:  "X-Yandex-Https",
					Value: "1",
				})
			}
			gotNewHost, gotRedirect := CheckRedirect(headers, tt.path)
			assert.Equal(t, tt.wantRedirect, gotRedirect, "check redirect flag")
			assert.Equal(t, tt.wantNewHost, gotNewHost, "check new host")
		})
	}
}

func Test_CheckDzenRedirect(t *testing.T) {
	type testCase struct {
		name         string
		host         string
		path         string
		wantRedirect bool
		wantNewPath  string
		isGramps     bool
	}

	cases := []testCase{
		{
			name:         "no host header",
			host:         "",
			path:         "/",
			wantRedirect: false,
			wantNewPath:  "",
		},
		{
			name:         "regular redirect",
			host:         "yandex.ru",
			path:         "/",
			wantRedirect: true,
			wantNewPath:  "/?yredirect=true",
		},
		{
			name:         "redirect params",
			host:         "yandex.ru",
			path:         "/?clid=235352&some=thing",
			wantRedirect: true,
			wantNewPath:  "/?clid=235352&yredirect=true",
		},
		{
			name:         "gramps device",
			host:         "yandex.ru",
			path:         "/?clid=235352&some=thing",
			wantRedirect: false,
			wantNewPath:  "",
			isGramps:     true,
		},
		{
			name:         "national TLD-domain",
			host:         "yandex.by",
			path:         "/",
			wantRedirect: false,
			wantNewPath:  "",
		},
		{
			name:         "chrome NTP",
			host:         "yandex.ru",
			path:         "/portal/api/data?some_arg=value",
			wantRedirect: false,
			wantNewPath:  "",
		},
		{
			name:         "starts with www",
			host:         "www.yandex.ru",
			path:         "/",
			wantRedirect: true,
			wantNewPath:  "/?yredirect=true",
		},
		{
			name:         "ends with dot",
			host:         "yandex.ru.",
			path:         "/",
			wantRedirect: true,
			wantNewPath:  "/?yredirect=true",
		},
		{
			name:         "ends with dot and starts with www",
			host:         "www.yandex.kz.",
			path:         "/",
			wantRedirect: false,
			wantNewPath:  "",
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			originRequest := protoanswers.THttpRequest{
				Path: tt.path,
				Headers: []*protoanswers.THeader{{
					Name:  "Host",
					Value: tt.host,
				}},
			}
			device := models.Device{
				BrowserDesc: &models.BrowserDesc{
					IsGramps:  tt.isGramps,
					UserAgent: "user-agent",
				},
			}
			gotNewPath, gotRedirect := CheckDzenRedirect(&originRequest, device)
			assert.Equal(t, tt.wantNewPath, gotNewPath, "check new path")
			assert.Equal(t, tt.wantRedirect, gotRedirect, "check redirect flag")
		})
	}
}

func Test_IsRequestToLegacy(t *testing.T) {
	type args struct {
		path string
		host string
	}
	tests := []struct {
		name string
		args args
		want bool
	}{
		{
			name: "root path",
			args: args{
				path: "/",
				host: "",
			},
			want: false,
		}, {
			name: "root path 2",
			args: args{
				path: "//",
				host: "",
			},
			want: false,
		},
		{
			name: "m path",
			args: args{
				path: "/m",
				host: "",
			},
			want: false,
		},
		{
			name: "M path",
			args: args{
				path: "/M",
				host: "",
			},
			want: false,
		},
		{
			name: "m path 2",
			args: args{
				path: "/m/",
				host: "",
			},
			want: false,
		},
		{
			name: "m path 3",
			args: args{
				path: "/m//",
				host: "",
			},
			want: false,
		},
		{
			name: "d path",
			args: args{
				path: "/d/",
				host: "",
			},
			want: false,
		},
		{
			name: "d path 2",
			args: args{
				path: "/D/",
				host: "",
			},
			want: false,
		},
		{
			name: "d path 3",
			args: args{
				path: "//d/",
				host: "",
			},
			want: false,
		},
		{
			name: "all path",
			args: args{
				path: "/all",
				host: "",
			},
			want: false,
		},
		{
			name: "beta path",
			args: args{
				path: "/beta",
				host: "",
			},
			want: true,
		},
		{
			name: "portal path",
			args: args{
				path: "/portal",
				host: "",
			},
			want: true,
		},
		{
			name: "mhaha path",
			args: args{
				path: "/mhaha",
				host: "",
			},
			want: true,
		},
		{
			name: "ololo path",
			args: args{
				path: "/ololo/",
				host: "",
			},
			want: true,
		},
		{
			name: "mobilsearch path",
			args: args{
				path: "/portal/mobilesearch",
				host: "",
			},
			want: true,
		},
		{
			name: "yabrowser path",
			args: args{
				path: "/portal/api/yabrowser",
				host: "",
			},
			want: true,
		},
		{
			name: "qwe.hometest.ya.ru hostname",
			args: args{
				path: "/",
				host: "qwe.hometest.ya.ru",
			},
			want: false,
		},
		{
			name: "hamster.ya.ru hostname",
			args: args{
				path: "/",
				host: "hamster.ya.ru",
			},
			want: false,
		},
		{
			name: "ya.ru hostname",
			args: args{
				path: "/",
				host: "ya.ru",
			},
			want: false,
		},
		{
			name: "rc.ya.ru hostname",
			args: args{
				path: "/",
				host: "rc.ya.ru",
			},
			want: false,
		},
		//"/chrome/newtab",
		//"/black",
		//"/white",
		//"/test/something",
		//"/test/",
		//"/portal/ntp/banner",
		//"/portal/ntp/main",
		//"/portal/ntp/main2",
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {

			got := IsRequestToLegacy(tt.args.path, tt.args.host)

			require.Equal(t, tt.want, got)
		})
	}
}
