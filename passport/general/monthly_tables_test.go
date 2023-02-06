package ytc

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestMonthlyTables(t *testing.T) {
	cases := []struct {
		from   uint64
		to     uint64
		tables []string
	}{
		{ // Чт дек  3 00:03:20 MSK 2020 -> Вт фев  2 03:46:40 MSK 2021
			from:   1606943000,
			to:     1612226800,
			tables: []string{"2021-02", "2021-01", "2020-12"},
		},
		{ // Вт фев  2 01:00:00 MSK 2021 -> Вт фев  2 03:46:40 MSK 2021
			from:   1612216800,
			to:     1612226800,
			tables: []string{"2021-02"},
		},
		{ // Вт фев  2 03:46:40 MSK 2021 -> Вт фев  2 01:00:00 MSK 2021
			from:   1612226800,
			to:     1612216800,
			tables: []string{},
		},
		{ // Сб окт  2 00:00:00 MSK 2021 -> Пт дек 31 00:00:00 MSK 2021
			from:   1633122000,
			to:     1640898000,
			tables: []string{"2021-12", "2021-11", "2021-10"},
		},
		{ // Вс янв 31 00:00:00 MSK 2021 -> Пн мрт 29 00:00:00 MSK 2021
			from:   1612040400,
			to:     1616965200,
			tables: []string{"2021-03", "2021-02", "2021-01"},
		},
	}

	for idx, c := range cases {
		m := NewMonthlyTables(c.from, c.to)

		tables := make([]string, 0)
		for m.Next() {
			tables = append(tables, m.TableName())
		}

		require.Equal(t, c.tables, tables, idx)
	}

}
