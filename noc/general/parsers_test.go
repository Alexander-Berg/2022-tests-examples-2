package descriptionparser

import (
	"reflect"
	"testing"
	"time"
)

func Test_parseDateTime(t *testing.T) {
	type args struct {
		dateString string
		timeString string
	}
	tests := []struct {
		name    string
		args    args
		want    time.Time
		wantErr bool
	}{
		{
			name: "common format",
			args: args{
				dateString: "2021-12-13",
				timeString: "18:10",
			},
			want:    timeMust(t, "2021-12-13T18:10:00+03:00"),
			wantErr: false,
		},
		// можно указывать время через точку, см: NOCDEV-6603
		{
			name: "time with dot separator",
			args: args{
				dateString: "2021-12-13",
				timeString: "18.10",
			},
			want:    timeMust(t, "2021-12-13T18:10:00+03:00"),
			wantErr: false,
		},
		// можно указывать время через дефис, см: NOCDEV-6603
		{
			name: "time with dash separator",
			args: args{
				dateString: "2021-12-13",
				timeString: "18-10",
			},
			want:    timeMust(t, "2021-12-13T18:10:00+03:00"),
			wantErr: false,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := parseDateTime(tt.args.dateString, tt.args.timeString)
			if (err != nil) != tt.wantErr {
				t.Errorf("parseDateTime() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if !reflect.DeepEqual(got, tt.want) {
				t.Errorf("parseDateTime() = %v, want %v", got, tt.want)
			}
		})
	}
}
