package api

import (
	"context"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/passport/infra/daemons/historydb_api2/internal/errs"
	"a.yandex-team.ru/passport/infra/daemons/historydb_api2/internal/reqs"
	"a.yandex-team.ru/passport/infra/daemons/historydb_api2/internal/resps"
)

func TestMergeAuthsFailed(t *testing.T) {
	cases := []struct {
		yt       []*resps.PlainAuth
		hbase    []*resps.PlainAuth
		expected []*resps.PlainAuth
		limit    int
		order    reqs.OrderByType
	}{
		{
			yt: []*resps.PlainAuth{
				{Timestamp: 10},
				{Timestamp: 9},
			},
			hbase: []*resps.PlainAuth{
				{Timestamp: 8},
				{Timestamp: 7},
			},
			expected: []*resps.PlainAuth{
				{Timestamp: 10},
				{Timestamp: 9},
				{Timestamp: 8},
				{Timestamp: 7},
			},
			limit: 100500,
			order: reqs.OrderByDesc,
		},
		{
			yt: []*resps.PlainAuth{
				{Timestamp: 9},
				{Timestamp: 10},
			},
			hbase: []*resps.PlainAuth{
				{Timestamp: 7},
				{Timestamp: 8},
			},
			expected: []*resps.PlainAuth{
				{Timestamp: 7},
				{Timestamp: 8},
				{Timestamp: 9},
				{Timestamp: 10},
			},
			limit: 100500,
			order: reqs.OrderByAsc,
		},
		{
			yt: []*resps.PlainAuth{
				{Timestamp: 10},
				{Timestamp: 9},
			},
			hbase: []*resps.PlainAuth{
				{Timestamp: 8},
				{Timestamp: 7},
			},
			expected: []*resps.PlainAuth{
				{Timestamp: 10},
				{Timestamp: 9},
				{Timestamp: 8},
			},
			limit: 3,
			order: reqs.OrderByDesc,
		},
		{
			yt: []*resps.PlainAuth{
				{Timestamp: 9},
				{Timestamp: 10},
			},
			hbase: []*resps.PlainAuth{
				{Timestamp: 7},
				{Timestamp: 8},
			},
			expected: []*resps.PlainAuth{
				{Timestamp: 8},
				{Timestamp: 9},
				{Timestamp: 10},
			},
			limit: 3,
			order: reqs.OrderByAsc,
		},
		{
			yt: []*resps.PlainAuth{
				{Timestamp: 10},
				{Timestamp: 9},
			},
			hbase: []*resps.PlainAuth{
				{Timestamp: 8},
				{Timestamp: 7},
			},
			expected: []*resps.PlainAuth{
				{Timestamp: 10},
				{Timestamp: 9},
			},
			limit: 2,
			order: reqs.OrderByDesc,
		},
		{
			yt: []*resps.PlainAuth{
				{Timestamp: 9},
				{Timestamp: 10},
			},
			hbase: []*resps.PlainAuth{
				{Timestamp: 7},
				{Timestamp: 8},
			},
			expected: []*resps.PlainAuth{
				{Timestamp: 9},
				{Timestamp: 10},
			},
			limit: 2,
			order: reqs.OrderByAsc,
		},
	}

	for idx, c := range cases {
		res := mergeOrderedSlices(c.yt, c.hbase, c.limit, c.order)
		require.EqualValues(t, res, c.expected, idx)
	}
}

func TestMergeMailUserHistoryErrs(t *testing.T) {
	cases := []struct {
		yt    resps.MailUserHistoryResult
		hbase resps.MailUserHistoryResult
		err   string
	}{
		{
			yt: resps.MailUserHistoryResult{
				Status: errs.ScalaStatusOk,
			},
			hbase: resps.MailUserHistoryResult{
				Status: errs.ScalaStatusError,
			},
			err: "statuses are not equal; yt=ok, hbase=error",
		},
		{
			yt: resps.MailUserHistoryResult{
				Status: errs.ScalaStatusOk,
				UID:    42,
			},
			hbase: resps.MailUserHistoryResult{
				Status: errs.ScalaStatusOk,
				UID:    43,
			},
			err: "uids are not equal; yt=42, hbase=43",
		},
	}

	for idx, c := range cases {
		res, err := mergeMailUserHistoryResults(context.Background(), &c.yt, &c.hbase)
		require.Nil(t, res)
		require.EqualError(t, err, c.err, idx)
	}
}

