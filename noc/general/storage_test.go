package roles

import (
	"context"
	"fmt"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"inet.af/netaddr"

	"a.yandex-team.ru/library/go/core/log/nop"
	"a.yandex-team.ru/noc/nocauth/pkg/types"
)

func NewMockStorage() *Storage {
	return NewStorage(
		&types.RoleProviderMock{
			Roles: []types.Role{
				{Username: "vladstar", DestinationSlug: "iva1-i65", Sudo: true},
				{Username: "vladstar", DestinationSlug: "devicegroup.cisco-devices", Sudo: false},
				{Username: "god", DestinationSlug: "devicegroup.all-devices", Sudo: true},
				{Username: "semigod", DestinationSlug: "devicegroup.all-devices", Sudo: false},
			},
		},
		&types.RTAPIClientMock{
			TacacsDevices: nil,
			NocauthGroups: []types.Group{
				{Name: "All devices", Devices: []types.Device{{Name: "iva1-i64"}}},
				{Name: "CISCO devices", Devices: []types.Device{{Name: "iva1-i64"}}},
			},
			NocauthDeviceIPs: []types.DeviceIPs{
				types.NewDeviceIPs("iva1-i64", []string{"2a02:6b8:b010:81::106", "127.0.0.1"}),
				types.NewDeviceIPs("iva1-i65", []string{"2a02:6b8:b010:82::1006:1001"}),
			},
		},
		&nop.Logger{},
	)
}

func TestStorage_UpdateRoles(t *testing.T) {
	storage := NewMockStorage()

	assert.Equal(t, map[UserDevice]bool{}, storage.grants)

	require.NoError(t, storage.UpdateRoles(context.TODO()))

	assert.Equal(t, map[UserDevice]bool{
		UserDevice{Username: "vladstar", Device: "iva1-i65"}: true,
		UserDevice{Username: "vladstar", Device: "iva1-i64"}: false,
		UserDevice{Username: "god", Device: "iva1-i64"}:      true,
		UserDevice{Username: "semigod", Device: "iva1-i64"}:  false,
	}, storage.grants)
}

func TestStorage_UpdateIPs(t *testing.T) {
	storage := NewMockStorage()

	assert.Equal(t, map[UserDevice]bool{}, storage.grants)

	require.NoError(t, storage.UpdateIPs(context.TODO()))

	assert.Equal(t, map[netaddr.IP]types.DeviceIPs{
		netaddr.MustParseIP("2a02:6b8:b010:81::106"):       types.NewDeviceIPs("iva1-i64", []string{"2a02:6b8:b010:81::106", "127.0.0.1"}),
		netaddr.MustParseIP("127.0.0.1"):                   types.NewDeviceIPs("iva1-i64", []string{"2a02:6b8:b010:81::106", "127.0.0.1"}),
		netaddr.MustParseIP("2a02:6b8:b010:82::1006:1001"): types.NewDeviceIPs("iva1-i65", []string{"2a02:6b8:b010:82::1006:1001"}),
	}, storage.deviceIPs)
}

func TestStorage_CheckRole(t *testing.T) {
	storage := NewMockStorage()
	require.NoError(t, storage.UpdateRoles(context.TODO()))

	testCases := []struct {
		Username      string
		Device        string
		AllowRTSuffix bool
		Expected      types.AccessType
	}{
		{Username: "vladstar", Device: "iva1-i65", AllowRTSuffix: false, Expected: types.SudoAccess},
		{Username: "vladstar", Device: "iva1-i64", AllowRTSuffix: false, Expected: types.Access},
		{Username: "invalid", Device: "iva1-i65", AllowRTSuffix: false, Expected: types.NoAccess},
		{Username: "god", Device: "iva1-i64", AllowRTSuffix: false, Expected: types.SudoAccess},
		{Username: "semigod", Device: "iva1-i64", AllowRTSuffix: false, Expected: types.Access},
		{Username: "racktables", Device: "iva1-i64", AllowRTSuffix: false, Expected: types.SudoAccess},
		{Username: "vladstar-nocauth-RT", Device: "iva1-i64", AllowRTSuffix: true, Expected: types.SudoAccess},
		{Username: "monitor", Device: "iva1-i64", AllowRTSuffix: false, Expected: types.Access},
	}

	for _, testCase := range testCases {
		t.Run(fmt.Sprintf("%s_%s", testCase.Username, testCase.Device), func(t *testing.T) {
			assert.Equal(
				t,
				testCase.Expected,
				storage.CheckRole(testCase.Username, testCase.Device, testCase.AllowRTSuffix))
		})
	}
}

func TestStorage_GetDeviceByIP(t *testing.T) {
	storage := NewMockStorage()
	require.NoError(t, storage.UpdateIPs(context.TODO()))

	testCases := []struct {
		IP       string
		Expected string
		Found    bool
	}{
		{IP: "127.0.0.1", Expected: "iva1-i64", Found: true},
		{IP: "127.0.0.7", Expected: "", Found: false},
		{IP: "::ffff:127.0.0.1", Expected: "iva1-i64", Found: true},
		{IP: "::ffff:127.0.0.7", Expected: "", Found: false},
		{IP: "2a02:6b8:b010:82::1006:1001", Expected: "iva1-i65", Found: true},
		{IP: "invalid", Expected: "", Found: false},
	}

	for _, testCase := range testCases {
		t.Run(testCase.IP, func(t *testing.T) {
			device, ok := storage.GetDeviceByIP(testCase.IP)
			require.Equal(t, testCase.Found, ok)
			assert.Equal(t, testCase.Expected, device.Name)
		})
	}
}
