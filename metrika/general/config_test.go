package clickhouse

import (
	"encoding/xml"
	"fmt"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestConfig(t *testing.T) {
	testCases := []struct {
		c Shard
		e string
	}{
		{
			c: Shard{
				Replicas: []Replica{
					{
						Host:         "asd",
						Port:         9000,
						User:         "my_user",
						Password:     "qwerty",
						Database:     "xxx",
						ReadTimeout:  10,
						WriteTimeout: 20,
						Secure:       true,
						Compress:     true,
					},
					{
						Host:         "second",
						Port:         9001,
						User:         "my_user",
						Password:     "qwerty",
						Database:     "xxx",
						ReadTimeout:  10,
						WriteTimeout: 20,
						Secure:       true,
						Compress:     true,
					},
					{
						Host:         "third",
						Port:         9002,
						User:         "my_user",
						Password:     "qwerty",
						Database:     "xxx",
						ReadTimeout:  10,
						WriteTimeout: 20,
						Secure:       true,
						Compress:     true,
					},
				},
				ConnectionOpenStrategy: "random",
				BlockSize:              2000,
				PoolSize:               90,

				SkipVerify: true,
				TLSConfig:  "wtf",
			},
			e: "tcp://asd:9000" +
				"?alt_hosts=second%3A9001%2Cthird%3A9002" +
				"&block_size=2000" +
				"&compress=true" +
				"&connection_open_strategy=random" +
				"&database=xxx" +
				"&password=qwerty" +
				"&pool_size=90" +
				"&read_timeout=10" +
				"&secure=true" +
				"&skip_verify=true" +
				"&tls_config=wtf" +
				"&user=my_user" +
				"&write_timeout=20",
		},
		{
			c: Shard{
				Replicas: []Replica{
					{
						Host: "host1",
						Port: 9000,
						User: "default",
					},
					{
						Host: "host2",
						Port: 9000,
						User: "default",
					},
				},
				Database: "qwe",
			},
			e: "tcp://host1:9000?alt_hosts=host2%3A9000&database=qwe&user=default",
		},
	}

	for i, tc := range testCases {
		t.Run(fmt.Sprintf("%d", i), func(t *testing.T) {
			dsn, err := tc.c.MakeDSN()
			require.NoError(t, err)
			assert.Equal(t, tc.e, dsn)
		})
	}
}

func TestXMLConfig(t *testing.T) {
	testCases := []struct {
		c []byte
		e string
	}{
		{
			c: []byte(`
<section>
	<max_block_size>25000000</max_block_size>
	<save_period>300</save_period>
	<time_period>600</time_period>
	<db>mydb</db>
	<replica>
		<host>host1</host>
		<port>9440</port>
		<user>metrika</user>
		<password>pass</password>
		<secure>true</secure>
		<clickhouse_read_timeout>10</clickhouse_read_timeout>
	</replica>
	<replica>
		<host>host2</host>
		<port>9440</port>
		<user>metrika</user>
		<password>pass</password>
		<secure>true</secure>
		<clickhouse_read_timeout>10</clickhouse_read_timeout>
	</replica>
</section>
`),
			e: "tcp://host1:9440" +
				"?alt_hosts=host2%3A9440" +
				"&block_size=25000000" +
				"&database=mydb" +
				"&password=pass" +
				"&read_timeout=10" +
				"&secure=true" +
				"&user=metrika",
		},
		{
			c: []byte(`
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
`),
			e: "tcp://mtgiga001-1.metrika.yandex.net:9000" +
				"?alt_hosts=mtgiga001-2.metrika.yandex.net%3A9000%2Cmtgiga001-3.metrika.yandex.net%3A9000" +
				"&compress=true" +
				"&database=merge" +
				"&user=metrika_engine" +
				"&write_timeout=5",
		},
	}

	for i, tc := range testCases {
		t.Run(fmt.Sprintf("%d", i), func(t *testing.T) {
			var cfg Shard
			err := xml.Unmarshal(tc.c, &cfg)
			require.NoError(t, err)
			dsn, err := cfg.MakeDSN()
			require.NoError(t, err)
			assert.Equal(t, tc.e, dsn)
		})
	}
}

func TestDebug(t *testing.T) {
	s := Shard{Replicas: []Replica{{Host: "localhost", Port: 9000}}}
	dsn, err := s.SetDebug().MakeDSN()
	require.NoError(t, err)
	assert.Equal(t, "tcp://localhost:9000?debug=true", dsn)
}

func TestErrors(t *testing.T) {
	testCases := []struct {
		s *Shard
		e error
	}{
		{
			s: &Shard{},
			e: EmptyShardError,
		},
		{
			s: &Shard{
				Replicas: []Replica{
					{
						Port: 8123,
					},
				},
			},
			e: EmptyHostError,
		},
		{
			s: &Shard{
				Replicas: []Replica{
					{
						Host: "asd",
					},
				},
			},
			e: EmptyPortError,
		},
	}
	for i, tc := range testCases {
		t.Run(fmt.Sprintf("%d", i), func(t *testing.T) {
			_, err := tc.s.MakeDSN()
			require.Error(t, err)
			assert.Equal(t, tc.e, err)
		})
	}
}
