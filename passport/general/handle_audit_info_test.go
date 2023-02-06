package processor

import (
	"context"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/passport/infra/daemons/yasms_internal/internal/model"
)

func TestProcessor_HandleAuditBulkInfo(t *testing.T) {
	provider := NewFakeProvider()
	processor, err := NewTestProcessor(provider)
	require.NoError(t, err)

	response, err := processor.HandleAuditBulkInfo(context.Background(), GetAuditBulkInfoRequest{
		BulkID: "1",
	})

	require.NoError(t, err)
	require.Equal(t, &GetAuditBulkInfoResponse{
		AuditBulkInfo: provider.AuditBulkInfo,
	}, response)
}

func TestProcessor_HandleAuditChangeInfo(t *testing.T) {
	provider := NewFakeProvider()
	processor, err := NewTestProcessor(provider)
	require.NoError(t, err)

	response, err := processor.HandleAuditChangeInfo(context.Background(), GetAuditChangeInfoRequest{ChangeIDs: []model.EntityID{"1", "2}"}})

	require.NoError(t, err)
	require.Equal(t, &GetAuditChangeInfoResponse{
		AuditChangesInfo: provider.AuditChangesInfo,
	}, response)
}
