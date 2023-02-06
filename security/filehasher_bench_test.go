package fim

import (
	"math/rand"
	"testing"
)

func BenchmarkHashingSha256(b *testing.B) {
	benchmarkHashing(b, Sha256)
}

func BenchmarkHashingBlake2b(b *testing.B) {
	benchmarkHashing(b, Blake2b)
}

func benchmarkHashing(b *testing.B, algorithm Algorithm) {
	h, err := newHasher(algorithm)
	if err != nil {
		b.Fatalf("error in newHasher: %v", err)
	}
	src := make([]byte, 256*1024)
	rand.Read(src)

	var result int
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_, err = h.Write(src)
		if err != nil {
			b.Fatalf("error in h.Write: %v", err)
		}
		result += int(h.Sum(nil)[0])
	}
}
