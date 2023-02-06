package policy_test

import (
	"reflect"
	"testing"

	"a.yandex-team.ru/noc/puncher/client/usersd"
	"a.yandex-team.ru/noc/puncher/cmd/puncher-daemon/errors"
	"a.yandex-team.ru/noc/puncher/cmd/puncher-daemon/policy"
	"a.yandex-team.ru/noc/puncher/mock/usersdmock"
	"a.yandex-team.ru/noc/puncher/models"
	"a.yandex-team.ru/noc/puncher/models/modelstest"
)

func TestCanDeleteRequest(t *testing.T) {
	usersdServer := usersdmock.NewServer()
	defer usersdServer.Close()

	usersdClient := usersd.NewClient(usersdServer.URL)

	tests := []struct {
		Name      string
		User      models.Target
		SuperUser bool
		Rule      *models.Rule
		Request   models.Request
		Status    models.RequestStatus
		Err       errors.HTTPError
	}{
		{
			"author can delete own request",
			modelstest.Eve, false,
			nil, models.Request{
				Author:       modelstest.Eve,
				Sources:      []models.Target{modelstest.CBobHosts},
				Destinations: []models.Target{modelstest.CAliceHosts},
			},
			models.RequestStatusClosedByAuthor, nil,
		},
		{
			"admins can delete requests",
			modelstest.Alice, false,
			nil, models.Request{
				Author:       modelstest.Eve,
				Sources:      []models.Target{modelstest.CBobHosts},
				Destinations: []models.Target{modelstest.CAliceHosts},
			},
			models.RequestStatusClosedByAdmin, nil,
		},
		{
			"delete request without owners",
			modelstest.Alice, false,
			nil, models.Request{
				Author:       modelstest.Eve,
				Sources:      []models.Target{modelstest.CBobHosts},
				Destinations: []models.Target{modelstest.CLostHosts},
			},
			"", errors.NewHTTPError(400, "No responsible users found for this request"),
		},
		{
			"delete foreign request",
			modelstest.Alice, false,
			nil, models.Request{
				Author:       modelstest.Eve,
				Sources:      []models.Target{modelstest.CBobHosts},
				Destinations: []models.Target{modelstest.CBobHosts},
			},
			"", errors.NewHTTPError(400, "You are not responsible for this request"),
		},
		{
			"security can delete requests",
			modelstest.Supreme, true,
			nil, models.Request{
				Author:       modelstest.Eve,
				Sources:      []models.Target{modelstest.CBobHosts},
				Destinations: []models.Target{modelstest.CAliceHosts},
			},
			"closed_by_security", nil,
		},
	}

	for _, test := range tests {
		status, err := policy.CanDeleteRequest(usersdClient, test.User, test.SuperUser, test.Rule, test.Request)
		if status != test.Status {
			t.Errorf("%s - status: got %q, want %q", test.Name, status, test.Status)
		}
		if !reflect.DeepEqual(err, test.Err) {
			t.Errorf("%s - error: got %v, want %v", test.Name, err, test.Err)
		}
	}
}
