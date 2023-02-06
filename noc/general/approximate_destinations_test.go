package cauth_test

import (
	"fmt"
	"net"
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/noc/puncher/client/macrosd"
	"a.yandex-team.ru/noc/puncher/cmd/puncher-rules-cauth/importers/cauth"
	"a.yandex-team.ru/noc/puncher/mock/macrosdmock"
	"a.yandex-team.ru/noc/puncher/models"
)

func TestApproximateDestinations(t *testing.T) {
	macrosdServer := macrosdmock.NewServer()
	defer macrosdServer.Close()

	macrosdClient := macrosd.NewClient(macrosdServer.URL)

	h := make([]models.Addr, 21)
	for i := range h {
		h[i] = models.Addr{FQDN: fmt.Sprintf("h%d.yandex.net", i), IPs: []net.IP{net.ParseIP(fmt.Sprintf("10.0.0.%d", i))}}
	}

	s := make([]models.Addr, 4)
	for i := range s {
		s[i] = models.Addr{FQDN: fmt.Sprintf("slb%d.yandex.net", i), IPs: []net.IP{net.ParseIP(fmt.Sprintf("10.1.0.%d", i))}}
	}

	threshold := 3
	tests := []struct {
		Name         string
		Destinations []*cauth.Destination
		Macros       []string
		FQDNs        []string
	}{
		{
			Name: "simple case",
			Destinations: []*cauth.Destination{
				{
					Type:     "conductor",
					Name:     "test",
					Children: []models.Addr{h[0], h[1], h[2]},
				},
			},
			Macros: []string{},
			FQDNs:  []string{"h0.yandex.net", "h1.yandex.net", "h2.yandex.net"},
		},
		{
			Name: "approximate to macros",
			Destinations: []*cauth.Destination{
				{
					Type:     "conductor",
					Name:     "test",
					Children: []models.Addr{h[0], h[1], h[2], h[3]},
				},
			},
			Macros: []string{"_PROJECTNETS_"},
			FQDNs:  []string{},
		},
		{
			Name: "partial approximate",
			Destinations: []*cauth.Destination{
				{
					Type:     "conductor",
					Name:     "test",
					Children: []models.Addr{h[0], h[1], h[2], h[3], h[4]},
				},
			},
			Macros: []string{"_PROJECTNETS_"},
			FQDNs:  []string{"h4.yandex.net"},
		},
		{
			Name: "do not export fqdns without valid parents",
			Destinations: []*cauth.Destination{
				{
					Type:     "conductor",
					Name:     "test",
					Children: []models.Addr{h[0], h[1], h[2], h[3], h[5], h[20]},
				},
			},
			Macros: []string{"_PROJECTNETS_"},
			FQDNs:  []string{},
		},
		{
			Name: "several destinations",
			Destinations: []*cauth.Destination{
				{
					Type:     "conductor",
					Name:     "test",
					Children: []models.Addr{h[0], h[1], h[2]},
				},
				{
					Type:     "conductor",
					Name:     "test",
					Children: []models.Addr{h[3]},
				},
			},
			Macros: []string{"_PROJECTNETS_"},
			FQDNs:  []string{},
		},
		{
			Name: "fqnd for already approximated macro",
			Destinations: []*cauth.Destination{
				{
					Type:     "conductor",
					Name:     "test",
					Children: []models.Addr{h[0], h[1], h[2], h[3], h[6]},
				},
				{
					Type:     "conductor",
					Name:     "test",
					Children: []models.Addr{h[7]},
				},
			},
			Macros: []string{"_PROJECTNETS_"},
			FQDNs:  []string{},
		},
		{
			Name: "do not approximate VS",
			Destinations: []*cauth.Destination{
				{
					Type:     "conductor",
					Name:     "test",
					Children: []models.Addr{s[0], s[1], s[2], s[3], h[6]},
				},
			},
			Macros: []string{},
			FQDNs:  []string{"h6.yandex.net", "slb0.yandex.net", "slb1.yandex.net", "slb2.yandex.net", "slb3.yandex.net"},
		},
		{
			Name: "do not export a macro if already approximated for some parent macro",
			Destinations: []*cauth.Destination{
				{
					Type:     "conductor",
					Name:     "test",
					Children: []models.Addr{h[0], h[1], h[2], h[3], h[6], h[8], h[9], h[10], h[11]},
				},
				{
					Type:     "conductor",
					Name:     "test",
					Children: []models.Addr{h[12], h[13], h[14], h[15]},
				},
			},
			Macros: []string{"_HBFPROJECTSNETS_TEST_", "_PROJECTNETS2_"},
			FQDNs:  []string{"h6.yandex.net"},
		},
		{
			Name: "absorb a child macro only if parrent will be exported",
			Destinations: []*cauth.Destination{
				{
					Type:     "conductor",
					Name:     "test",
					Children: []models.Addr{h[0], h[1], h[2], h[3], h[8], h[9], h[10]},
				},
			},
			Macros: []string{"_PROJECTNETS_"},
			FQDNs:  []string{"h10.yandex.net", "h8.yandex.net", "h9.yandex.net"},
		},
		{
			Name: "if there is no parents for approximate – export as fqdn",
			Destinations: []*cauth.Destination{
				{
					Type:     "conductor",
					Name:     "test",
					Children: []models.Addr{h[16], h[17], h[18], h[19], h[8], h[9], h[10], h[11]},
				},
			},
			Macros: []string{"_HBFPROJECTSNETS_TEST_"},
			FQDNs:  []string{"h16.yandex.net", "h17.yandex.net", "h18.yandex.net", "h19.yandex.net"},
		},
	}
	projectsIDsCache := make(map[string]string)
	rejectedCache := make(map[string]struct{})

	slbSections := make(map[string]models.Section)
	slbSections["slb0.yandex.net"] = models.Section{Name: "slb1.yandex.net"}
	slbSections["slb1.yandex.net"] = models.Section{Name: "slb2.yandex.net"}
	slbSections["slb2.yandex.net"] = models.Section{Name: "slb3.yandex.net"}
	slbSections["slb3.yandex.net"] = models.Section{Name: "slb4.yandex.net"}

	for _, test := range tests {
		allParentsCache := make(map[string][]models.MacroSize)
		macrosAndFQDNs, err := cauth.ApproximateDestinations(
			test.Destinations,
			slbSections,
			threshold,
			projectsIDsCache,
			macrosdClient,
			rejectedCache,
			allParentsCache,
		)
		assert.NoError(t, err)
		assert.Equal(t, macrosAndFQDNs.Macros, test.Macros)
		assert.Equal(t, macrosAndFQDNs.FQDNs, test.FQDNs)
	}
}
