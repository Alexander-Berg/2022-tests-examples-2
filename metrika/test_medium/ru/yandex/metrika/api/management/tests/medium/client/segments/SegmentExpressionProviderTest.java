package ru.yandex.metrika.api.management.tests.medium.client.segments;

import javax.annotation.Nonnull;

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

import ru.yandex.metrika.api.management.client.segments.Segment;
import ru.yandex.metrika.api.management.client.segments.SegmentExpressionProvider;
import ru.yandex.metrika.api.management.client.segments.SegmentRetargeting;
import ru.yandex.metrika.api.management.client.segments.SegmentSource;
import ru.yandex.metrika.api.management.client.segments.SegmentStatus;
import ru.yandex.metrika.api.management.client.segments.SegmentsDao;
import ru.yandex.metrika.api.management.client.segments.SegmentsExpressionHistoryDao;
import ru.yandex.metrika.api.management.client.segments.streamabillity.StreamabilityClass;
import ru.yandex.metrika.api.management.config.JdbcTemplateConfig;
import ru.yandex.metrika.auth.AuthUtils;
import ru.yandex.metrika.auth.MetrikaUserDetails;
import ru.yandex.metrika.dbclients.MySqlTestSetup;
import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;

@RunWith(SpringRunner.class)
@ContextConfiguration
public class SegmentExpressionProviderTest {

    private static final int oldVer = 1;
    private static final int newVer = 2;
    private static final int counterId = 42;
    private static final MetrikaUserDetails FAKE_USER = AuthUtils.buildSimpleUserDetails(42, "localhost");

    @BeforeClass
    public static void beforeClass() throws Exception {
        MySqlTestSetup.globalSetup();
    }

    @Autowired
    private SegmentsExpressionHistoryDao segmentsExpressionHistoryDao;

    @Autowired
    private SegmentsDao segmentsDao;

    @Autowired
    private SegmentExpressionProvider segmentExpressionProvider;

    @Autowired
    private MySqlJdbcTemplate convMainTemplate;

    @Before
    public void setUp() throws Exception {
        convMainTemplate.update("TRUNCATE " + SegmentsExpressionHistoryDao.SEGMENTS_EXPRESSION_HISTORY_TABLE);
        convMainTemplate.update("TRUNCATE segments");
    }


    @Test
    public void getActualVersion() {
        var expression = "ym:s:age > 10";
        var segmentId = segmentsDao.createSegment(FAKE_USER, segment(expression), counterId);
        var actualExpression = segmentExpressionProvider.getActualExpression(segmentId);
        Assert.assertEquals(expression, actualExpression);
    }

    @Test
    public void getActualVersionWhenOldExists() {
        var expressionOld = "ym:s:age > 9";
        var expressionNew = "ym:s:age > 10";
        var segmentId = segmentsDao.createSegment(FAKE_USER, segment(expressionNew, newVer), counterId);
        segmentsExpressionHistoryDao.saveVersion(segmentId, oldVer, expressionOld);
        var actualExpression = segmentExpressionProvider.getActualExpression(segmentId);
        Assert.assertEquals(expressionNew, actualExpression);
    }

    @Test
    public void getOldVersion() {
        var expressionOld = "ym:s:age > 9";
        var expressionNew = "ym:s:age > 10";
        var segment = segment(expressionOld);

        var segmentId = segmentsDao.createSegment(FAKE_USER, segment, counterId);

        segment.setSegmentId(segmentId);
        segment.setExpression(expressionNew);
        segment.incrementExpressionVersion();
        segmentsExpressionHistoryDao.saveVersion(segmentId, oldVer, expressionOld);
        segmentsDao.updateSegment(segmentId, counterId, segment);

        var actualExpression = segmentExpressionProvider.getExpressionByVersion(segmentId, oldVer);
        Assert.assertEquals(expressionOld, actualExpression);
    }

    @SuppressWarnings("SameParameterValue")
    @Nonnull
    private Segment segment(String expression, int expressionVersion) {
        var segment = segment(expression);
        segment.setExpressionVersion(expressionVersion);
        return segment;
    }

    @Nonnull
    private Segment segment(String expression) {
        return new Segment(
                0, counterId, "s", expression, 1, FAKE_USER.getUid(), false,
                SegmentStatus.active, SegmentSource.API, SegmentRetargeting.NEED_RECALCULATION, StreamabilityClass.NOT_STREAMABLE
        );
    }

    @Configuration
    @Import(JdbcTemplateConfig.class)
    static class Config {
        @Bean
        public SegmentsExpressionHistoryDao segmentsExpressionHistoryDao(MySqlJdbcTemplate convMainTemplate) {
            return new SegmentsExpressionHistoryDao(convMainTemplate);
        }
        @Bean
        public SegmentsDao segmentsDao(MySqlJdbcTemplate convMainTemplate) {
            return new SegmentsDao(convMainTemplate);
        }

        @Bean
        public SegmentExpressionProvider segmentExpressionProvider(SegmentsDao segmentsDao, SegmentsExpressionHistoryDao segmentsExpressionHistoryDao) {
            return new SegmentExpressionProvider(segmentsDao, segmentsExpressionHistoryDao);
        }
    }
}
