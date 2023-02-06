package hbaseapi

import (
	"fmt"
	"net/http"

	"github.com/jarcoal/httpmock"
)

func newTestClient() *Client {
	client, err := NewClient(Config{
		Consumer: "me, mario",
		Host:     "localhost",
		Port:     8201,
		Retries:  3,
		Timeout:  500,
	})
	if err != nil {
		panic(err)
	}

	return client
}

func newTestQueryHandler(body string, expectedQuery map[string]string) httpmock.Responder {
	return func(req *http.Request) (*http.Response, error) {
		if err := req.ParseForm(); err != nil {
			return httpmock.NewStringResponse(
				http.StatusBadRequest,
				fmt.Sprintf("Failed to parse form: %s", err),
			), nil
		}

		for key, value := range expectedQuery {
			if !req.Form.Has(key) {
				return httpmock.NewStringResponse(
					http.StatusBadRequest,
					fmt.Sprintf("Request query missing '%s'", key),
				), nil
			}
			actual := req.Form.Get(key)
			if value != actual {
				return httpmock.NewStringResponse(
					http.StatusBadRequest,
					fmt.Sprintf("Request query wrong '%s' value: expected %s, got %s", key, value, actual),
				), nil
			}
		}

		return httpmock.NewStringResponse(http.StatusOK, body), nil
	}
}
