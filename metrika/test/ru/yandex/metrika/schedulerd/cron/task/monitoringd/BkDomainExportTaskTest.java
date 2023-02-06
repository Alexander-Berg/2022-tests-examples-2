package ru.yandex.metrika.schedulerd.cron.task.monitoringd;

import java.sql.Connection;
import java.sql.SQLException;
import java.util.Date;
import java.util.Properties;

import javax.sql.DataSource;

import com.google.common.base.Stopwatch;
import org.junit.Ignore;
import org.junit.Test;
import org.springframework.jdbc.datasource.DriverManagerDataSource;

import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;
import ru.yandex.metrika.util.app.XmlPropertyConfigurer;

public class BkDomainExportTaskTest {


    private static DataSource createDs() {
        try {
            DriverManagerDataSource dmds = new DriverManagerDataSource();

            dmds.setDriverClassName("com.mysql.cj.jdbc.Driver");
            dmds.setUrl("jdbc:mysql://localhost:25702/conv_main");
            dmds.setUsername("metrica");
            dmds.setPassword(XmlPropertyConfigurer.getTextFromFile("~/.mysql/pass_new"));
            Properties p = new Properties();
            p.setProperty("autocommit", "true");
            dmds.setConnectionProperties(p);

            Connection con = dmds.getConnection();

            con.close();
            return dmds;
        } catch(SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Test
    @Ignore
    public void testInitForbiddenPattern() {
        final BkDomainExportTask task = new BkDomainExportTask();
        task.initForbiddenPattern();
        assert !task.isDomainValid("pala.ucoz.ru");
        assert task.isDomainValid("gmail.com");
        assert !task.isDomainValid("xpeh.narod.ru");
    }

    @Test
    @Ignore
    public void testFullExportX() {

        DataSource dmds = createDs();

        final DomainCountersDao dcd = new DomainCountersDao() {{
            setJdbcTemplate(new MySqlJdbcTemplate(dmds));
        }};

        final BkDomainExportTask task = new BkDomainExportTask() {{
            setConvMain(new MySqlJdbcTemplate(dmds));
            setDomainCountersDao(dcd);
            setState(new MyState());
        }};

        task.initForbiddenPattern();

        Stopwatch sw = Stopwatch.createStarted();
        System.out.println("Fix :" + new Date(task.getCountersMaxUpdateTime()));
        task.fillDomainCounters();
        System.out.println(" Ellapsed: " + sw.stop());
    }

    @Test
    @Ignore
    public void testFullExport1() {

        DataSource dmds = createDs();

        final DomainCountersDao dcd = new DomainCountersDao() {{
            setJdbcTemplate(new MySqlJdbcTemplate(dmds));
        }};

        final BkDomainExportTask task = new BkDomainExportTask() {{
            setConvMain(new MySqlJdbcTemplate(dmds));
            setDomainCountersDao(dcd);
            setState(new MyState());
        }};

        task.initForbiddenPattern();

        Stopwatch sw = Stopwatch.createStarted();
        System.out.println("Fix :" + new Date(task.getCountersMaxUpdateTime()));
        // task.jmxTestFullExport();
        System.out.println(" Ellapsed: " + sw.stop());
        //
    }


    @Test
    @Ignore
    public void testDomainsScan() {
        DataSource dmds = createDs();

        final DomainCountersDao dcd = new DomainCountersDao() {{
            setJdbcTemplate(new MySqlJdbcTemplate(dmds));
        }};

        final BkDomainExportTask task = new BkDomainExportTask() {{
            setConvMain(new MySqlJdbcTemplate(dmds));
            setDomainCountersDao(dcd);
            setState(new MyState());
        }};

        task.initForbiddenPattern();

        System.out.println("Fix :" + new Date(task.getCountersMaxUpdateTime()));
        System.out.println("DEL" + dcd.delete(22));
    }

    @Test
    @Ignore
    public void testX() {

        DataSource dmds = createDs();

        final DomainCountersDao dcd = new DomainCountersDao() {{
            setJdbcTemplate(new MySqlJdbcTemplate(dmds));
        }};

        int i = 0;
        for (DomainCountersDao.DomainCounterRec ignored : dcd.findAll()) {
            ++ i;
        }

        System.out.println(" h" +i);
    }
}
