package trigger

func Range(n int) []int {
	result := make([]int, 0)
	for i := 0; i < n; i++ {
		i := i
		result = append(result, i)
	}
	return result
}
