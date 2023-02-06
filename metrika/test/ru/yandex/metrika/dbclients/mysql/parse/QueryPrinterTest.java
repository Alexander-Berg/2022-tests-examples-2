package ru.yandex.metrika.dbclients.mysql.parse;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Date;
import java.util.List;

import org.apache.commons.lang3.mutable.MutableLong;
import org.junit.Before;
import org.junit.Ignore;
import org.junit.Test;
import org.springframework.jdbc.core.RowMapper;

import ru.yandex.metrika.dbclients.clickhouse.HttpTemplateImpl;
import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;
import ru.yandex.metrika.tool.AllDatabases;
import ru.yandex.metrika.util.StringUtil;
import ru.yandex.metrika.util.app.XmlPropertyConfigurer;

/**
 * ssh -L 12342:localhost:8123 mtstatlog01d.yandex.ru
 *
 *
  CREATE TABLE `conv_main`.`test_queries_copy`(
  'Id` bigint(20) NOT NULL AUTO_INCREMENT,
  `EventDate` DATE,
  `EventDateTime` DATETIME,
  `Database` VARCHAR(32),
  `QuerySimple` varchar(4096) DEFAULT NULL,
  `QueryNorm` varchar(4096) DEFAULT NULL,
  `Uid` BIGINT,
  `Time` BIGINT,
   PRIMARY KEY (`Id`)
  );
* Created by orantius on 1/10/16.
 */
@Ignore
public class QueryPrinterTest {


    private HttpTemplateImpl chTemplate;
    private MySqlJdbcTemplate template;

    @Before
    public void setUp()  {
        chTemplate = AllDatabases.getCHTemplate("localhost", 12342, "stats");
        chTemplate.getProperties().setConnectionTimeout(30000);
        chTemplate.getProperties().setUser("default");
        chTemplate.getProperties().setSocketTimeout(30000);
        chTemplate.afterPropertiesSet();

        template = AllDatabases.getTemplate("localhost", 3311, "metrika", XmlPropertyConfigurer.getTextFromFile("~/.mysql/pass_old"), "conv_main");
    }

    @Test
    public void testSimple() throws Exception {
        String sql = "select concat(a,c) from b";
        String print = Sketch.normalize(sql);
        System.out.println("print = " + print);
    }

    List<List<Object>> buffer = new ArrayList<>();
    //EventDate, EventDateTime, Database, Query, Uid, Time
    RowMapper<List<String>> listRowMapper = (rs, ii) -> {
        if(ii%10000 ==0) {
            System.out.println(ii+" new Date() = " + new Date());
            template.batchInsert("insert into test_queries_copy(EventDate,EventDateTime,`Database`,QuerySimple,QueryNorm,Uid,`Time`)", buffer, 1000);
            buffer.clear();
        }
        String string = rs.getString(4);
        String print = Sketch.simplify(string);
        buffer.add(Arrays.asList("'"+rs.getString(1)+"'","'"+rs.getTimestamp(2)+"'", "'"+rs.getString(3)+"'",
                StringUtil.escape(rs.getString(4)), StringUtil.escape(print), rs.getLong(5), rs.getLong(6)));
        return Arrays.asList(string, print);
    };


    //@Test
    public void testAll() throws Exception {
        MutableLong count = new MutableLong();
        chTemplate.queryStreaming("select EventDate, EventDateTime, Database, Query, Uid, Time from mysql where EventDate = '2016-01-10' ", (rs)->{
            listRowMapper.mapRow(rs,count.intValue());
            count.increment();
        });

        template.batchInsert("insert into test_queries(EventDate,EventDateTime,`Database`,QuerySimple,QueryNorm,Uid,`Time`)", buffer, 1000);
        buffer.clear();

    }
}
