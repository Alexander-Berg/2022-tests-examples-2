package topnews

import (
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/portal/avocado/proto/topnews"
)

func TestExperimentsFlags(t *testing.T) {
	tests := []struct {
		name        string
		expected    string
		experiments string
		flags       string
	}{
		{
			name:        "Both exists",
			expected:    "&experiments=ex1%2Cex2%2Cex3&flags=flag_ab",
			experiments: "ex1,ex2,ex3",
			flags:       "flag_ab",
		},
		{
			name:        "Only experiments exist",
			expected:    "&experiments=ex1%2Cex2%2Cex3",
			experiments: "ex1,ex2,ex3",
			flags:       "",
		},
		{
			name:        "Only flags exist",
			expected:    "&flags=flagab",
			experiments: "",
			flags:       "flagab",
		},
		{
			name:        "Nothing exists",
			expected:    "",
			experiments: "",
			flags:       "",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			searchAppData := &topnews.TSearchAppData{
				Experiments: tt.experiments,
				Flags:       tt.flags,
			}
			topnewsRequest := topnews.TRequest{
				Common: &topnews.TCommon{
					Url:            "",
					ScaleFactor:    1,
					OrderedRubrics: []string{},
					Locale:         "",
				},
			}
			topnewsRequest.Data = &topnews.TRequest_SearchApp{SearchApp: searchAppData}

			got := addExperimentsFlagsToRequest(&topnewsRequest)

			require.Equal(t, tt.expected, got)
		})
	}
}

type data struct {
	Experiments string
	Flags       string
}

func TestIsExperimentOn(t *testing.T) {
	tests := []struct {
		name        string
		expected    bool
		iserror     bool
		experiments string
		flags       string
		flag        string
	}{
		{
			name:        "Not exists",
			expected:    false,
			iserror:     false,
			experiments: "exp1,exp2,exp3=1,exp4",
			flags:       "f1,f2,f3=a,f4=b",
			flag:        "",
		},
		{
			name:        "Exists in exp",
			expected:    false,
			iserror:     false,
			experiments: "exp1,exp2,exp3=1,exp4",
			flags:       "f1,f2,f3=a,f4=b",
			flag:        "exp1",
		},
		{
			name:        "Exists in exp 2",
			expected:    true,
			iserror:     false,
			experiments: "exp1,exp2=1,exp3=1,exp4",
			flags:       "f1,f2,f3=a,f4=b",
			flag:        "exp2",
		},
		{
			name:        "Exists in exp 3",
			expected:    true,
			iserror:     false,
			experiments: "exp1,exp2,exp3=1,exp4",
			flags:       "f1,f2,f3=a,f4=b",
			flag:        "exp3",
		},
		{
			name:        "Exists in exp 4",
			expected:    false,
			iserror:     false,
			experiments: "exp1,exp2,exp3=1,exp4",
			flags:       "f1,f2,f3=a,f4=b",
			flag:        "exp4",
		},
		{
			name:        "Exists in flag 1",
			expected:    true,
			iserror:     false,
			experiments: "exp1,exp2,exp3=1,exp4",
			flags:       "f1=1,f2,f3=a,f4=b",
			flag:        "f1",
		},
		{
			name:        "Exists in flag 2",
			expected:    false,
			iserror:     false,
			experiments: "exp1,exp2,exp3=1,exp4",
			flags:       "f1,f2,f3=a,f4=b",
			flag:        "f2",
		},
		{
			name:        "Exists in flag 3",
			expected:    false,
			iserror:     false,
			experiments: "exp1,exp2,exp3=1,exp4",
			flags:       "f1,f2,f3=a,f4=b",
			flag:        "f3",
		},
		{
			name:        "Exists in flag 4",
			expected:    true,
			iserror:     false,
			experiments: "exp1,exp2,exp3=1,exp4",
			flags:       "f1,f2,f3=a,f4=1",
			flag:        "f4",
		},
		{
			name:        "Not found",
			expected:    false,
			iserror:     false,
			experiments: "exp1,exp2,exp3=1,exp4",
			flags:       "f1,f2,f3=a,f4=b",
			flag:        "a",
		},
		{
			name:        "Zero in exp 2",
			expected:    false,
			iserror:     false,
			experiments: "exp1,exp2=0,exp3=1,exp4",
			flags:       "f1,f2,f3=a,f4=b",
			flag:        "exp2",
		},
		{
			name:        "Zero in flag 2",
			expected:    false,
			iserror:     false,
			experiments: "exp1,exp2=0,exp3=1,exp4",
			flags:       "f1,f2=0,f3=a,f4=b",
			flag:        "f2",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			searchAppData := &topnews.TSearchAppData{
				Experiments: tt.experiments,
				Flags:       tt.flags,
			}
			topnewsRequest := topnews.TRequest{
				Common: &topnews.TCommon{
					Url:            "",
					ScaleFactor:    1,
					OrderedRubrics: []string{},
					Locale:         "",
				},
			}
			topnewsRequest.Data = &topnews.TRequest_SearchApp{SearchApp: searchAppData}

			got, err := isExperimentOn(&topnewsRequest, tt.flag)

			require.Equal(t, tt.expected, got)
			if tt.iserror {
				require.Error(t, err)
			}
		})
	}
}
