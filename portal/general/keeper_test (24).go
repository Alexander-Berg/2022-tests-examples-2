package its

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/portal/avocado/morda-go/pkg/its"
)

func Test_keeper_parse(t *testing.T) {
	tests := []struct {
		name    string
		arg     string
		want    *its.Options
		errFunc require.ErrorAssertionFunc
	}{
		{
			name: "comparator options",
			arg: `{
				"MordaBackendOptions": {
					"ComparatorOptions": {
						"First": {
							"DefaultComponentPercentage": 50,
							"ComponentsPercentage": {
								"Auth": 5,
								"Clid": 100,
								"Geo": 5,
								"YandexUID": 100,
								"YabsURL": 1
							}
						},
						"Second": {
							"DefaultComponentPercentage": 70,
							"ComponentsPercentage": {
								"ABFlags": 5,
								"BigB": 15,
								"Device": 100,
								"Geo": 50
							}
						}
					}
				}
			}`,
			want: &its.Options{
				MordaBackendOptions: its.MordaBackendOptions{
					ComparatorOptions: its.ComparatorOptions{
						First: its.ComparatorOptionsBase{
							DefaultComponentPercentage: 50,
							ComponentsPercentage: map[string]int{
								"Auth":      5,
								"Clid":      100,
								"Geo":       5,
								"YandexUID": 100,
								"YabsURL":   1,
							},
						},
						Second: its.ComparatorOptionsBase{
							DefaultComponentPercentage: 70,
							ComponentsPercentage: map[string]int{
								"ABFlags": 5,
								"BigB":    15,
								"Device":  100,
								"Geo":     50,
							},
						},
					},
				},
			},
			errFunc: require.NoError,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			k := &keeper{}
			got, err := k.parse([]byte(tt.arg))
			tt.errFunc(t, err)
			assert.Equal(t, tt.want, got)
		})
	}
}
