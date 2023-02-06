package dbsynctest

import (
	"context"
	"net/url"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"gorm.io/plugin/dbresolver"

	"a.yandex-team.ru/library/go/core/log"
	"a.yandex-team.ru/library/go/core/log/zap"
	"a.yandex-team.ru/library/go/ptr"
	"a.yandex-team.ru/library/go/yandex/tvm"
	"a.yandex-team.ru/noc/cmdb/pkg/cmdbapi"
	"a.yandex-team.ru/noc/cmdb/pkg/cmdbapitest"
	"a.yandex-team.ru/noc/cmdb/pkg/configuration"
	"a.yandex-team.ru/noc/cmdb/pkg/dbconn"
	"a.yandex-team.ru/noc/cmdb/pkg/types"
	"a.yandex-team.ru/strm/common/go/pkg/fn"
	"a.yandex-team.ru/strm/common/go/pkg/xtime"
)

type UserTicket struct {
	UIDs []tvm.UID
}

func (u *UserTicket) UserTicket(ctx context.Context) *tvm.CheckedUserTicket {
	return &tvm.CheckedUserTicket{UIDs: u.UIDs}
}

func TestLogWithoutUser(t *testing.T) {
	dbURI := cmdbapitest.DBURI()
	lg, _ := zap.New(zap.JSONConfig(log.DebugLevel))
	logger := fn.NewLogger(lg)
	db, err := dbconn.Database{
		URIRW:  dbURI,
		Logger: logger,
	}.Open()
	require.NoError(t, err)

	now := &xtime.TimeIncrement{TimeNow: time.Unix(1700000000, 0), Step: xtime.Seconds(1)}
	register := configuration.RegisterLoggerPlugin{
		LoggerPlugin: configuration.LoggerPlugin{
			Now:    now,
			RW:     db.Clauses(dbresolver.Write),
			Logger: logger,
		},
		RW: db.Clauses(dbresolver.Write),
	}
	require.NoError(t, register.RegisterLoggerPlugin())

	server, _, cmdbServer := cmdbapitest.NewRouter(t, db, logger)

	contact := cmdbServer.Contacts.PostContact(t, GetContact())
	cmdbServer.Contacts.GetContacts(t, []*cmdbapi.ContactOut{contact})

	var logs []cmdbapi.LogExt
	uri := url.URL{Path: "/api/logs", RawQuery: url.Values{"after": {"1700000020"}, "before": {"1700000030"}}.Encode()}
	server.Get(t, server.URL+uri.String(), &logs)
	assert.Equal(t, 0, len(logs), logs)
}

func GetContact() cmdbapi.ContactIn {
	return cmdbapi.ContactIn{
		ID:             (*types.ContactID)(ptr.Int64(15)),
		Name:           "Первая линия поддержки Ростелеком",
		Details:        "+7(999)111-22-33",
		EmailForRobots: "for_robots@rostelekom.ru",
	}
}

func GetContactModified() cmdbapi.ContactIn {
	return cmdbapi.ContactIn{
		ID:             (*types.ContactID)(ptr.Int64(15)),
		Name:           "Первая линия поддержки Ростелеком",
		Details:        "+7(999)111-22-33",
		EmailForRobots: "for_robots@rostelekom.ru",
	}
}
