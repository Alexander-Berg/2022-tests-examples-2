package main

import "net/http"

func main() {
	http.HandleFunc("/ping", func(w http.ResponseWriter, _ *http.Request) {
		_, _ = w.Write([]byte("OK"))
	})

	err := http.ListenAndServe(":80", nil)
	if err != nil {
		panic(err.Error())
	}
}
