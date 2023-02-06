package s3

import (
	"errors"
	"testing"

	"github.com/stretchr/testify/require"
)

func TestThreadPool(t *testing.T) {
	pool := NewThreadPool(10, 0, "test1")
	var futures []*Future
	for i := 0; i < 10000; i++ {
		i := i
		future := pool.Submit(func() (interface{}, error) {
			if i%2 == 0 {
				return i * i, nil
			} else if i%100 == 0 {
				panic("hello, panic")
			} else {
				return nil, errors.New("bad index")
			}
		})
		futures = append(futures, future)
	}

	for i, future := range futures {
		v, err := future.Get()
		if i%2 == 0 {
			require.Equal(t, i*i, v.(int))
			require.NoError(t, err)
		} else if i%100 == 0 {
			require.Error(t, err)
			require.Contains(t, err.Error(), "hello, panic")
		} else {
			require.Error(t, err)
			require.Contains(t, err.Error(), "bad index")
		}
	}
}
