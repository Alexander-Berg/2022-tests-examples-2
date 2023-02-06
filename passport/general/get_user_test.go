package crud

import (
	"context"
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/library/go/yandex/blackbox"
	passportapi_client "a.yandex-team.ru/passport/backend/library/passportapi/mocks/passportapi_mock"
	"a.yandex-team.ru/passport/backend/scim_api/internal/core/models"
	"a.yandex-team.ru/passport/backend/scim_api/internal/logutils"
	passportBlackbox "a.yandex-team.ru/passport/shared/golibs/blackbox"
	"a.yandex-team.ru/passport/shared/golibs/blackbox/mock_blackbox"
	"a.yandex-team.ru/passport/shared/golibs/logger"
)

func getAdapter(ctrl *gomock.Controller) (adapter, *mock_blackbox.MockClient, *passportapi_client.MockAPIClient) {
	bb := mock_blackbox.NewMockClient(ctrl)
	passp := passportapi_client.NewMockAPIClient(ctrl)

	a := adapter{
		bb:       bb,
		passport: passp,
		logger:   logger.Log(),
	}
	return a, bb, passp
}

func TestGetUser(t *testing.T) {
	ctrl := gomock.NewController(t)
	adapter, bb, _ := getAdapter(ctrl)

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
						blackbox.UserAttributePersonFirstname:    "firstname",
						blackbox.UserAttributePersonLastname:     "lastname",
						blackbox.UserAttributeAccountIsAvailable: "1",
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

	expectedUser := models.User{
		PassportUID: 123,
		UserName:    "saml-alias@foobar.ru",
		FirstName:   "firstname",
		LastName:    "lastname",
		IsActive:    true,
		DisplayName: "Firstname Lastname",
		DomainID:    1,
		Emails:      []models.Email{{Address: "foo@bar.ru"}},
	}

	user, err := adapter.GetUser(ctx, "123")
	assert.NoError(t, err)
	assert.Equal(t, expectedUser, user)
}

func TestGetUserNotFound(t *testing.T) {
	ctrl := gomock.NewController(t)
	adapter, bb, _ := getAdapter(ctrl)

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
		&blackbox.UserInfoResponse{},
		nil,
	)

	_, err := adapter.GetUser(ctx, "123")
	assert.Error(t, err)
}

func TestGetUserNotFederal(t *testing.T) {
	ctrl := gomock.NewController(t)
	adapter, bb, _ := getAdapter(ctrl)

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

	_, err := adapter.GetUser(ctx, "123")
	assert.Error(t, err)
}
