package origin

import (
	"testing"

	"github.com/stretchr/testify/require"

	protoanswers "a.yandex-team.ru/apphost/lib/proto_answers"
	"a.yandex-team.ru/portal/avocado/libs/utils/cookies"
	"a.yandex-team.ru/portal/avocado/morda-go/pkg/its"
)

func Test_fixer_Fix(t *testing.T) {
	tests := []struct {
		name    string
		options its.Options
		request *protoanswers.THttpRequest
		want    *protoanswers.THttpRequest
	}{
		{
			name: "full valid request",
			options: its.Options{
				RequestCorrectionBehaviour: CutHeadersBehaviour,
			},
			request: &protoanswers.THttpRequest{
				Path: "valid/path",
				Headers: []*protoanswers.THeader{
					{
						Name:  "valid name",
						Value: "valid value",
					},
					{
						Name:  "Cookie",
						Value: "valid cookie",
					},
				},
			},
			want: &protoanswers.THttpRequest{
				Path: "valid/path",
				Headers: []*protoanswers.THeader{
					{
						Name:  "valid name",
						Value: "valid value",
					},
					{
						Name:  "Cookie",
						Value: "valid cookie",
					},
				},
			},
		},
		{
			name: "no cuts",
			options: its.Options{
				RequestCorrectionBehaviour: NoCutBehaviour,
			},
			request: &protoanswers.THttpRequest{
				Path: "path/\xc5",
				Headers: []*protoanswers.THeader{
					{
						Name:  "\xc5name",
						Value: "val\xc5ue",
					},
					{
						Name:  "Cookie",
						Value: "cookie\xc5",
					},
				},
			},
			want: &protoanswers.THttpRequest{
				Path: "path/\xc5",
				Headers: []*protoanswers.THeader{
					{
						Name:  "\xc5name",
						Value: "val\xc5ue",
					},
					{
						Name:  "Cookie",
						Value: "cookie\xc5",
					},
				},
			},
		},
		{
			name: "cut symbols",
			options: its.Options{
				RequestCorrectionBehaviour: CutSymbolsBehaviour,
			},
			request: &protoanswers.THttpRequest{
				Path: "path/\xc5",
				Headers: []*protoanswers.THeader{
					{
						Name:  "\xc5name",
						Value: "val\xc5ue",
					},
					{
						Name:  "Cookie",
						Value: "cookie\xc5",
					},
				},
			},
			want: &protoanswers.THttpRequest{
				Path: "path/",
				Headers: []*protoanswers.THeader{
					{
						Name:  "name",
						Value: "value",
					},
					{
						Name:  "Cookie",
						Value: "cookie",
					},
				},
			},
		},
		{
			name: "cut headers",
			options: its.Options{
				RequestCorrectionBehaviour: CutHeadersBehaviour,
			},
			request: &protoanswers.THttpRequest{
				Path: "path/\xc5",
				Headers: []*protoanswers.THeader{
					{
						Name:  "\xc5name",
						Value: "val\xc5ue",
					},
					{
						Name:  "Cookie",
						Value: "cookie\xc5",
					},
				},
			},
			want: &protoanswers.THttpRequest{
				Path:    "path/",
				Headers: []*protoanswers.THeader{},
			},
		},
		{
			name: "cut cookie or header",
			options: its.Options{
				RequestCorrectionBehaviour: CutCookieOrHeadersBehaviour,
			},
			request: &protoanswers.THttpRequest{
				Path: "path/\xc5",
				Headers: []*protoanswers.THeader{
					{
						Name:  "\xc5name",
						Value: "val\xc5ue",
					},
					{
						Name:  "Cookie",
						Value: "cookie\xc5",
					},
					{
						Name:  "Cookie",
						Value: "cookie",
					},
				},
			},
			want: &protoanswers.THttpRequest{
				Path: "path/",
				Headers: []*protoanswers.THeader{
					{
						Name:  "Cookie",
						Value: "",
					},
					{
						Name:  "Cookie",
						Value: "cookie",
					},
				},
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			fixer := NewFixer(tt.options, cookies.NewParser())
			fixer.Fix(tt.request)
			require.Equal(t, tt.want, tt.request)
		})
	}
}
