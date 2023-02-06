package util

import (
	"reflect"
	"strconv"
	"strings"
	"testing"
	"unsafe"

	"github.com/stretchr/testify/require"
)

func TestCopyString(t *testing.T) {
	str := "Hello, World!"
	strSlice := str[:5]
	strSliceCopy := CopyString(strSlice)
	require.Equal(t, strSlice, strSliceCopy)
	strDataPtr := (*reflect.StringHeader)(unsafe.Pointer(&str)).Data
	strSlicePtr := (*reflect.StringHeader)(unsafe.Pointer(&strSlice)).Data
	strSliceCopyPtr := (*reflect.StringHeader)(unsafe.Pointer(&strSliceCopy)).Data
	require.Equal(t, strDataPtr, strSlicePtr)
	require.NotEqual(t, strDataPtr, strSliceCopyPtr)
}

func copyStringV2(s string) string {
	b := []byte(s)
	return *(*string)(unsafe.Pointer(&b))
}

func BenchmarkCopyString(b *testing.B) {
	bigStringB := strings.Builder{}
	bigStringLen := 16 * 1024
	for i := 0; i < bigStringLen; i++ {
		bigStringB.WriteString(strconv.Itoa(i))
	}
	bigString := bigStringB.String()

	b.Run("copyString", func(b *testing.B) {
		var ret string
		b.ResetTimer()
		for i := 0; i < b.N; i++ {
			ret = CopyString(bigString[:i&(bigStringLen-1)])
		}
		_ = CopyString(ret)
	})

	b.Run("copyStringV2", func(b *testing.B) {
		var ret string
		b.ResetTimer()
		for i := 0; i < b.N; i++ {
			ret = copyStringV2(bigString[:i&(bigStringLen-1)])
		}
		_ = CopyString(ret)
	})
}

func TestGlobToRegexp(t *testing.T) {
	re1 := GlobsToRegexp([]string{"abc"})
	require.True(t, re1.MatchString("abc"))
	require.False(t, re1.MatchString("b"))
	require.False(t, re1.MatchString("abcd"))
	require.False(t, re1.MatchString("dabc"))
	re2 := GlobsToRegexp([]string{"ab*c", "de*"})
	require.True(t, re2.MatchString("abc"))
	require.False(t, re2.MatchString("b"))
	require.False(t, re2.MatchString("abcd"))
	require.False(t, re2.MatchString("dabc"))
	require.True(t, re2.MatchString("abdefc"))
	require.True(t, re2.MatchString("de"))
	require.True(t, re2.MatchString("def"))
	require.False(t, re2.MatchString("1de"))
}
