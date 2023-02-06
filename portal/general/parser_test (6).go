package cookies

import (
	"net/http"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
)

func Test_parser_Parse(t *testing.T) {
	type args struct {
		raw string
	}
	tests := []struct {
		name    string
		args    args
		want    models.Cookie
		wantErr bool
	}{
		{
			name: "Parse real cookie",
			args: args{
				raw: "i=HuW+z7THFxziz9l93WdTzxRqrwdTjgkL5Y+y72L5suFizu+Yq4uUtlKOPhDJYtK+4RyC34dQ7ybpJ6peh8zcy1HDQEg=; is_gdpr=0; is_gdpr_b=CK+GIhDfIygC; mda=0; yandex_gid=213; yandexuid=1234567890123456789; yp=1618661331.ygu.1#1616505385.nwcst.1616419200_213_1",
			},
			want: models.Cookie{
				Parsed: map[string][]string{
					"i":          {"HuW+z7THFxziz9l93WdTzxRqrwdTjgkL5Y+y72L5suFizu+Yq4uUtlKOPhDJYtK+4RyC34dQ7ybpJ6peh8zcy1HDQEg="},
					"is_gdpr":    {"0"},
					"is_gdpr_b":  {"CK+GIhDfIygC"},
					"mda":        {"0"},
					"yandex_gid": {"213"},
					"yandexuid":  {"1234567890123456789"},
					"yp":         {"1618661331.ygu.1#1616505385.nwcst.1616419200_213_1"},
				},
			},
		},
		{
			name: "Doubled keys",
			args: args{
				raw: "test=qwerty;test=y182",
			},
			want: models.Cookie{
				Parsed: map[string][]string{
					"test": {"qwerty", "y182"},
				},
			},
		},
		{
			name: "Value in double quotes",
			args: args{
				raw: `device_id="chto-tostrannoetestovoe"`,
			},
			want: models.Cookie{
				Parsed: map[string][]string{
					"device_id": {"chto-tostrannoetestovoe"},
				},
			},
		},
		{
			name: "Invalid cookie key",
			args: args{
				raw: "test =oo;",
			},
			want: models.Cookie{
				Parsed: map[string][]string{},
			},
		},
		{
			name: "Without semicolon",
			args: args{
				raw: "test=oo",
			},
			want: models.Cookie{
				Parsed: map[string][]string{
					"test": {"oo"},
				},
			},
		},
		{
			name: "Value started by space",
			args: args{
				raw: "test= oo;",
			},
			want: models.Cookie{
				Parsed: map[string][]string{
					"test": {" oo"},
				},
			},
		},
		{
			name: "Empty raw string",
			args: args{
				raw: "",
			},
			want: models.Cookie{
				Parsed: map[string][]string{},
			},
		},
		{
			name: "Cookie my",
			args: args{
				raw: "my=YycCAAMsAQAA;test=123",
			},
			want: models.Cookie{
				Parsed: map[string][]string{
					"my":   {"YycCAAMsAQAA"},
					"test": {"123"},
				},
				My: models.MyCookie{
					Parsed: map[uint32][]int32{
						39: {0, 3},
						44: {0},
					},
				},
			},
		},
		{
			name: "Invalid cookie my",
			args: args{
				raw: "my=Yw==;test=123",
			},
			want: models.Cookie{
				Parsed: map[string][]string{
					"my":   {"Yw=="},
					"test": {"123"},
				},
				My: models.MyCookie{},
			},
			wantErr: true,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			p := &parser{
				parserMy: NewParserMy(),
			}

			got, err := p.Parse(tt.args.raw)
			require.Equal(t, tt.wantErr, err != nil)
			require.Equal(t, tt.want, got)
		})
	}
}

func Test_headerParser_JoinHttp(t *testing.T) {
	type args struct {
		cookies []*http.Cookie
	}
	tests := []struct {
		name string
		args args
		want string
	}{
		{
			name: "Simple check",
			args: args{
				cookies: []*http.Cookie{
					{Name: "test", Value: "ooo"},
					{Name: "uts", Value: "sefopi0wd"},
				},
			},
			want: "test=ooo;uts=sefopi0wd",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			p := &parser{}

			got := p.JoinHTTP(tt.args.cookies)

			require.Equal(t, tt.want, got)
		})
	}
}

func Test_parser_ParseInHTTP(t *testing.T) {
	type testCase struct {
		name string
		raw  string
		want []*http.Cookie
	}
	cases := []testCase{
		{
			name: "empty string",
			raw:  "",
			want: make([]*http.Cookie, 0),
		},
		{
			name: "regular value",
			raw:  "town=korolyov; fruit=apple",
			want: []*http.Cookie{
				{
					Name:  "town",
					Value: "korolyov",
				},
				{
					Name:  "fruit",
					Value: "apple",
				},
			},
		},
		{
			name: "starts with semicolon",
			raw:  "; town=korolyov; fruit=apple",
			want: []*http.Cookie{
				{
					Name:  "town",
					Value: "korolyov",
				},
				{
					Name:  "fruit",
					Value: "apple",
				},
			},
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			p := &parser{}
			got := p.ParseInHTTP(tt.raw)
			require.Equal(t, tt.want, got)
		})
	}
}
