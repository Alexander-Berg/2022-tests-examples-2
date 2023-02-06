package bytebuffer

import (
	"fmt"
	"testing"

	"github.com/stretchr/testify/require"
)

func TestBytes(t *testing.T) {
	b := newBufferPool(128, 10)
	bufs := make([][]byte, 100)
	for i := 0; i < 100; i++ {
		t.Run(fmt.Sprintf("get_%d", i), func(t *testing.T) {
			buf := b.Get()
			require.Len(t, buf, 128)

			bufs[i] = buf
		})
	}

	for i := 0; i < 100; i++ {
		t.Run(fmt.Sprintf("put_%d", i), func(t *testing.T) {
			b.Put(bufs[i])
		})
	}
}
