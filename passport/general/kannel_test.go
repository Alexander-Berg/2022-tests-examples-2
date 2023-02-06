package kannel

import (
	"context"
	"net/http"
	"net/http/httptest"
	"path"
	"testing"
	"time"

	"a.yandex-team.ru/library/go/test/yatest"
	"a.yandex-team.ru/passport/infra/daemons/yasmsd/internal/utils"
	shared_utils "a.yandex-team.ru/passport/shared/golibs/utils"
)

const TestKannelHost = "kannel-test-x1.passport.yandex.net"

const KannelQueueSizeThreshold = 100
const KannelPingInterval = time.Second
const KannelPingTimeout = 100 * time.Millisecond

func getKannelConfig(kannelURL1 string, kannelURL2 string) *Config {
	return &Config{
		Hosts:          []string{kannelURL1, kannelURL2},
		PingInterval:   shared_utils.Duration{Duration: time.Second},
		PingTimeout:    shared_utils.Duration{Duration: 100 * time.Millisecond},
		StatusTimeout:  shared_utils.Duration{Duration: 100 * time.Millisecond},
		StatusInterval: shared_utils.Duration{Duration: time.Second},

		QueueSizeThreshold: 100,
	}
}

// Получение тестового XML статуса.
func kannelTestStatusXMLPath() string {
	return path.Join(yatest.SourcePath("passport/infra/daemons/yasmsd/internal/testdata"), "kannel_test.xml")
}

func kannelTestStatusXML() (string, error) {
	return utils.FileContents(kannelTestStatusXMLPath())
}

// Парсинг тестового XML статуса.
func kannelTestStatus(host string) (*KannelStatus, error) {
	data, err := kannelTestStatusXML()
	if err != nil {
		return nil, err
	}

	return parseKannelStatus([]byte(data), host)
}

func TestKannelCoding(t *testing.T) {
	var c []byte

	// nil
	if kannelCoding(c) != KannelConding7Bit {
		t.Errorf(`expected 7bit`)
	}

	// коды до 0x20 (пробел) не представлены в gsm
	// за исключением кодов <CR> / <LF> / <FF> (см. ниже)
	c = make([]byte, Kannel7BitSegmentSize)
	if kannelCoding(c) != KannelCodingUCS2 {
		t.Errorf(`expected ucs-2`)
	}

	// 160 пробелов (7 bit ascii)
	for i := 0; i < Kannel7BitSegmentSize; i++ {
		c[i] = 0x20
	}

	if kannelCoding(c) != KannelConding7Bit {
		t.Errorf(`expected 7bit`)
	}

	// "`" (GRAVE ACCENT) не может быть представлен в gsm
	c[0] = 0x60
	if kannelCoding(c) != KannelCodingUCS2 {
		t.Errorf(`expected ucs-2`)
	}

	// 0x7f = <DEL>, хотя все еще 7 bit
	c[0] = 0x7f
	if kannelCoding(c) != KannelCodingUCS2 {
		t.Errorf(`expected ucs-2`)
	}

	// спец-символы перевода каретки / страницы
	for _, b := range []uint8{0x0a, 0x0c, 0x0d} {
		c[0] = b
		if kannelCoding(c) != KannelConding7Bit {
			t.Errorf(`expected ucs-2`)
		}
	}

	// превышение длины в 160 байт
	c[0] = 0x20
	c = append(c, 0x20)
	if kannelCoding(c) != KannelCodingUCS2 {
		t.Errorf(`expected ucs-2`)
	}
}

func TestKannelRequest(t *testing.T) {
	checkFail := func(url, id string) {
		ctx, cancel := context.WithTimeout(context.Background(), KannelPingTimeout)
		defer cancel()

		actual, err := kannelRequest(ctx, nil, url, http.StatusOK)
		if err == nil {
			t.Errorf(`id = '%s' must throw error but result is: '%s'`, id, string(actual))
		}
	}

	// неверный хост
	checkFail("http://[::1", "invalid host")

	// 302 (не должны ходить за редиректом)
	server302 := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusFound)
	}))
	defer server302.Close()
	checkFail(server302.URL, "HTTP-302")

	// 403 (авторизация?)
	server403 := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusForbidden)
		_, _ = w.Write([]byte("Forbidden"))
	}))
	defer server403.Close()
	checkFail(server403.URL, "HTTP-403")

	// 404 (хост не найден)
	server404 := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusNotFound)
	}))
	defer server404.Close()
	checkFail(server404.URL, "HTTP-404")

	// таймаут
	server499 := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		time.Sleep(2 * KannelPingTimeout)
	}))
	defer server499.Close()
	checkFail(server499.URL, "timeout")
}

func TestKannelPing(t *testing.T) {
	check := func(url, id string, expected bool) {
		actual, err := kannelPing(context.Background(), nil, url)
		if !expected && err == nil {
			t.Errorf(`id = '%s' must throw error but result is: %v`, id, actual)
		} else if expected && err != nil {
			t.Errorf(`id = '%s' error: %s`, id, err)
		}

		if actual != expected {
			t.Errorf(`id = '%s', expected: %v, actual: %v`, id, expected, actual)
		}
	}

	server200 := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		_, _ = w.Write(KannelPingResponse)
	}))
	defer server200.Close()
	check(server200.URL, "ok", true)

	server403 := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusForbidden)
	}))
	defer server403.Close()
	check(server403.URL, "HTTP-403", false)
}

func TestParseKannelStatus(t *testing.T) {
	status, err := kannelTestStatus(TestKannelHost)
	if err != nil {
		t.Fatal(err)
	}

	if len(status.gates) != 8 {
		t.Error("expected 8")
	}

	// TODO: проверить остальные поля
}

func TestKannelStatus(t *testing.T) {
	check := func(url, id string, expected bool) {
		actual, err := kannelStatus(context.Background(), nil, url)
		if !expected && err == nil {
			t.Errorf(`id = '%s' must throw error but result is: %v`, id, actual)
		} else if expected && err != nil {
			t.Errorf(`id = '%s' error: %s`, id, err)
		}
	}

	server200 := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		xml, _ := kannelTestStatusXML()
		_, _ = w.Write([]byte(xml))
	}))
	defer server200.Close()
	check(server200.URL, "ok", true)

	server403 := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusForbidden)
	}))
	defer server403.Close()
	check(server403.URL, "HTTP-403", false)
}
