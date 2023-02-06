package drills

import (
	"bytes"
	"context"
	"encoding/json"
	"io/ioutil"
	"net/http"
	"net/url"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/noc/go/logging"
	"a.yandex-team.ru/noc/topka/pkg/internal/topka/staff"
)

type Resp struct{}

func (m Resp) Do(req *http.Request) (*http.Response, error) {
	membershipQuery := url.Values{
		"person.official.is_dismissed": []string{"false"},
		"_fields":                      []string{"person.login,group.url"},
		"_limit":                       []string{"2000000000"}, // no limit (this number fits in int32)
	}
	ancestorsQuery := url.Values{
		"ancestors.is_deleted": []string{"false"},
		"is_deleted":           []string{"false"},
		"_fields":              []string{"url,ancestors.url"},
		"_limit":               []string{"2000000000"}, // no limit (this number fits in int32)
	}

	type PersonLogin struct {
		Login string `json:"login"`
	}
	type GroupURL struct {
		URL string `json:"url"`
	}
	type Membership struct {
		Person PersonLogin `json:"person"`
		Group  GroupURL    `json:"group"`
	}
	type MembershipResult struct {
		ResultArray []Membership `json:"result"`
	}
	membershipResp := MembershipResult{
		ResultArray: []Membership{
			{
				Person: PersonLogin{
					Login: "a",
				},
				Group: GroupURL{
					URL: "a_gr",
				},
			},
			{
				Person: PersonLogin{
					Login: "b",
				},
				Group: GroupURL{
					URL: "b_gr",
				},
			},
			{
				Person: PersonLogin{
					Login: "c",
				},
				Group: GroupURL{
					URL: "c_gr",
				},
			},
			{
				Person: PersonLogin{
					Login: "a",
				},
				Group: GroupURL{
					URL: "c_gr",
				},
			},
			{
				Person: PersonLogin{
					Login: "b",
				},
				Group: GroupURL{
					URL: "h_gr",
				},
			},
			{
				Person: PersonLogin{
					Login: "ctash",
				},
				Group: GroupURL{
					URL: "yandex_search_tech_assesment_toloka_serv",
				},
			},
		},
	}

	type GroupRecord struct {
		URL       string     `json:"url"`
		Ancestors []GroupURL `json:"ancestors"`
	}
	type AncestorsResult struct {
		ResultArray []GroupRecord `json:"result"`
	}
	ancestorsResp := AncestorsResult{
		ResultArray: []GroupRecord{
			{
				URL: "a_gr",
				Ancestors: []GroupURL{
					{
						URL: "b_gr",
					},
					{
						URL: "c_gr",
					},
				},
			},
			{
				URL: "b_gr",
				Ancestors: []GroupURL{
					{
						URL: "c_gr",
					},
				},
			},
			{
				URL:       "c_gr",
				Ancestors: []GroupURL{},
			},
			{
				URL: "yandex_search_tech_assesment_toloka_serv",
				Ancestors: []GroupURL{
					{
						URL: "yandex_search_tech_assesment_toloka",
					},
					{
						URL: "yandex_search_tech_assesment_toloka_dev",
					},
				},
			},
		},
	}

	var respBytes []byte
	if req.URL.Path == "/v3/groupmembership" && req.URL.RawQuery == membershipQuery.Encode() {
		respBytes, _ = json.Marshal(membershipResp)
	} else if req.URL.Path == "/v3/groups" && req.URL.RawQuery == ancestorsQuery.Encode() {
		respBytes, _ = json.Marshal(ancestorsResp)
	}

	return &http.Response{
		StatusCode: http.StatusOK,
		Body:       ioutil.NopCloser(bytes.NewReader(respBytes)),
	}, nil
}

func TestUpdateStaffInfo(t *testing.T) {
	staffClient, err := staff.NewClient(&staff.Config{
		URL:   "https://mock.yandex-team.ru",
		OAuth: "mock",
	}, staff.WithResponder(Resp{}))
	require.NoError(t, err)

	log, err := logging.NewLogger(&logging.Config{Encoding: "console", Level: 1})
	require.NoError(t, err)

	service := NewService(&Config{}, nil, nil, nil, staffClient, log)
	err = service.UpdateStaffInfo(context.Background())
	require.NoError(t, err)

	require.Equal(t, map[string]map[string]struct{}{
		"a_gr": {
			"a": struct{}{},
		},
		"b_gr": {
			"a": struct{}{},
			"b": struct{}{},
		},
		"c_gr": {
			"a": struct{}{},
			"b": struct{}{},
			"c": struct{}{},
		},
		"h_gr": {
			"b": struct{}{},
		},
		"yandex_search_tech_assesment_toloka_serv": {
			"ctash": struct{}{},
		},
		"yandex_search_tech_assesment_toloka": {
			"ctash": struct{}{},
		},
		"yandex_search_tech_assesment_toloka_dev": {
			"ctash": struct{}{},
		},
	}, service.staffGroupsToPeople)

	require.Equal(t, map[string]map[string]struct{}{
		"a": {
			"a_gr": struct{}{},
			"b_gr": struct{}{},
			"c_gr": struct{}{},
		},
		"b": {
			"b_gr": struct{}{},
			"c_gr": struct{}{},
			"h_gr": struct{}{},
		},
		"c": {
			"c_gr": struct{}{},
		},
		"ctash": {
			"yandex_search_tech_assesment_toloka_serv": struct{}{},
			"yandex_search_tech_assesment_toloka":      struct{}{},
			"yandex_search_tech_assesment_toloka_dev":  struct{}{},
		},
	}, service.staffPeopleToGroups)
}
