package ru.yandex.metrika.api.management.tests.medium.client.segments;

import java.util.Map;

import org.apache.commons.lang3.tuple.Pair;
import org.junit.Assert;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringRunner;

import ru.yandex.metrika.api.management.client.segments.SegmentsExpressionHistoryDao;
import ru.yandex.metrika.api.management.config.JdbcTemplateConfig;
import ru.yandex.metrika.dbclients.MySqlTestSetup;
import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;

@RunWith(SpringRunner.class)
@ContextConfiguration
public class SegmentsExpressionHistoryDaoTest {

    @BeforeClass
    public static void beforeClass() throws Exception {
        MySqlTestSetup.globalSetup();
    }

    @Autowired
    private SegmentsExpressionHistoryDao segmentsExpressionHistoryDao;

    @Autowired
    private MySqlJdbcTemplate convMainTemplate;

    @Before
    public void setUp() throws Exception {
        convMainTemplate.update("TRUNCATE " + SegmentsExpressionHistoryDao.SEGMENTS_EXPRESSION_HISTORY_TABLE);
    }

    @Test
    public void addNewVersion() {
        var expression = "ym:s:age > 10";
        segmentsExpressionHistoryDao.saveVersion(1, 1, expression);
        var fromDB = segmentsExpressionHistoryDao.getExpression(1, 1);
        Assert.assertTrue("Expected not empty optional from DB", fromDB.isPresent());
        Assert.assertEquals(expression, fromDB.get());
    }

    @Test
    public void addManyVersions() {
        var values = Map.of(
                Pair.of(1, 1), "ym:s:age > 10",
                Pair.of(1, 2), "ym:s:age > 11",
                Pair.of(1, 3), "ym:s:age > 12",
                Pair.of(2, 1), "ym:s:age > 13",
                Pair.of(2, 2), "ym:s:age > 14",
                Pair.of(3, 1), "ym:s:age > 15"
        );
        values.forEach((p, e) -> segmentsExpressionHistoryDao.saveVersion(p.getLeft(), p.getRight(), e));
        var fromDB = segmentsExpressionHistoryDao.getExpressionsByVersions(values.keySet());
        Assert.assertEquals(values, fromDB);
    }

    @Configuration
    @Import(JdbcTemplateConfig.class)
    static class Config {
        @Bean
        public SegmentsExpressionHistoryDao segmentsExpressionHistoryDao(MySqlJdbcTemplate convMainTemplate) {
            return new SegmentsExpressionHistoryDao(convMainTemplate);
        }
    }
}
