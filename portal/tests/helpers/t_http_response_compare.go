package helpers

import (
	protoanswers "a.yandex-team.ru/apphost/lib/proto_answers"
)

func THttpResponseCompare(expected *protoanswers.THttpResponse, got *protoanswers.THttpResponse) bool {
	if expected.StatusCode != got.StatusCode {
		return false
	}

	if len(expected.Headers) != len(got.Headers) {
		return false
	}

	for i := 0; i < len(expected.Headers); i++ {
		if expected.Headers[i].Name != got.Headers[i].Name || expected.Headers[i].Value != got.Headers[i].Value {
			return false
		}
	}

	if len(expected.Content) != len(got.Content) {
		return false
	}

	for i := 0; i < len(expected.Content); i++ {
		if expected.Content[i] != got.Content[i] {
			return false
		}
	}

	return expected.IsSdchEncoded == got.IsSdchEncoded
}
