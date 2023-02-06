package util

import (
	"math/rand"
	"testing"

	"github.com/stretchr/testify/assert"
)

const maxN = 12

func Test_LCS(t *testing.T) {
	randomX := randomString()
	randomY := randomString()
	type args struct {
		x string
		y string
	}
	tests := []struct {
		name string
		args args
		want int
	}{
		{
			name: "Strings are equal",
			args: args{
				x: "akjasndkajfhudhfoghcmshguihsfuhgisuhrgkm",
				y: "akjasndkajfhudhfoghcmshguihsfuhgisuhrgkm",
			},
			want: len("akjasndkajfhudhfoghcmshguihsfuhgisuhrgkm"),
		},
		{
			name: "One string is empty",
			args: args{
				x: "",
				y: "fkfjajlkglgdajgakjahqiguhgqoui30418198__-+okfkfl",
			},
			want: 0,
		},
		{
			name: "Random test",
			args: args{
				x: "jf98wunv98y4y",
				y: "dfkljwu02-I24",
			},
			want: 4,
		},
		{
			name: "Generated test",
			args: args{
				x: randomX,
				y: randomY,
			},
			want: naiveLcs(randomX, randomY),
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			assert.Equalf(t, tt.want, LCS(tt.args.x, tt.args.y), "LCS(%v, %v)", tt.args.x, tt.args.y)
		})
	}
}

func randomString() string {
	var x string
	for i := 0; i < rand.Intn(maxN+1); i++ {
		x += string('a' + rune(rand.Intn(26)))
	}
	return x
}

func naiveLcs(x, y string) int {
	n := len(x)
	m := len(y)
	max := 0
	for maskX := 0; maskX < (1 << n); maskX++ {
		for maskY := 0; maskY < (1 << m); maskY++ {
			var a string
			var b string
			for i := 0; i < n; i++ {
				if (maskX & (1 << i)) != 0 {
					a += string(x[i])
				}
			}
			for i := 0; i < m; i++ {
				if (maskY & (1 << i)) != 0 {
					b += string(y[i])
				}
			}
			if a == b && len(a) > max {
				max = len(a)
			}
		}
	}
	return max
}
