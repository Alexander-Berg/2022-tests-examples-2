package srcsetup

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func Test_newGeocoderArgs(t *testing.T) {
	type testCase struct {
		name    string
		path    string
		want    *geocoderArgs
		wantErr bool
	}
	cases := []testCase{
		{
			name: "normal",
			path: "?lat=37.863554&lon=55.917186&lang=ru",
			want: &geocoderArgs{
				latitude:  37.863554,
				longitude: 55.917186,
				language:  "ru",
			},
			wantErr: false,
		},
		{
			name: "English locale",
			path: "?lat=37.863554&lon=55.917186&lang=en",
			want: &geocoderArgs{
				latitude:  37.863554,
				longitude: 55.917186,
				language:  "en",
			},
			wantErr: false,
		},
		{
			name: "negative longitude",
			path: "?lat=-23.544808&lon=-46.633746&lang=ru",
			want: &geocoderArgs{
				latitude:  -23.544808,
				longitude: -46.633746,
				language:  "ru",
			},
			wantErr: false,
		},
		{
			name: "extra args",
			path: "?lat=37.863554&lon=55.917186&lang=ru&some_arg=1",
			want: &geocoderArgs{
				latitude:  37.863554,
				longitude: 55.917186,
				language:  "ru",
			},
			wantErr: false,
		},
		{
			name: "missing lang, fallback to default",
			path: "?lat=37.863554&lon=55.917186",
			want: &geocoderArgs{
				latitude:  37.863554,
				longitude: 55.917186,
				language:  "ru",
			},
			wantErr: false,
		},
		{
			name: "empty lang, fallback to default",
			path: "?lat=37.863554&lon=55.917186&lang=",
			want: &geocoderArgs{
				latitude:  37.863554,
				longitude: 55.917186,
				language:  "ru",
			},
			wantErr: false,
		},
		{
			name: "incorrect lang, fallback to default",
			path: "?lat=37.863554&lon=55.917186&lang=_not_a_valid_locale_",
			want: &geocoderArgs{
				latitude:  37.863554,
				longitude: 55.917186,
				language:  "ru",
			},
			wantErr: false,
		},
		{
			name:    "missing latitude",
			path:    "?lon=55.917186&lang=ru",
			wantErr: true,
		},
		{
			name:    "missing longitude",
			path:    "?lat=37.863554&lang=ru",
			wantErr: true,
		},
		{
			name:    "not a float number",
			path:    "?lat=some_value&lon=55.917186&lang=ru",
			wantErr: true,
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			actual, err := newGeocoderArgs(tt.path)
			if tt.wantErr {
				assert.Error(t, err)
				assert.Nil(t, actual)
			} else {
				assert.NoError(t, err)
				assert.Equal(t, tt.want, actual)
			}
		})
	}
}

func Test_isLocaleStringValid(t *testing.T) {
	type testCase struct {
		name   string
		locale string
		want   bool
	}

	cases := []testCase{
		{
			name:   "empty string",
			locale: "",
			want:   false,
		},
		{
			name:   "not a locale",
			locale: "_not_a_locale_",
			want:   false,
		},
		{
			name:   "Russian",
			locale: "ru",
			want:   true,
		},
		{
			name:   "Ukrainian",
			locale: "uk",
			want:   true,
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			actual := isLocaleStringValid(tt.locale)
			assert.Equal(t, tt.want, actual)
		})
	}
}
