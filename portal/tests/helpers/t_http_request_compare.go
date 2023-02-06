package helpers

import (
	"testing"

	"github.com/google/go-cmp/cmp"
	"github.com/stretchr/testify/assert"
	"google.golang.org/protobuf/testing/protocmp"

	protoanswers "a.yandex-team.ru/apphost/lib/proto_answers"
)

func THttpRequestAssertEqual(t *testing.T, expected *protoanswers.THttpRequest, actual *protoanswers.THttpRequest) {
	if diff := cmp.Diff(expected, actual, protocmp.Transform()); diff != "" {
		assert.FailNow(t, "proto THttpRequests are different", "%v", diff)
	}
}

func THttpRequestCompare(expected *protoanswers.THttpRequest, got *protoanswers.THttpRequest) bool {
	if expected.Method != got.Method {
		return false
	}

	if expected.Scheme != got.Scheme {
		return false
	}

	if expected.Path != got.Path {
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

	return true
}
