package restclient_test

import (
	"net/http"
	"net/http/httptest"
	"testing"

	"a.yandex-team.ru/noc/puncher/lib/restclient"
)

func TestGetJSONSuccss(t *testing.T) {
	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Add("Content-Type", "application/json")
		_, _ = w.Write([]byte(`{"answer":42}`))
	}))
	defer ts.Close()

	c := restclient.Client{
		URL: ts.URL,
	}
	var response struct {
		Answer int `json:"answer"`
	}
	resp, err := c.Get("/", nil, &response, nil)
	if err != nil {
		t.Error("error:", err)
	}
	if resp.StatusCode != 200 {
		t.Errorf("StatusCode == %d, want 200", resp.StatusCode)
	}
	if response.Answer != 42 {
		t.Errorf("Answer == %d, want 42", response.Answer)
	}
}

func TestGetJSONError(t *testing.T) {
	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Add("Content-Type", "application/json")
		w.WriteHeader(418)
		_, _ = w.Write([]byte(`{"message":"I'm a teapot"}`))
	}))
	defer ts.Close()

	c := restclient.Client{
		URL: ts.URL,
	}
	var failure struct {
		Message string `json:"message"`
	}
	resp, err := c.Get("/", nil, nil, &failure)
	if err != nil {
		t.Error("error:", err)
	}
	if resp.StatusCode != 418 {
		t.Errorf("StatusCode == %d, want 418", resp.StatusCode)
	}
	if failure.Message != "I'm a teapot" {
		t.Errorf("Message == %q, want %q", failure.Message, "I'm a teapot")
	}
}
