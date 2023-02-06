package netmath_test

import (
	"math"
	"testing"

	"a.yandex-team.ru/noc/puncher/lib/netmath"
)

func slowLog2Sum(logx, logy float64) float64 {
	return math.Log2(math.Pow(2, logx) + math.Pow(2, logy))
}

func TestLog2Sum(t *testing.T) {
	tests := []struct {
		x, y   float64
		result float64
	}{
		{0, 0, 1}, /* .../32 + .../32 = .../31 */
		{4, 4, 5}, /* .../28 + .../28 = .../27 */
	}
	for _, test := range tests {
		if result := netmath.Log2Sum(test.x, test.y); math.Abs(result-test.result) > 1e-6 {
			t.Errorf("Log2Sum(%f, %f) = %f, want %f", test.x, test.y, result, test.result)
		}
	}

	for x := 1; x < 200; x++ {
		for y := 1; y < 200; y++ {
			logx := math.Log2(float64(x))
			logy := math.Log2(float64(y))
			a := netmath.Log2Sum(logx, logy)
			b := slowLog2Sum(logx, logy)
			if math.Abs(a-b) >= 0.001 {
				t.Errorf("Log2(%d + %d) = Log2Sum(%f, %f) = %f, want %f", x, y, logx, logy, a, b)
			}
		}
	}

	for x := float64(1); x < 2e128; x *= 10 {
		for y := float64(1); y < 2e128; y *= 10 {
			logx := math.Log2(x)
			logy := math.Log2(y)
			a := netmath.Log2Sum(logx, logy)
			b := slowLog2Sum(logx, logy)
			if math.Abs(a-b) >= 0.00001 {
				t.Errorf("Log2(%f + %f) = Log2Sum(%f, %f) = %f, want %f", x, y, logx, logy, a, b)
			}
		}
	}
}

func BenchmarkLog2Sum(b *testing.B) {
	x, y := math.Log2(50), math.Log2(200)
	for i := 0; i < b.N; i++ {
		netmath.Log2Sum(x, y)
	}
}

func BenchmarkSlowLog2Sum(b *testing.B) {
	x, y := math.Log2(50), math.Log2(200)
	for i := 0; i < b.N; i++ {
		slowLog2Sum(x, y)
	}
}
