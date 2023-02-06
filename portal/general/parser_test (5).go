package clids

import (
	"net/url"
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/libs/utils/log3"
)

func Test_parserService_parseValue(t *testing.T) {
	type args struct {
		s string
	}
	tests := []struct {
		name string
		args args
		want string
	}{
		{
			name: "Empty string",
			args: args{
				s: "",
			},
			want: "",
		},
		{
			name: "Got only client in clid",
			args: args{
				s: "1924",
			},
			want: "1924",
		},
		{
			name: "Big clid",
			args: args{
				s: "12893-91248.213",
			},
			want: "12893",
		},
		{
			name: "Invalid",
			args: args{
				s: "test",
			},
			want: "",
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			p := &parser{}

			got := p.parseValue(tt.args.s)

			require.Equal(t, tt.want, got)
		})
	}
}

func Test_parser_parseFromCookie(t *testing.T) {
	type cookieAnswer struct {
		cookie models.Cookie
	}
	tests := []struct {
		name         string
		cookieAnswer *cookieAnswer
		want         *models.Clid
	}{
		{
			name: "Got nil map from cookie getter",
			cookieAnswer: &cookieAnswer{
				cookie: models.Cookie{},
			},
			want: nil,
		},
		{
			name: "No S key in cookies",
			cookieAnswer: &cookieAnswer{
				cookie: models.Cookie{
					Parsed: map[string][]string{
						"A": {"test"},
					},
				},
			},
			want: nil,
		},
		{
			name: "Got S key, but value is empty",
			cookieAnswer: &cookieAnswer{
				cookie: models.Cookie{
					Parsed: map[string][]string{
						"S": {""},
					},
				},
			},
			want: nil,
		},
		{
			name: "Got S key and value is parseable",
			cookieAnswer: &cookieAnswer{
				cookie: models.Cookie{
					Parsed: map[string][]string{
						"S": {"12893-91248.213"},
					},
				},
			},
			want: &models.Clid{
				Client: "12893",
			},
		},
		{
			name: "Got S key and value is parseable, but in second value",
			cookieAnswer: &cookieAnswer{
				cookie: models.Cookie{
					Parsed: map[string][]string{
						"S": {"", "12893-91248.213"},
					},
				},
			},
			want: nil,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			cookieGetter := NewMockcookieGetter(ctrl)
			if tt.cookieAnswer != nil {
				cookieGetter.EXPECT().GetCookie().Return(tt.cookieAnswer.cookie).Times(1)
			}
			p := &parser{
				logger:       log3.NewLoggerStub(),
				cookieGetter: cookieGetter,
			}

			got := p.parseFromCookie()
			require.Equal(t, tt.want, got)
		})
	}
}

func Test_parser_parseFromOrigin(t *testing.T) {
	tests := []struct {
		name string
		cgi  url.Values
		want *models.Clid
	}{
		{
			name: "CGI is nil",
			cgi:  nil,
			want: nil,
		},
		{
			name: "CGI is empty",
			cgi:  url.Values{},
			want: nil,
		},
		{
			name: "CGI has clid",
			cgi:  url.Values{"clid": {"832-082.66"}},
			want: &models.Clid{
				Client: "832",
			},
		},
		{
			name: "CGI has clid in but empty",
			cgi:  url.Values{"clid": {""}},
			want: nil,
		},
		{
			name: "CGI has clid in but no value",
			cgi:  url.Values{"clid": {}},
			want: nil,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			requestGetter := NewMockrequestGetter(ctrl)
			requestGetter.EXPECT().GetRequest().Return(models.Request{CGI: tt.cgi}).Times(1)

			p := &parser{
				logger:        log3.NewLoggerStub(),
				requestGetter: requestGetter,
			}

			got := p.parseFromCGI()

			require.Equal(t, tt.want, got)
		})
	}
}

func Test_parser_parse(t *testing.T) {
	type cookieAnswer struct {
		cookie models.Cookie
	}
	tests := []struct {
		name         string
		cgi          url.Values
		cookieAnswer *cookieAnswer
		want         models.Clid
	}{
		{
			name: "Got nil map from cookie getter and nil CGI",
			cgi:  nil,
			cookieAnswer: &cookieAnswer{
				cookie: models.Cookie{},
			},
			want: models.Clid{},
		},
		{
			name:         "Got answer from CGI",
			cgi:          url.Values{"clid": {"9124"}},
			cookieAnswer: nil,
			want: models.Clid{
				Client: "9124",
			},
		},
		{
			name: "Got answer from cookies",
			cgi:  nil,
			cookieAnswer: &cookieAnswer{
				cookie: models.Cookie{
					Parsed: map[string][]string{
						"S": {"555"},
					},
				},
			},
			want: models.Clid{
				Client: "555",
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			requestGetter := NewMockrequestGetter(ctrl)
			requestGetter.EXPECT().GetRequest().Return(models.Request{CGI: tt.cgi}).Times(1)
			cookieGetter := NewMockcookieGetter(ctrl)
			if tt.cookieAnswer != nil {
				cookieGetter.EXPECT().GetCookie().Return(tt.cookieAnswer.cookie).Times(1)
			}
			p := &parser{
				logger:        log3.NewLoggerStub(),
				requestGetter: requestGetter,
				cookieGetter:  cookieGetter,
			}

			got := p.parse()

			require.Equal(t, tt.want, got)
		})
	}
}