func TestMergeMailUserHistoryResult(t *testing.T) {
	cases := []struct {
		yt       resps.MailUserHistoryResult
		hbase    resps.MailUserHistoryResult
		expected resps.MailUserHistoryResult
	}{
		{ // check only status and uid
			yt: resps.MailUserHistoryResult{
				Status: errs.ScalaStatusOk,
				UID:    42,
			},
			hbase: resps.MailUserHistoryResult{
				Status: errs.ScalaStatusOk,
				UID:    42,
			},
			expected: resps.MailUserHistoryResult{
				Status: errs.ScalaStatusOk,
				UID:    42,
			},
		},
		{ // check optimization for yt-only result
			yt: resps.MailUserHistoryResult{
				Items: []*resps.MailUserHistoryItem{
					{Common: resps.MailUserHistoryItemCommon{
						Date:      uint64(100),
						Operation: "op#11",
						Module:    "mod#11",
					}},
				},
			},
			hbase: resps.MailUserHistoryResult{},
			expected: resps.MailUserHistoryResult{
				Items: []*resps.MailUserHistoryItem{
					{Common: resps.MailUserHistoryItemCommon{
						Date:      uint64(100),
						Operation: "op#11",
						Module:    "mod#11",
					}},
				},
			},
		},
		{ // check optimization for hbase-only result
			yt: resps.MailUserHistoryResult{},
			hbase: resps.MailUserHistoryResult{
				Items: []*resps.MailUserHistoryItem{
					{Common: resps.MailUserHistoryItemCommon{
						Date:      uint64(100),
						Operation: "op#11",
						Module:    "mod#11",
					}},
				},
			},
			expected: resps.MailUserHistoryResult{
				Items: []*resps.MailUserHistoryItem{
					{Common: resps.MailUserHistoryItemCommon{
						Date:      uint64(100),
						Operation: "op#11",
						Module:    "mod#11",
					}},
				},
			},
		},
		{ // common merge
			yt: resps.MailUserHistoryResult{
				Items: []*resps.MailUserHistoryItem{
					{Common: resps.MailUserHistoryItemCommon{
						Date:      uint64(100),
						Operation: "op#11",
						Module:    "mod#11",
					}},
					{Common: resps.MailUserHistoryItemCommon{
						Date:      uint64(90),
						Operation: "op#12",
						Module:    "mod#12",
					}},
					{Common: resps.MailUserHistoryItemCommon{
						Date:      uint64(80),
						Operation: "op#13",
						Module:    "mod#13",
					}},
				},
			},
			hbase: resps.MailUserHistoryResult{
				Items: []*resps.MailUserHistoryItem{
					{Common: resps.MailUserHistoryItemCommon{
						Date:      uint64(100),
						Operation: "op#11",
						Module:    "mod#11",
					}},
					{Common: resps.MailUserHistoryItemCommon{
						Date:      uint64(95),
						Operation: "op#22",
						Module:    "mod#22",
					}},
					{Common: resps.MailUserHistoryItemCommon{
						Date:      uint64(80),
						Operation: "op#23",
						Module:    "mod#23",
					}},
				},
			},
			expected: resps.MailUserHistoryResult{
				Items: []*resps.MailUserHistoryItem{
					{Common: resps.MailUserHistoryItemCommon{
						Date:      uint64(100),
						Operation: "op#11",
						Module:    "mod#11",
					}},
					{Common: resps.MailUserHistoryItemCommon{
						Date:      uint64(95),
						Operation: "op#22",
						Module:    "mod#22",
					}},
					{Common: resps.MailUserHistoryItemCommon{
						Date:      uint64(90),
						Operation: "op#12",
						Module:    "mod#12",
					}},
					{Common: resps.MailUserHistoryItemCommon{
						Date:      uint64(80),
						Operation: "op#13",
						Module:    "mod#13",
					}},
				},
			},
		},
		{ // check tail processing for yt-result
			yt: resps.MailUserHistoryResult{
				Items: []*resps.MailUserHistoryItem{
					{Common: resps.MailUserHistoryItemCommon{
						Date:      uint64(100),
						Operation: "op#11",
						Module:    "mod#11",
					}},
					{Common: resps.MailUserHistoryItemCommon{
						Date:      uint64(90),
						Operation: "op#12",
						Module:    "mod#12",
					}},
				},
			},
			hbase: resps.MailUserHistoryResult{
				Items: []*resps.MailUserHistoryItem{
					{Common: resps.MailUserHistoryItemCommon{
						Date:      uint64(95),
						Operation: "op#22",
						Module:    "mod#22",
					}},
				},
			},
			expected: resps.MailUserHistoryResult{
				Items: []*resps.MailUserHistoryItem{
					{Common: resps.MailUserHistoryItemCommon{
						Date:      uint64(100),
						Operation: "op#11",
						Module:    "mod#11",
					}},
					{Common: resps.MailUserHistoryItemCommon{
						Date:      uint64(95),
						Operation: "op#22",
						Module:    "mod#22",
					}},
					{Common: resps.MailUserHistoryItemCommon{
						Date:      uint64(90),
						Operation: "op#12",
						Module:    "mod#12",
					}},
				},
			},
		},
		{ // check tail processing for hbase-result
			yt: resps.MailUserHistoryResult{
				Items: []*resps.MailUserHistoryItem{
					{Common: resps.MailUserHistoryItemCommon{
						Date:      uint64(95),
						Operation: "op#22",
						Module:    "mod#22",
					}},
				},
			},
			hbase: resps.MailUserHistoryResult{
				Items: []*resps.MailUserHistoryItem{
					{Common: resps.MailUserHistoryItemCommon{
						Date:      uint64(100),
						Operation: "op#11",
						Module:    "mod#11",
					}},
					{Common: resps.MailUserHistoryItemCommon{
						Date:      uint64(90),
						Operation: "op#12",
						Module:    "mod#12",
					}},
				},
			},
			expected: resps.MailUserHistoryResult{
				Items: []*resps.MailUserHistoryItem{
					{Common: resps.MailUserHistoryItemCommon{
						Date:      uint64(100),
						Operation: "op#11",
						Module:    "mod#11",
					}},
					{Common: resps.MailUserHistoryItemCommon{
						Date:      uint64(95),
						Operation: "op#22",
						Module:    "mod#22",
					}},
					{Common: resps.MailUserHistoryItemCommon{
						Date:      uint64(90),
						Operation: "op#12",
						Module:    "mod#12",
					}},
				},
			},
		},
	}

	for idx, c := range cases {
		res, err := mergeMailUserHistoryResults(context.Background(), &c.yt, &c.hbase)
		require.NoError(t, err, idx)
		require.Equal(t, c.expected.Status, res.Status, idx)
		require.Equal(t, c.expected.UID, res.UID, idx)
		require.Equal(t, len(c.expected.Items), len(res.Items), idx)

		for cidx := range c.expected.Items {
			require.Equal(t,
				c.expected.Items[cidx].Common.Date,
				res.Items[cidx].Common.Date,
				idx, cidx,
			)
			require.Equal(t,
				c.expected.Items[cidx].Common.Operation,
				res.Items[cidx].Common.Operation,
				idx, cidx,
			)
			require.Equal(t,
				c.expected.Items[cidx].Common.Module,
				res.Items[cidx].Common.Module,
				idx, cidx,
			)
		}
	}
}
