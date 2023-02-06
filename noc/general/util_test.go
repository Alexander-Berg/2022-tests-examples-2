package targetutil_test

import (
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/noc/puncher/models"
	"a.yandex-team.ru/noc/puncher/models/modelstest"
	"a.yandex-team.ru/noc/puncher/models/targetutil"
)

func TestAppend(t *testing.T) {
	tests := []struct {
		a      []models.Target
		b      []models.Target
		result []models.Target
	}{
		{
			[]models.Target{modelstest.Alice},
			[]models.Target{modelstest.Bob},
			[]models.Target{modelstest.Alice, modelstest.Bob},
		},
		{
			nil,
			[]models.Target{modelstest.Alice},
			[]models.Target{modelstest.Alice},
		},
		{
			[]models.Target{modelstest.Alice, modelstest.Bob},
			[]models.Target{modelstest.Eve, modelstest.Alice},
			[]models.Target{modelstest.Alice, modelstest.Bob, modelstest.Eve},
		},
	}
	for _, test := range tests {
		result := targetutil.Append(test.a, test.b...)
		assert.Equal(t, result, test.result)
	}
}

func TestDifference(t *testing.T) {
	tests := []struct {
		a      []models.Target
		b      []models.Target
		result []models.Target
	}{
		{
			[]models.Target{modelstest.Alice},
			[]models.Target{modelstest.Bob},
			[]models.Target{modelstest.Alice},
		},
		{
			[]models.Target{modelstest.Alice},
			[]models.Target{modelstest.Alice},
			nil,
		},
		{
			[]models.Target{modelstest.Alice, modelstest.Bob},
			[]models.Target{modelstest.Eve, modelstest.Alice},
			[]models.Target{modelstest.Bob},
		},
	}
	for _, test := range tests {
		result := targetutil.Difference(test.a, test.b)
		assert.Equal(t, result, test.result)
	}
}

func TestIntersect(t *testing.T) {
	tests := []struct {
		a      []models.Target
		b      []models.Target
		result []models.Target
	}{
		{
			[]models.Target{modelstest.Alice},
			[]models.Target{modelstest.Bob},
			nil,
		},
		{
			[]models.Target{modelstest.Alice},
			[]models.Target{modelstest.Alice},
			[]models.Target{modelstest.Alice},
		},
		{
			[]models.Target{modelstest.Alice, modelstest.Bob},
			[]models.Target{modelstest.Eve, modelstest.Alice},
			[]models.Target{modelstest.Alice},
		},
	}
	for _, test := range tests {
		result := targetutil.Intersect(test.a, test.b)
		assert.Equal(t, result, test.result)
	}
}

func TestIsSectionUpdateLegitimate(t *testing.T) {
	tests := []struct {
		name     string
		old      []string
		new      []string
		expected bool
	}{
		{
			"same is ok",
			[]string{"OTHERSECTION", "SOMESECTION"},
			[]string{"SOMESECTION", "OTHERSECTION"},
			true,
		},
		{
			"pseudo sections are ignored",
			[]string{"OTHERSECTION", "SOMESECTION", models.PseudoSectionExternal},
			[]string{models.PseudoSectionRoot, "SOMESECTION", "OTHERSECTION"},
			true,
		},
		{
			"different len is not ok",
			[]string{"SOMESECTION"},
			[]string{"SOMESECTION", "OTHERSECTION"},
			false,
		},
		{
			"new section is not ok",
			[]string{"SOMESECTION", "OTHERSECTION"},
			[]string{"SOMESECTION", "THIRDSECTION"},
			false,
		},
	}
	for _, test := range tests {
		assert.Equalf(
			t,
			test.expected,
			targetutil.IsSectionUpdateLegitimate(test.old, test.new),
			"test: %s",
			test.name,
		)
	}
}
