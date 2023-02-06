package topnews

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func createStubNewTabs(rubrics []string, customRubricAlias string) []tab {
	tabs := make([]tab, len(rubrics))

	for i, rubric := range rubrics {
		tabs[i].Alias = rubric
		switch rubric {
		case "Moscow":
			tabs[i].ID = 213
			tabs[i].URL = "https://yandex.ru/news/region/Moscow"
		case "Saint_Petersburg":
			tabs[i].ID = 2
			tabs[i].URL = "https://yandex.ru/news/region/Saint_Petersburg"
		case "custom":
			tabs[i].Alias = customRubricAlias
			tabs[i].IsCustomTab = true
		}
	}

	return tabs
}

func collectRubricsFromNewsTabs(tabs []tab) []string {
	topics := make([]string, len(tabs))

	for i, tab := range tabs {
		topics[i] = tab.Alias
	}

	return topics
}

func TestSortTopnewsTabs(t *testing.T) {
	testCases := []struct {
		caseName        string
		inputTabRubrics []string
		orderedRubrics  []string
		expected        []string
	}{
		{
			caseName:        "no reordering",
			inputTabRubrics: []string{"index", "Moscow", "auto", "business", "computers", "culture", "incident", "politics", "science", "society", "sport", "world"},
			orderedRubrics:  nil,
			expected:        []string{"index", "Moscow", "auto", "business", "computers", "culture", "incident", "politics", "science", "society", "sport", "world"},
		},
		{
			caseName:        "all valid rubrics",
			inputTabRubrics: []string{"index", "Moscow", "Saint_Petersburg", "auto", "business", "computers", "culture", "incident", "politics", "science", "society", "sport", "world"},
			orderedRubrics:  []string{"index", "region", "home_region", "politics", "society", "business", "world", "sport", "incident", "culture", "computers", "science", "auto"},
			expected:        []string{"index", "Moscow", "Saint_Petersburg", "politics", "society", "business", "world", "sport", "incident", "culture", "computers", "science", "auto"},
		},
		{
			caseName:        "duplicated rubric",
			inputTabRubrics: []string{"index", "Moscow", "auto", "business", "computers", "culture", "incident", "politics", "science", "society", "sport", "world"},
			orderedRubrics: []string{
				"index", "region", "politics",
				"society", "society", "society",
				"business", "world", "sport", "incident", "culture", "computers", "society", "science", "auto",
			},
			expected: []string{"index", "Moscow", "politics", "society", "business", "world", "sport", "incident", "culture", "computers", "science", "auto"},
		},
		{
			caseName:        "missed rubrics",
			inputTabRubrics: []string{"index", "Moscow", "auto", "business", "computers", "culture", "incident", "politics", "science", "society", "sport", "world"},
			orderedRubrics:  []string{"index", "region", "politics", "society", "business", "world", "sport"},
			expected:        []string{"index", "Moscow", "politics", "society", "business", "world", "sport"},
		},
		{
			caseName:        "extra rubric",
			inputTabRubrics: []string{"index", "Moscow", "auto", "business", "computers", "culture", "incident", "politics", "science", "society", "sport", "world"},
			orderedRubrics: []string{"index", "region", "politics", "society", "business", "world", "sport",
				"space", "hockey",
				"incident", "culture", "computers", "science", "auto"},
			expected: []string{"index", "Moscow", "politics", "society", "business", "world", "sport", "incident", "culture", "computers", "science", "auto"},
		},
		{
			caseName:        "personal_feed",
			inputTabRubrics: []string{"index", "Moscow", "auto", "business", "personal_feed"},
			orderedRubrics:  []string{"index", "region", "personal", "auto", "business"},
			expected:        []string{"index", "Moscow", "personal_feed", "auto", "business"},
		},
		{
			caseName:        "custom rubric",
			inputTabRubrics: []string{"index", "Moscow", "auto", "custom", "business"},
			orderedRubrics:  []string{"index", "region", "custom", "auto", "business", "politics"},
			expected:        []string{"index", "Moscow", "politics", "auto", "business"},
		},
	}

	for _, testCase := range testCases {
		t.Run(testCase.caseName, func(t *testing.T) {
			newsTabs := createStubNewTabs(testCase.inputTabRubrics, "politics")
			orderedTabs := sortRubricTabs(newsTabs, testCase.orderedRubrics)
			sortedRubrics := collectRubricsFromNewsTabs(orderedTabs)
			assert.Equal(t, testCase.expected, sortedRubrics)
		})
	}
}
