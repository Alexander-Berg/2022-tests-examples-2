package types_test

import (
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/noc/cmdb/pkg/types"
)

func TestNetCIDR_Le(t *testing.T) {
	assert.True(t, types.NetCIDR("217.169.82.160/27").Le(types.NetCIDR("2001:504:0:2::/64")))
	assert.True(t, types.NetCIDR("2001:503:0:2::/64").Le(types.NetCIDR("2001:504:0:2::/64")))
	assert.True(t, types.NetCIDR("217.169.82.160/27").Le(types.NetCIDR("217.169.83.160/27")))
	assert.True(t, types.NetCIDR("217.169.82.160/27").Le(types.NetCIDR("217.169.82.160/28")))
}
