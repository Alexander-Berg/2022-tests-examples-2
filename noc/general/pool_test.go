package worker_test

import (
	"fmt"
	"testing"

	"a.yandex-team.ru/noc/puncher/lib/worker"
)

func TestCreatePool(t *testing.T) {
	tasks := []int{1, 2, 3, 4, 4}

	pool := worker.NewPool(3, int32(len(tasks)))

	for i, t := range tasks {
		pool.Jobs <- worker.Job{ID: i, Payload: t}
	}
	pool.Done()

	err := pool.Run(func(job worker.Job, results chan error) {
		fmt.Printf("%d: %d\n", job.Payload.(int), job.ID)
		results <- nil
	})
	if err != nil {
		fmt.Println(err)
	}
}
