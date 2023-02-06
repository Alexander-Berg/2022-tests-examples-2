package crud

import (
	"context"
	"testing"

	"github.com/elimity-com/scim"
	"github.com/golang/mock/gomock"
	"github.com/scim2/filter-parser/v2"
	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/library/go/yandex/blackbox"
	"a.yandex-team.ru/passport/backend/library/passportapi"
	"a.yandex-team.ru/passport/backend/scim_api/internal/core/models"
	"a.yandex-team.ru/passport/backend/scim_api/internal/logutils"
	passportBlackbox "a.yandex-team.ru/passport/shared/golibs/blackbox"
)

func TestPatchUser(t *testing.T) {
	ctrl := gomock.NewController(t)
	adapter, bb, passp := getAdapter(ctrl)

	ctx := context.Background()
	ctx = logutils.AddRequestToContext(ctx, &logutils.CtxRequest{
		ClientIP: "127.0.0.1",
		DomainID: 1,
	})

	bb.EXPECT().HostedDomains(gomock.Any(), uint64(1)).Return(
		&passportBlackbox.HostedDomainsResponse{
			Domains: []passportBlackbox.HostedDomain{
				{
					Domain:   "foobar.ru",
					DomainID: 1,
				},
			},
		},
		nil,
	)

	bb.EXPECT().UserInfo(gomock.Any(), gomock.Any()).Return(
		&blackbox.UserInfoResponse{
			Users: []blackbox.User{
				{
					UID:         blackbox.UID{ID: 123},
					DisplayName: blackbox.DisplayName{Name: "Firstname Lastname"},
					Attributes: map[blackbox.UserAttribute]string{
						blackbox.UserAttributePersonFirstname: "firstname",
						blackbox.UserAttributePersonLastname:  "lastname",
					},
					Aliases: map[blackbox.UserAlias]string{
						blackbox.UserAliasPdd: "1/pdd-alias",
						"24":                  "1/saml-alias",
					},
					AddressList: []blackbox.Address{
						{
							Address: "foo@bar.ru",
						},
					},
				},
			},
		},
		nil,
	)

	passp.EXPECT().EditFederal(gomock.Any(), gomock.Any(), passportapi.EditFederalRequest{
		UID:         123,
		DisplayName: "new display name",
		FirstName:   "new firstname",
		LastName:    "new lastname",
		Active:      false,
		EMails:      []string{"foo@bar.ru"},
	}).Return(
		passportapi.BaseResponse{
			Status: "ok",
		},
		nil,
	)

	givenName := "givenName"
	familyName := "familyName"

	user, err := adapter.PatchUser(ctx, "123", []scim.PatchOperation{
		{
			Op: scim.PatchOperationReplace,
			Path: &filter.Path{
				AttributePath: filter.AttributePath{AttributeName: "isActive"},
			},
			Value: false,
		},
		{
			Op: scim.PatchOperationReplace,
			Path: &filter.Path{
				AttributePath: filter.AttributePath{AttributeName: "displayName"},
			},
			Value: "new display name",
		},
		{
			Op: scim.PatchOperationReplace,
			Path: &filter.Path{
				AttributePath: filter.AttributePath{
					AttributeName: "name",
					SubAttribute:  &givenName,
				},
			},
			Value: "new firstname",
		},
		{
			Op: scim.PatchOperationReplace,
			Path: &filter.Path{
				AttributePath: filter.AttributePath{
					AttributeName: "name",
					SubAttribute:  &familyName,
				},
			},
			Value: "new lastname",
		},
	})

	expectedUser := models.User{
		PassportUID: 123,
		FirstName:   "new firstname",
		LastName:    "new lastname",
		IsActive:    false,
		DisplayName: "new display name",
		Emails: []models.Email{
			{Address: "foo@bar.ru"},
		},
		UserName: "saml-alias@foobar.ru",
		DomainID: 1,
	}

	assert.NoError(t, err)
	assert.Equal(t, expectedUser, user)
}
