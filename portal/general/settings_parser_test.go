package blocks

import (
	"encoding/base64"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/libs/utils/log3"
)

func Test_settingsParser_parse(t *testing.T) {
	type args struct {
		foldedCookie string
	}
	tests := []struct {
		name string
		args args
		want Settings
	}{
		{
			name: "zen is folded",
			args: args{
				foldedCookie: "AEA",
			},
			want: Settings{
				folded: map[ID]bool{
					InfinityZenID: true,
				},
			},
		},
		{
			name: "zen & Kinopoisk is folded",
			args: args{
				foldedCookie: "AGA",
			},
			want: Settings{
				folded: map[ID]bool{
					InfinityZenID: true,
					KinopoiskID:   true,
				},
			},
		},
		{
			name: "afisha, zen, kinopoisk, estate is folded",
			args: args{
				foldedCookie: "QGAAAAAAAEA",
			},
			want: Settings{
				folded: map[ID]bool{
					AfishaInsertsID: true,
					InfinityZenID:   true,
					KinopoiskID:     true,
					DivReserved1ID:  true,
				},
			},
		},
		{
			name: "afisha, autoru, autoru journal, estate, zen, kinopoisk is folded",
			args: args{
				foldedCookie: "QGAAAEAAAGg",
			},
			want: Settings{
				folded: map[ID]bool{
					AfishaInsertsID:  true,
					AutoruInsertsID:  true,
					InfinityZenID:    true,
					KinopoiskID:      true,
					DivReserved1ID:   true,
					DivKinopoiskNyID: true,
					61:               true,
				},
			},
		},
		{
			name: "1 byte full of zero",
			args: args{
				foldedCookie: base64.RawURLEncoding.EncodeToString([]byte{0, 0}),
			},
			want: Settings{
				folded: map[ID]bool{},
			},
		},
		{
			name: "1 byte, full of 1",
			args: args{
				foldedCookie: base64.RawURLEncoding.EncodeToString([]byte{255}),
			},
			want: Settings{
				folded: map[ID]bool{
					1: true,
					2: true,
					3: true,
					4: true,
					5: true,
					6: true,
					7: true,
					8: true,
				},
			},
		},
		{
			name: "empty string",
			args: args{
				foldedCookie: "",
			},
			want: Settings{},
		},
		{
			name: "undecodable base64",
			args: args{
				foldedCookie: "A;S;K",
			},
			want: Settings{},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			p := &settingsParser{
				logger: log3.NewLoggerStub(),
			}

			got := p.parse(tt.args.foldedCookie)

			require.Equal(t, tt.want, got)
		})
	}
}

func Test_settingsParser_Parse(t *testing.T) {
	type args struct {
		yaCookie models.YaCookies
	}
	tests := []struct {
		name string
		args args
		want Settings
	}{
		{
			name: "YaCookie is nil",
			args: args{
				yaCookie: models.YaCookies{},
			},
			want: Settings{},
		},
		{
			name: "No folded key in yp",
			args: args{
				yaCookie: models.YaCookies{
					Yp: models.YCookie{
						Subcookies: map[string]models.YSubcookie{
							"test": {
								Name:   "test",
								Value:  "1",
								Expire: 128904120948,
							},
						},
					},
				},
			},
			want: Settings{},
		},
		{
			name: "Got folded key, but encoded info is empty",
			args: args{
				yaCookie: models.YaCookies{
					Yp: models.YCookie{
						Subcookies: map[string]models.YSubcookie{
							"fblkv2": {
								Name:   "fblkv2",
								Value:  "AAA",
								Expire: 128904120948,
							},
						},
					},
				},
			},
			want: Settings{
				folded: map[ID]bool{},
			},
		},
		{
			name: "Got folded key, zen and afisha is folded",
			args: args{
				yaCookie: models.YaCookies{
					Yp: models.YCookie{
						Subcookies: map[string]models.YSubcookie{
							"fblkv2": {
								Name:   "fblkv2",
								Value:  "AGA",
								Expire: 128904120948,
							},
						},
					},
				},
			},
			want: Settings{
				folded: map[ID]bool{
					InfinityZenID: true,
					KinopoiskID:   true,
				},
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			p := &settingsParser{
				logger: log3.NewLoggerStub(),
			}

			got := p.Parse(tt.args.yaCookie)

			require.Equal(t, tt.want, got)
		})
	}
}
