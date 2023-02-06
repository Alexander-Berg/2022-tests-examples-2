package compare

import (
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/portal/avocado/libs/utils/unistat"
	"a.yandex-team.ru/portal/avocado/libs/utils/yabs"
)

func Test_findCGIArgsDiff(t *testing.T) {
	type testCase struct {
		name     string
		expected map[string]string
		got      map[string]string
		want     yabsURLCGIArgsDiff
	}

	cases := []testCase{
		{
			name: "equal",
			expected: map[string]string{
				"fruit": "apple",
				"town":  "korolyov",
			},
			got: map[string]string{
				"fruit": "apple",
				"town":  "korolyov",
			},
			want: yabsURLCGIArgsDiff{
				missing:  make([]string, 0),
				extra:    make([]string, 0),
				expected: make(map[string]string),
				got:      make(map[string]string),
			},
		},
		{
			name: "missing arg",
			expected: map[string]string{
				"fruit":   "apple",
				"town":    "korolyov",
				"country": "russia",
			},
			got: map[string]string{
				"fruit": "apple",
				"town":  "korolyov",
			},
			want: yabsURLCGIArgsDiff{
				missing:  []string{"country"},
				extra:    make([]string, 0),
				expected: make(map[string]string),
				got:      make(map[string]string),
			},
		},
		{
			name: "several missing args",
			expected: map[string]string{
				"fruit":   "apple",
				"town":    "korolyov",
				"country": "russia",
				"key_AAA": "value_AAA",
				"key_DDD": "value_DDD",
				"key_CCC": "value_CCC",
			},
			got: map[string]string{
				"fruit": "apple",
				"town":  "korolyov",
			},
			want: yabsURLCGIArgsDiff{
				missing:  []string{"country", "key_AAA", "key_CCC", "key_DDD"},
				extra:    make([]string, 0),
				expected: make(map[string]string),
				got:      make(map[string]string),
			},
		},
		{
			name: "extra arg",
			expected: map[string]string{
				"fruit": "apple",
				"town":  "korolyov",
			},
			got: map[string]string{
				"fruit":    "apple",
				"town":     "korolyov",
				"currency": "rub",
			},
			want: yabsURLCGIArgsDiff{
				missing:  make([]string, 0),
				extra:    []string{"currency"},
				expected: make(map[string]string),
				got:      make(map[string]string),
			},
		},
		{
			name: "mismatched arg",
			expected: map[string]string{
				"fruit": "apple",
				"town":  "korolyov",
				"os":    "iphone",
			},
			got: map[string]string{
				"fruit": "apple",
				"town":  "korolyov",
				"os":    "android",
			},
			want: yabsURLCGIArgsDiff{
				missing: make([]string, 0),
				extra:   make([]string, 0),
				expected: map[string]string{
					"os": "iphone",
				},
				got: map[string]string{
					"os": "android",
				},
			},
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			c := yabsURLComparator{}
			gotDiff := c.findCGIArgsDiff(tt.expected, tt.got)
			assert.Equal(t, tt.want, gotDiff)
		})
	}
}

func Test_yabsURLComparator_compareYabsURLs(t *testing.T) {
	tests := []struct {
		name     string
		expected yabs.Request
		got      yabs.Request
		wantErr  bool
		want     string
	}{
		{
			name: "equal",
			expected: yabs.Request{
				Host: "yandex.ru",
				Path: "/yabs",
				CGIArgs: map[string]string{
					"os": "ios",
				},
			},
			got: yabs.Request{
				Host: "yandex.ru",
				Path: "/yabs",
				CGIArgs: map[string]string{
					"os": "ios",
				},
			},
		},
		{
			name: "different host, extra and different cgi",
			expected: yabs.Request{
				Host: "yandex.ru",
				Path: "/yabs",
				CGIArgs: map[string]string{
					"os": "ios",
				},
			},
			got: yabs.Request{
				Host: "mail.ru",
				Path: "/yabs",
				CGIArgs: map[string]string{
					"os":  "android",
					"pet": "dog",
				},
			},
			wantErr: true,
			want:    "diff: ([ExpectedYabsURLHost], [GotYabsURLHost], [ExtraYabsURLArgs], [ExpectedYabsURLArgs], [GotYabsURLArgs])",
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)

			c := newYabsURLComparator(unistat.NewRegistry("test"))

			expectedGetterMock := NewMockyabsURLGetter(ctrl)
			expectedGetterMock.EXPECT().GetYabsURL().Return(tt.expected).Times(1)
			gotGetterMock := NewMockyabsURLGetter(ctrl)
			gotGetterMock.EXPECT().GetYabsURL().Return(tt.got).Times(1)

			err := c.compareYabsURLs(expectedGetterMock, gotGetterMock)
			if tt.wantErr {
				require.Error(t, err)
				additionalErr, ok := err.(errorTemplated)
				require.True(t, ok)

				template, _ := additionalErr.GetTemplated()
				require.Equal(t, tt.want, template)
			} else {
				require.NoError(t, err)
			}
		})
	}
}
