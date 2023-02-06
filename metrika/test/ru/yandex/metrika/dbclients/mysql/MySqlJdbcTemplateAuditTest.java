package ru.yandex.metrika.dbclients.mysql;

import java.sql.Types;
import java.util.Arrays;

import org.junit.Before;
import org.junit.Ignore;
import org.junit.Test;

import ru.yandex.metrika.tool.AllDatabases;
import ru.yandex.metrika.util.app.XmlPropertyConfigurer;

@Ignore
public class MySqlJdbcTemplateAuditTest {

    MySqlJdbcTemplateAudit target;
    @Before
    public void setUp() throws Exception {
        target = new MySqlJdbcTemplateAudit(AllDatabases.getDataSource("localhost", 3312, "metrica", XmlPropertyConfigurer.getTextFromFile("~/.mysql/pass_new"), "conv_main"));
        target.setAuditableTables(Arrays.asList("markedphones2_orders"));
    }

    @Test
    public void testBatchUpdateGeneratedKey() throws Exception {

    }

    @Test
    public void testUpdate() throws Exception {
        // insert - с известным id
        target.update("insert into markedphones2_orders (`order_id`,`uid`,`goods_id`,`numberodays_purchased`,`create_date`,`numberodays_used`,`notify_num`)" +
                "values(200,200,1,1,'"+ MySqlJdbcTemplateAudit.DTF.print(System.currentTimeMillis())+"',0,0)");

        target.update("insert into markedphones2_orders (`order_id`,`uid`,`goods_id`,`numberodays_purchased`,`create_date`,`numberodays_used`,`notify_num`)" +
                "values(?,?,?,?,?,?,?)", 200,200,1,1, MySqlJdbcTemplateAudit.DTF.print(System.currentTimeMillis()), 0,0);
        // insert c генерированным id
        target.update("insert into markedphones2_orders (`uid`,`goods_id`,`numberodays_purchased`,`create_date`,`numberodays_used`,`notify_num`)" +
                "values(?,?,?,?,?,?)", 200,1,1, MySqlJdbcTemplateAudit.DTF.print(System.currentTimeMillis()), 0,0);

        // update по id
        // Update - строка
        target.update("update markedphones2_orders set numberodays_used = 0 where order_id = 199");
        // update - с аргументами
        target.update("update markedphones2_orders set numberodays_used = ? where order_id = ?",1,199);
        // update - с аргументами/типами
        target.update("update markedphones2_orders set numberodays_used = ? where order_id = ?",new Object[]{1,199}, new int[]{Types.INTEGER, Types.BIGINT});

        // апдейт множества строк
        target.update("update markedphones2_orders set numberodays_used = 0 where numberodays_used = 30");
        // delete по id
        target.update("delete from markedphones2_orders where numberodays_used = 30");
        // delete по условию
        target.update("delete from markedphones2_orders where order_id = 200");
    }

    @Test
    public void testBatchUpdate() throws Exception {

    }

    @Test
    public void testUpdate1() throws Exception {

    }

    @Test
    public void testUpdate2() throws Exception {

    }

    @Test
    public void testBatchUpdate1() throws Exception {

    }

    @Test
    public void testBatchUpdate2() throws Exception {

    }

    @Test
    public void testUpdateRowGetGeneratedKey() throws Exception {

    }

    @Test
    public void testUpdateGeneratedKey() throws Exception {

    }

    @Test
    public void testBatchUpdateGeneratedKey1() throws Exception {

    }

    @Test
    public void testBatchUpdate3() throws Exception {

    }

    @Test
    public void testBatchUpdate4() throws Exception {

    }

    @Test
    public void testBatchDelete() throws Exception {

    }

    @Test
    public void testUpdate3() throws Exception {

    }

    @Test
    public void testBatchUpdate5() throws Exception {

    }

    @Test
    public void testUpdate4() throws Exception {

    }

    @Test
    public void testUpdate5() throws Exception {

    }

    @Test
    public void testUpdate6() throws Exception {

    }

    @Test
    public void testUpdate7() throws Exception {

    }

    @Test
    public void testUpdate8() throws Exception {

    }

    @Test
    public void testBatchUpdate6() throws Exception {

    }

    @Test
    public void testBatchUpdate7() throws Exception {

    }

    @Test
    public void testBatchUpdate8() throws Exception {

    }

    @Test
    public void testBatchUpdate9() throws Exception {

    }

}
