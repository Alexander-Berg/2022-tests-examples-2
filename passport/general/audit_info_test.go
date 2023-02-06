package mysql

import (
	"context"
	"testing"
	"time"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/passport/infra/daemons/yasms_internal/internal/model"
)

var AuditBulk = model.AuditBulkInfo{
	AuditBulkInfoBase: model.AuditBulkInfoBase{
		ID:      "1",
		Comment: "comment",
		Issue:   "PASSP-1",
		Author:  "login",
	},
	Changes: map[string]model.AuditRowChange{
		"1": {AuditRowChangeBase: model.AuditRowChangeBase{EntityID: "56", Action: "add"}, Payload: "phone=+234,blocktype=permanent,blocktill=1234-05-06 07:08:09 +0000 UTC"},
	},
}

var AuditChange = model.AuditChangeInfo{
	AuditRowChangeBase: model.AuditRowChangeBase{EntityID: "56", Action: "add"},
	AuditBulkInfo: model.AuditBulkInfoBase{
		ID:        "1",
		Comment:   "comment",
		Issue:     "PASSP-1",
		Author:    "login",
		Timestamp: 1233456,
	},
}

func TestMySQLProvider_GetAuditBulkInfo(t *testing.T) {
	provider, _ := initProvider()

	// insert something to get audit log
	newPhone := &model.BlockedPhone{
		PhoneNumber: "+234",
		BlockType:   model.BlockTypePermanent,
		BlockUntil:  time.Date(1234, 5, 6, 7, 8, 9, 0, time.UTC),
	}
	err := provider.SetBlockedPhones(context.Background(), nil, []*model.BlockedPhone{newPhone}, nil, &model.AuditLogBulkParams{
		Author:  "login",
		Issue:   []string{"PASSP-1"},
		Comment: "comment",
	})
	require.NoError(t, err)

	auditbulk, err := provider.GetAuditBulkInfo(context.Background(), "1")
	require.NoError(t, err)
	require.Equal(t, auditbulk.ID, AuditBulk.ID)
	require.Equal(t, auditbulk.Author, AuditBulk.Author)
	require.Equal(t, auditbulk.Comment, AuditBulk.Comment)
	require.Equal(t, auditbulk.Issue, AuditBulk.Issue)
	require.Equal(t, auditbulk.Changes, AuditBulk.Changes)
	require.Greater(t, auditbulk.Timestamp, int64(0))
}

func TestMySQLProvider_GetAuditChangeInfo(t *testing.T) {
	provider, _ := initProvider()

	// insert something to get audit log
	newPhone := &model.BlockedPhone{
		PhoneNumber: "+234",
		BlockType:   model.BlockTypePermanent,
		BlockUntil:  time.Date(1234, 5, 6, 7, 8, 9, 0, time.UTC),
	}
	err := provider.SetBlockedPhones(context.Background(), nil, []*model.BlockedPhone{newPhone}, nil, &model.AuditLogBulkParams{
		Author:  "login",
		Issue:   []string{"PASSP-1"},
		Comment: "comment",
	})
	require.NoError(t, err)

	auditchange, err := provider.GetAuditChangeInfo(context.Background(), []model.EntityID{"1"})
	require.NoError(t, err)
	require.Equal(t, (*auditchange)["1"].AuditBulkInfo.ID, AuditChange.AuditBulkInfo.ID)
	require.Equal(t, (*auditchange)["1"].AuditBulkInfo.Author, AuditChange.AuditBulkInfo.Author)
	require.Equal(t, (*auditchange)["1"].AuditBulkInfo.Comment, AuditChange.AuditBulkInfo.Comment)
	require.Equal(t, (*auditchange)["1"].AuditBulkInfo.Issue, AuditChange.AuditBulkInfo.Issue)
	require.Greater(t, (*auditchange)["1"].AuditBulkInfo.Timestamp, int64(0))

	require.Equal(t, (*auditchange)["1"].EntityID, AuditChange.EntityID)
	require.Equal(t, (*auditchange)["1"].Action, AuditChange.Action)
}
