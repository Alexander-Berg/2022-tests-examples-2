package glue

import (
	"testing"

	"github.com/elimity-com/scim"
	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/library/go/yandex/blackbox"
	"a.yandex-team.ru/passport/backend/scim_api/internal/core/models"
)

func TestParseBlackboxUser(t *testing.T) {
	bbUser := blackbox.User{
		UID: blackbox.UID{ID: 123},
		Aliases: map[blackbox.UserAlias]string{
			blackbox.UserAlias("24"): "12345/FEDERAL-alias",
		},
		Attributes: map[blackbox.UserAttribute]string{
			blackbox.UserAttributePersonFirstname:    "firstname",
			blackbox.UserAttributePersonLastname:     "lastname",
			blackbox.UserAttributeAccountIsAvailable: "1",
		},
		AddressList: []blackbox.Address{
			{
				Address: "username@domain.com",
				Default: true,
			},
			{
				Address: "username@domain.ru",
			},
		},
	}
	var actualUser models.User
	expectedUser := models.User{
		PassportUID: 123,
		DomainID:    12345,
		FirstName:   "firstname",
		LastName:    "lastname",
		Emails: []models.Email{
			{Address: "username@domain.com"},
			{Address: "username@domain.ru"},
		},
		UserName: "FEDERAL-alias",
		IsActive: true,
	}
	if assert.NoError(t, BlackboxUserToUser(bbUser, &actualUser)) {
		assert.Equal(t, expectedUser, actualUser)
	}
}

var Parse24AliasTestTable = []struct {
	title    string
	badInput string
}{
	{
		"empty",
		"",
	},
	{
		"/no_domain_id",
		"/no_domain_id",
	},
	{
		"no_slash",
		"no_slash",
	},
	{
		"bad_domain_id",
		"foo/bar",
	},
	{
		"bad_name_id",
		"12345/",
	},
}

func TestParse24Alias(t *testing.T) {
	for _, tt := range Parse24AliasTestTable {
		t.Run(
			tt.title,
			func(t *testing.T) {
				_, _, err := parse24Alias(tt.badInput)
				assert.NotEqual(t, nil, err)
			})
	}
}

var DisplayNameTestTable = []struct {
	title       string
	displayName string
	formatted   string
	expected    string
}{
	{
		"display name without formatted",
		"foo bar",
		"",
		"foo bar",
	},
	{
		"display name and formatted",
		"foo bar",
		"bar foo",
		"foo bar",
	},
	{
		"no display name but formatted",
		"",
		"bar foo",
		"bar foo",
	},
}

func TestDisplayName(t *testing.T) {
	for _, tt := range DisplayNameTestTable {
		t.Run(tt.title, func(t *testing.T) {
			attrs := scim.ResourceAttributes{
				"name": map[string]interface{}{},
			}
			if tt.displayName != "" {
				attrs["displayName"] = tt.displayName
			}
			if tt.formatted != "" {
				attrs["name"] = map[string]interface{}{
					"formatted": tt.formatted,
				}
			}
			var user models.User
			assert.NoError(t, AttributesToUser(attrs, &user))
			assert.Equal(t, tt.expected, user.DisplayName)
		})
	}
}
