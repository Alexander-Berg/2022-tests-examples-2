package helpers

import (
	"bytes"

	"a.yandex-team.ru/portal/avocado/proto/morda_data"
)

func ProtoCookieCompare(expected *morda_data.Cookie, got *morda_data.Cookie) bool {
	if len(expected.Parsed) != len(got.Parsed) {
		return false
	}

	for k, v := range expected.Parsed {
		gotValue, ok := got.Parsed[k]
		if !ok {
			return false
		}

		if !ProtoCookieValueCompare(v, gotValue) {
			return false
		}
	}

	return true
}

func ProtoCookieValueCompare(expected *morda_data.Cookie_Value, got *morda_data.Cookie_Value) bool {
	if len(expected.Values) != len(got.Values) {
		return false
	}

	for i, v := range expected.Values {
		if !bytes.Equal(v, got.Values[i]) {
			return false
		}
	}

	return true
}
