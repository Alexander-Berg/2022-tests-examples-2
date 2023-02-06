package yacsrf_test

import (
	"testing"
	"time"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/security/libs/go/yacsrf"
)

func TestGenerateValidate(t *testing.T) {
	csrf, err := yacsrf.New(yacsrf.Options{
		SecretKey: "test_test_test",
		TTL:       10,
	})
	if !assert.NoError(t, err) {
		return
	}

	token, err := csrf.Generate(1, "1234")
	if !assert.NoError(t, err) {
		return
	}

	err = csrf.Validate(token, 1, "1234")
	if !assert.NoError(t, err) {
		return
	}
}

func TestWrongKey(t *testing.T) {
	csrfA, err := yacsrf.New(yacsrf.Options{
		SecretKey: "test_test_test_a",
		TTL:       10,
	})
	if !assert.NoError(t, err) {
		return
	}

	csrfB, err := yacsrf.New(yacsrf.Options{
		SecretKey: "test_test_test_b",
		TTL:       10,
	})
	if !assert.NoError(t, err) {
		return
	}

	token, err := csrfA.Generate(2, "1234")
	if !assert.NoError(t, err) {
		return
	}

	err = csrfB.Validate(token, 2, "1234")
	if !assert.Error(t, err) {
		return
	}
}

func TestExpires(t *testing.T) {
	csrf, err := yacsrf.New(yacsrf.Options{
		SecretKey: "test_test_test",
		TTL:       1,
	})
	if !assert.NoError(t, err) {
		return
	}

	token, err := csrf.Generate(1, "1234")
	if !assert.NoError(t, err) {
		return
	}

	time.Sleep(10 * time.Second)

	err = csrf.Validate(token, 1, "1234")
	if !assert.Error(t, err) {
		return
	}
}

func TestWrongUID(t *testing.T) {
	csrf, err := yacsrf.New(yacsrf.Options{
		SecretKey: "test_test_test",
		TTL:       10,
	})
	if !assert.NoError(t, err) {
		return
	}

	token, err := csrf.Generate(1, "1234")
	if !assert.NoError(t, err) {
		return
	}

	err = csrf.Validate(token, 2, "1234")
	if !assert.Error(t, err) {
		return
	}
}

func TestWrongYandexuid(t *testing.T) {
	csrf, err := yacsrf.New(yacsrf.Options{
		SecretKey: "test_test_test",
		TTL:       10,
	})
	if !assert.NoError(t, err) {
		return
	}

	token, err := csrf.Generate(1, "1234")
	if !assert.NoError(t, err) {
		return
	}

	err = csrf.Validate(token, 1, "4321")
	if !assert.Error(t, err) {
		return
	}
}
