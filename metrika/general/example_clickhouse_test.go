package clickhouse_test

import (
	"encoding/xml"
	"fmt"

	"a.yandex-team.ru/metrika/go/pkg/clickhouse"
)

var config = []byte(`
<yandex>
	<my_option>1</my_option>
	<ch>
		<shard>
			<replica>
				<compression>true</compression>
				<db>merge</db>
				<user>metrika_engine</user>
				<clickhouse_connect_timeout>1</clickhouse_connect_timeout>
				<clickhouse_send_timeout>5</clickhouse_send_timeout>
				<host>mtgiga001-1.metrika.yandex.net</host>
				<port>9000</port>
			</replica>
			<replica>
				<compression>true</compression>
				<db>merge</db>
				<user>metrika_engine</user>
				<clickhouse_connect_timeout>1</clickhouse_connect_timeout>
				<clickhouse_send_timeout>5</clickhouse_send_timeout>
				<host>mtgiga001-2.metrika.yandex.net</host>
				<port>9000</port>
			</replica>
			<replica>
				<compression>true</compression>
				<db>merge</db>
				<user>metrika_engine</user>
				<clickhouse_connect_timeout>1</clickhouse_connect_timeout>
				<clickhouse_send_timeout>5</clickhouse_send_timeout>
				<host>mtgiga001-3.metrika.yandex.net</host>
				<port>9000</port>
			</replica>
			<layer>1</layer>
			<weight>1</weight>
			<internal_replication>1</internal_replication>
		</shard>
		<shard>
			<replica>
				<compression>true</compression>
				<db>merge</db>
				<user>core</user>
				<clickhouse_connect_timeout>1</clickhouse_connect_timeout>
				<clickhouse_send_timeout>50</clickhouse_send_timeout>
				<host>mtgiga002-1.metrika.yandex.net</host>
				<port>9000</port>
			</replica>
			<replica>
				<compression>true</compression>
				<db>merge</db>
				<user>core</user>
				<clickhouse_connect_timeout>1</clickhouse_connect_timeout>
				<clickhouse_send_timeout>50</clickhouse_send_timeout>
				<host>mtgiga002-2.metrika.yandex.net</host>
				<port>9000</port>
			</replica>
			<replica>
				<compression>true</compression>
				<db>merge</db>
				<user>core</user>
				<clickhouse_connect_timeout>1</clickhouse_connect_timeout>
				<clickhouse_send_timeout>50</clickhouse_send_timeout>
				<host>mtgiga002-3.metrika.yandex.net</host>
				<port>9000</port>
			</replica>
			<layer>1</layer>
			<weight>1</weight>
			<internal_replication>1</internal_replication>
		</shard>
	</ch>
</yandex>
`)

type Config struct {
	MyOpt int                `xml:"my_option"`
	CH    []clickhouse.Shard `xml:"ch>shard"`
}

func Example() {
	var cfg Config
	_ = xml.Unmarshal(config, &cfg)
	shard1DSN, _ := cfg.CH[0].MakeDSN()
	shard2DSN, _ := cfg.CH[1].MakeDSN()
	fmt.Println(shard1DSN)
	fmt.Println(shard2DSN)
	// Output:
	// tcp://mtgiga001-1.metrika.yandex.net:9000?alt_hosts=mtgiga001-2.metrika.yandex.net%3A9000%2Cmtgiga001-3.metrika.yandex.net%3A9000&compress=true&database=merge&user=metrika_engine&write_timeout=5
	// tcp://mtgiga002-1.metrika.yandex.net:9000?alt_hosts=mtgiga002-2.metrika.yandex.net%3A9000%2Cmtgiga002-3.metrika.yandex.net%3A9000&compress=true&database=merge&user=core&write_timeout=50
}
