package ru.yandex.metrika.schedulerd.cron.task;

import java.util.Arrays;

import org.junit.Before;
import org.junit.Ignore;
import org.junit.Test;
import org.springframework.jdbc.core.JdbcTemplate;

import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;
import ru.yandex.metrika.dbclients.yt.YtDatabase;
import ru.yandex.metrika.tool.AllDatabases;
import ru.yandex.yql.YqlDataSource;
import ru.yandex.yql.settings.YqlProperties;

@Ignore
public class YabsPageTaskTest {

    public static final String TOKEN = "";
    private YabsPageTask target;

    @Before
    public void setUp() throws Exception {
        target = new YabsPageTask();
        YtDatabase blocks = new YtDatabase();
        blocks.setTableYTPath("//home/metrika/yabs");
        blocks.setTableName("blocks");
        blocks.setToken(TOKEN);
        blocks.setProxies(Arrays.asList("hahn.yt.yandex.net"));
        blocks.afterPropertiesSet();
        target.setBlocks(blocks);

        YtDatabase pages = new YtDatabase();
        pages.setTableYTPath("//home/metrika/yabs");
        pages.setTableName("pages");
        pages.setToken(TOKEN);
        pages.setProxies(Arrays.asList("hahn.yt.yandex.net"));
        pages.afterPropertiesSet();
        target.setPages(pages);

        YqlProperties p = new YqlProperties();
        p.setPassword(TOKEN);
        YqlDataSource d = new YqlDataSource("jdbc:yql://yql.yandex.net:443/hahn", p);
        JdbcTemplate ytTemplate = new JdbcTemplate(d); //
        target.setYtTemplate(ytTemplate);
        MySqlJdbcTemplate dicts = AllDatabases.getTemplate("localhost", 3343, "metrika", "J", "dicts");
        target.setDicts(dicts);
        target.afterPropertiesSet();
    }

    @Test
    public void execute() throws Exception {
        target.execute();
    }

}
