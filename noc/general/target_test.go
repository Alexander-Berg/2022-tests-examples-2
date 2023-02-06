package models_test

import (
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/noc/puncher/models"
)

func TestNormalize(t *testing.T) {
	target := models.Target{
		Responsibles: []string{"z", "c", "d"},
		Aliases:      []string{"ss", "zz", "aa"},
		Sections:     []string{"VV", "AA", "YY"},
	}
	anotherTarget := target

	// Normalize should be goroutine safe
	results := make(chan models.Target)
	for _, tg := range []models.Target{target, anotherTarget} {
		go func(tg models.Target) {
			tg.Normalize()
			results <- tg
		}(tg)
	}

	for _, tg := range []models.Target{<-results, <-results} {
		assert.Equal(t, []string{"c", "d", "z"}, tg.Responsibles)
		assert.Equal(t, []string{"aa", "ss", "zz"}, tg.Aliases)
		assert.Equal(t, []string{"AA", "VV", "YY"}, tg.Sections)
	}

}

func TestNormalizeIP(t *testing.T) {
	cases := []struct {
		input    string
		expected string
	}{
		{
			"127.0.0.1",
			"127.0.0.1",
		},
		{
			"027.000.0.001",
			"",
		},
		{
			"027.0.0.001/08",
			"",
		},
		{
			"2a0d:d6c0:0:ff1a::21b",
			"2a0d:d6c0:0:ff1a::21b",
		},
		{
			"2a0d:06c0:0:ff1a::021b",
			"",
		},
		{
			"0031@2a02:6b8:0c00::/040",
			"",
		},
		{
			"yandex.ru",
			"",
		},
		{
			"_YANDEXNETS_",
			"",
		},
	}
	for _, c := range cases {
		assert.Equal(t, c.expected, models.NormalizeIP(c.input))
	}
}
