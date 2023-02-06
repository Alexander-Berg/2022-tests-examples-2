package searchapp

import (
	"testing"

	"github.com/stretchr/testify/require"

	protoanswers "a.yandex-team.ru/apphost/lib/proto_answers"
)

func Test_compareRequestsToExternalService(t *testing.T) {
	type args struct {
		expected *protoanswers.THttpRequest
		actual   *protoanswers.THttpRequest
	}
	tests := []struct {
		name string
		args args
		want []string
	}{
		{
			name: "Requests is equal",
			args: args{
				expected: &protoanswers.THttpRequest{
					Scheme: protoanswers.THttpRequest_Http,
					Path:   "?preset=morda_div_cards_news_searchapp&need_pictures=1&picture_sizes=398.224.1&count=20&rubric=personal_feed&personalize=personal_feed&url_type=home_search_app&device_id=&userid=23791068",
				},
				actual: &protoanswers.THttpRequest{
					Scheme: protoanswers.THttpRequest_Http,
					Path:   "?preset=morda_div_cards_news_searchapp&need_pictures=1&picture_sizes=398.224.1&count=20&rubric=personal_feed&personalize=personal_feed&url_type=home_search_app&device_id=&userid=23791068",
				},
			},
			want: nil,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := compareRequestsToExternalService(tt.args.expected, tt.args.actual)
			require.Equal(t, tt.want, got)
		})
	}
}
