package inmemory

import (
	"testing"

	"github.com/elimity-com/scim"
	"github.com/scim2/filter-parser/v2"
	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/passport/backend/scim_api/internal/core/models"
)

func TestPatchReplace(t *testing.T) {
	user := models.User{
		UserName:    "user name",
		IsActive:    true,
		DisplayName: "display name",
		FirstName:   "first name",
		LastName:    "last name",
	}

	patch1 := scim.PatchOperation{
		Op: scim.PatchOperationReplace,
		Path: &filter.Path{
			AttributePath: filter.AttributePath{AttributeName: "userName"},
		},
		Value: "new user name",
	}
	applySinglePatch(&user, patch1)

	patch2 := scim.PatchOperation{
		Op: scim.PatchOperationReplace,
		Path: &filter.Path{
			AttributePath: filter.AttributePath{AttributeName: "active"},
		},
		Value: false,
	}
	applySinglePatch(&user, patch2)

	assert.Equal(t, user.IsActive, false)
}
