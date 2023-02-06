package ru.yandex.metrika.segments.clickhouse.optim;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.junit.Ignore;
import org.junit.Test;

import ru.yandex.clickhouse.response.ClickHouseResultSet;
import ru.yandex.clickhouse.settings.ClickHouseProperties;
import ru.yandex.clickhouse.settings.ClickHouseQueryParam;
import ru.yandex.metrika.dbclients.clickhouse.HttpTemplate;
import ru.yandex.metrika.dbclients.clickhouse.MetrikaClickHouseProperties;
import ru.yandex.metrika.dbclients.mysql.RowMappers;
import ru.yandex.metrika.tool.AllDatabases;

/**
 * Created by orantius on 20.02.17.
 */
@Ignore
public class CardinalityEstimatorImplTest {


    @Test
    public void estimate() throws Exception {
        ClickHouseProperties properties = new MetrikaClickHouseProperties();
        properties.setConnectionTimeout(1000000);
        properties.setMaxExecutionTime(1000000);
        properties.setSocketTimeout(1000000);
        properties.setUser("auditory_geo");

        HttpTemplate template = AllDatabases.getCHTemplate("localhost", 12301, "default", properties);

// timeout_before_checking_execution_speed='60'
        Map<ClickHouseQueryParam, String> additionalClickHouseDBParams = new HashMap<>();
        additionalClickHouseDBParams.put(ClickHouseQueryParam.MAX_EXECUTION_TIME, "1000000");
        additionalClickHouseDBParams.put(ClickHouseQueryParam.RECEIVE_TIMEOUT, "1000000");
        additionalClickHouseDBParams.put(ClickHouseQueryParam.CONNECT_TIMEOUT, "1000000");
        List<String> columns = template.query("desc table visits_all", RowMappers.STRING);
        columns = columns.subList(384, columns.size()); // до 375 был 2016-12-22, потом поменял на 2017-01-19 т.к. читались битые файлы.  https://st.yandex-team.ru/CLICKHOUSE-2855
        System.out.println("columns = " + columns);
        for (String column : columns) {
            String sql = "SELECT \n" +
                    "    arrayMap(x->toUInt32(x),quantiles(0, 0.25, 0.5, 0.75, 1)(size)) AS distr, \n" +
                    "    toInt32(avg(size)), \n" +
                    "    count()\n" +
                    "FROM \n" +
                    "(\n" +
                    "    SELECT \n" +
                    "        CounterID, \n" +
                    //"        uniq(" + column + ") AS size\n" +
                    "        uniqArray(" + column + ") AS size\n" +
                    "    FROM visits_all \n" +
                    "    WHERE (StartDate = '2016-11-12') \n" +
                    "    GROUP BY CounterID\n" +
                    "    HAVING count() > 1000\n" +
                    "    SETTINGS max_rows_to_read = 30000000000, max_memory_usage = 20000000000\n" +
                    ") \n";
            Data query = template.query(sql, (rs, i) -> {
                Data data = new Data();
                data.col = column;
                data.quantiles = ((ClickHouseResultSet) rs).getLongArray(1);
                data.avg = rs.getInt(2);
                data.count = rs.getInt(3);
                return data;
            }).get(0);
            System.out.println(query);
        }
    }

    static class Data {
        String col;
        long[] quantiles;
        int avg;
        int count;

        @Override
        public String toString() {
            return col + '\t' + quantiles[0] + '\t' + quantiles[1] + '\t' + quantiles[2] +
                    '\t' + quantiles[3] + '\t' + quantiles[4] + '\t' + avg + '\t' + count;
        }
    }
}
