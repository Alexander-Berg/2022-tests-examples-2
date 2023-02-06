package ru.yandex.metrika.dbclients.mysql;

import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.Statement;

import org.apache.logging.log4j.Level;
import org.junit.Before;
import org.junit.Ignore;
import org.junit.Test;

import ru.yandex.metrika.util.log.Log4jSetup;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;


public class TransactionalMetrikaDataSourceTest {

    @Before
    public void setUp() throws Exception {
        Log4jSetup.basicSetup(Level.DEBUG);
    }

    @Test
    @Ignore("METRIQA-936")
    public void testOpenAndCloseConnection() throws Exception {
        TransactionalMetrikaDataSource dataSource = new DataSourceFactory().getDataSource();
        dataSource.setHost("127.0.0.1");
        dataSource.setUser("root");
        dataSource.setDb("information_schema");
        dataSource.afterPropertiesSet();

        try (Connection cn = dataSource.getConnection()) {
            assertEquals(1, dataSource.getConnectionsInUse());
            try (Statement st = cn.createStatement(); ResultSet rs = st.executeQuery("SELECT 1")) {
                assertTrue(rs.next());
                assertEquals(1, rs.getInt(1));
                assertFalse(rs.next());
            }
        }
        assertEquals(0, dataSource.getConnectionsInUse());
    }
}
