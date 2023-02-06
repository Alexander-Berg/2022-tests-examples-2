package coordinates

import (
	"net/url"
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/portal/avocado/libs/utils/pointer"
)

func Test_parser_parseFloat(t *testing.T) {
	type args struct {
		value string
	}

	tests := []struct {
		name string
		args args
		want float64
		ok   bool
	}{
		{
			name: "success",
			args: args{value: "123"},
			want: 123,
			ok:   true,
		},
		{
			name: "failed",
			args: args{value: "abc"},
			want: 0,
			ok:   false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			c := &parser{}
			got, ok := c.parseFloat(tt.args.value)
			assert.Equal(t, tt.want, got)
			assert.Equal(t, tt.ok, ok)
		})
	}
}

func Test_parser_Parse(t *testing.T) {
	type args struct {
		cgi url.Values
	}
	tests := []struct {
		name string
		args args
		want Coordinates
	}{
		{
			name: "success",
			args: args{
				cgi: map[string][]string{
					"lat":               {"1"},
					"lon":               {"2"},
					"location_accuracy": {"3"},
					"location_recency":  {"4"},
				},
			},
			want: Coordinates{
				Latitude:  1,
				Longitude: 2,
				Accuracy:  pointer.NewFloat64(3),
				Recency:   pointer.NewInt(4),
			},
		},
		{
			name: "empty",
			args: args{
				cgi: map[string][]string{
					"lat":               {"0"},
					"lon":               {"0"},
					"location_accuracy": {"3"},
					"location_recency":  {"4"},
				},
			},
			want: Coordinates{},
		},
		{
			name: "empty accuracy",
			args: args{
				cgi: map[string][]string{
					"lat":              {"1"},
					"lon":              {"2"},
					"location_recency": {"4"},
				},
			},
			want: Coordinates{
				Latitude:  1,
				Longitude: 2,
				Recency: func() *int {
					value := 4
					return &value
				}(),
			},
		},
		{
			name: "empty recency",
			args: args{
				cgi: map[string][]string{
					"lat":               {"1"},
					"lon":               {"2"},
					"location_accuracy": {"3"},
				},
			},
			want: Coordinates{
				Latitude:  1,
				Longitude: 2,
				Accuracy:  pointer.NewFloat64(3),
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			c := &parser{}
			assert.Equal(t, tt.want, c.Parse(tt.args.cgi))
		})
	}
}
