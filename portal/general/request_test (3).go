package lbs

import (
	"net/url"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestNewRequest(t *testing.T) {
	type args struct {
		cgi url.Values
	}
	tests := []struct {
		name string
		args args
		want *Request
	}{
		{
			name: "success wifi and cellid",
			args: args{
				cgi: map[string][]string{
					"wifi":   {"123"},
					"cellid": {"456"},
				},
			},
			want: &Request{
				Params: Params{
					Wifi:   []string{"123"},
					CellID: []string{"456"},
				},
				Headers: make(map[string]string),
				URI:     "/getlocation",
				Method:  "GET",
			},
		},
		{
			name: "success wifi",
			args: args{
				cgi: map[string][]string{
					"wifi": {"123"},
				},
			},
			want: &Request{
				Params: Params{
					Wifi: []string{"123"},
				},
				Headers: make(map[string]string),
				URI:     "/getlocation",
				Method:  "GET",
			},
		},
		{
			name: "success cellid",
			args: args{
				cgi: map[string][]string{
					"cellid": {"456"},
				},
			},
			want: &Request{
				Params: Params{
					CellID: []string{"456"},
				},
				Headers: make(map[string]string),
				URI:     "/getlocation",
				Method:  "GET",
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			assert.Equalf(t, tt.want, NewRequest(tt.args.cgi), "NewRequest(%v)", tt.args.cgi)
		})
	}
}
