package ytc

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestBuildLastAuthQuery(t *testing.T) {
	require.Equal(t,
		`
authtype, timestamp
FROM [//some/dir/lastauth/lastauth]
WHERE uid = 100500
ORDER BY timestamp DESC
LIMIT 1
`,
		buildLastAuthQuery(100500, "//some/dir"),
	)
}

func TestBuildLastAuthBulkQuery(t *testing.T) {
	require.Equal(t,
		`
uid, MAX(timestamp) AS timestamp
FROM [//some/dir/lastauth/lastauth]
WHERE uid IN (100500,129)
GROUP BY uid
`,
		buildLastAuthBulkQuery([]uint64{100500, 129}, "//some/dir"),
	)
}
