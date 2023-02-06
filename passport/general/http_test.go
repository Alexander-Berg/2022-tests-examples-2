package kannel

import (
	"testing"
)

func TestFQDNFromUrl(t *testing.T) {
	check := func(host, expected string) {
		actual := FqdnFromURL(host)
		if actual != expected {
			t.Errorf(`hostFromUrl("%s"), expected: "%s", actual: "%s"`, host, expected, actual)
		}
	}

	check("kannel-x1", "kannel-x1")

	check("kannel-x1.passport.yandex.net", "kannel-x1.passport.yandex.net")
	check("kannel-x1.passport.yandex.net:443", "kannel-x1.passport.yandex.net")

	check("http://kannel-x1.passport.yandex.net", "kannel-x1.passport.yandex.net")
	check("https://kannel-x1.passport.yandex.net:443", "kannel-x1.passport.yandex.net")

	check("http://kannel-x1.passport.yandex.net/ping.html", "kannel-x1.passport.yandex.net")
	check("https://kannel-x1.passport.yandex.net:443/ping.html", "kannel-x1.passport.yandex.net")
}
