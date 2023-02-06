package ru.yandex.metrika.dbclients.mysql;

import java.util.concurrent.BrokenBarrierException;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.CyclicBarrier;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;
import org.springframework.dao.CannotAcquireLockException;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringRunner;

import ru.yandex.metrika.dbclients.config.JdbcTemplateConfig;

import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

@RunWith(SpringRunner.class)
@ContextConfiguration(classes = {DbUtilsTest.TestConfig.class})
public class DbUtilsTest {

    @Autowired
    protected MySqlJdbcTemplate convMainTemplate;
    @Autowired
    TransactionUtil transactionUtil;

    private static final String TABLE = "some_test_table";

    @Test
    public void testDropTempTable() {
        assertTrue(isTableExists("tmp_" + TABLE));
        DbUtils.dropTemporaryTable(TABLE, convMainTemplate);
        assertFalse(isTableExists("tmp_" + TABLE));
    }

    @Test
    public void testDropTempTableWithLock() throws InterruptedException, BrokenBarrierException, TimeoutException {
        assertTrue(isTableExists("tmp_" + TABLE));
        var inBarrier = new CyclicBarrier(2);
        var thread = new Thread(() -> transactionUtil.doInTransaction(() -> {
            convMainTemplate.execute("INSERT INTO tmp_" + TABLE + " VALUE (42)" );
            try {
                inBarrier.await(30, TimeUnit.SECONDS);
                Thread.sleep(TimeUnit.SECONDS.toMillis(5));
            } catch (InterruptedException | BrokenBarrierException | TimeoutException e) {
                e.printStackTrace();
                throw new RuntimeException(e);
            }
        }));
        thread.start();
        inBarrier.await(30, TimeUnit.SECONDS);
        DbUtils.dropTemporaryTable(TABLE, convMainTemplate);
        thread.join(TimeUnit.SECONDS.toMillis(30));
        assertFalse(isTableExists("tmp_" + TABLE));
        assertTrue(hasValue(TABLE, 42));
    }


    @Test(expected = CannotAcquireLockException.class)
    public void testDropTempTableWithTimeoutLock() throws InterruptedException, BrokenBarrierException, TimeoutException {
        assertTrue(isTableExists("tmp_" + TABLE));
        var inBarrier = new CyclicBarrier(2);
        var latch = new CountDownLatch(1);
        var thread = new Thread(() -> transactionUtil.doInTransaction(() -> {
            convMainTemplate.execute("INSERT INTO tmp_" + TABLE + " VALUE (42)" );
            try {
                inBarrier.await(30, TimeUnit.SECONDS);
                assertTrue(latch.await(30, TimeUnit.SECONDS));
            } catch (InterruptedException | BrokenBarrierException | TimeoutException e) {
                e.printStackTrace();
            }
        }));
        thread.start();
        inBarrier.await(30, TimeUnit.SECONDS);
        try {
            DbUtils.dropTemporaryTableWithTimeout(TABLE, convMainTemplate, 1);
        } finally {
            latch.countDown();
            thread.join();
        }
        assertFalse(isTableExists("tmp_" + TABLE));
        assertTrue(hasValue(TABLE, 42));
    }

    @Before
    public void setup() {
        convMainTemplate.execute("CREATE TABLE IF NOT EXISTS " + TABLE + "(v int)");
        DbUtils.createTemporaryTable(TABLE, convMainTemplate);
    }

    private boolean isTableExists(String table) {
        return Boolean.TRUE.equals(convMainTemplate.queryForObject(
                "SELECT COUNT(*) > 0\n" +
                "FROM information_schema.tables " +
                "WHERE table_schema = DATABASE() " +
                "  AND table_name = \"" + table + "\"", Boolean.class));
    }

    private boolean hasValue(String table, int val) {
        return Boolean.TRUE.equals(convMainTemplate.queryForObject(
                "SELECT COUNT(*) > 0 " +
                        "FROM " + table + " " +
                        "WHERE v = " + val, Boolean.class));
    }

    @Configuration
    @Import({
            JdbcTemplateConfig.class
    })
    static class TestConfig {
    }
}
