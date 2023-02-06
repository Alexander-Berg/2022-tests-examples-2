package debug_test

import (
	"fmt"

	"a.yandex-team.ru/noc/puncher/lib/debug"
)

func ExamplePrint() {
	type aType struct{ s string }
	x := struct {
		a aType
	}{
		a: aType{s: "hello"},
	}
	fmt.Println(debug.Print(x))

	// Output:
	// {a:{s:hello}}
}
