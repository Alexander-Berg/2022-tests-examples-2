package ru.yandex.metrika.api.management.tests.medium.client.segments;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

import javax.annotation.Nonnull;

import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringRunner;

import ru.yandex.metrika.api.management.client.CounterLimitsService;
import ru.yandex.metrika.api.management.client.counter.CounterOptionsDao;
import ru.yandex.metrika.api.management.client.counter.CounterOptionsService;
import ru.yandex.metrika.api.management.client.segments.Segment;
import ru.yandex.metrika.api.management.client.segments.SegmentParseService;
import ru.yandex.metrika.api.management.client.segments.SegmentParseServiceStreamabilityClassificationTest;
import ru.yandex.metrika.api.management.client.segments.SegmentSource;
import ru.yandex.metrika.api.management.client.segments.SegmentsDao;
import ru.yandex.metrika.api.management.client.segments.SegmentsExpressionHistoryDao;
import ru.yandex.metrika.api.management.client.segments.SegmentsService;
import ru.yandex.metrika.api.management.config.JdbcTemplateConfig;
import ru.yandex.metrika.dbclients.MySqlTestSetup;
import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;
import ru.yandex.metrika.dbclients.mysql.RowMappers;
import ru.yandex.metrika.retargeting.SegmentUpdateReason;
import ru.yandex.metrika.segments.core.ApiUtils;
import ru.yandex.metrika.segments.core.parser.SimpleTestSetup;

import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.notNullValue;
import static org.junit.Assert.assertThat;
import static ru.yandex.metrika.CommonTestsHelper.FAKE_USER;
import static ru.yandex.metrika.CommonTestsHelper.counterId;

@RunWith(SpringRunner.class)
@ContextConfiguration
public class SegmentServiceTest{

    private static final String segmentName = "simple name";
    private static final String segmentExpression = "ym:s:startURL == 'ya.ru'";

    @Autowired
    public SegmentsService segmentsService;
    @Autowired
    public MySqlJdbcTemplate convMainTemplate;
    @Autowired
    public SegmentsExpressionHistoryDao segmentsExpressionHistoryDao;

    @BeforeClass
    public static void beforeClass() throws Exception {
        MySqlTestSetup.globalSetup();
    }

    @Before
    public void setUp() throws Exception {
        convMainTemplate.update("TRUNCATE segments");
        convMainTemplate.update("TRUNCATE " + SegmentsExpressionHistoryDao.SEGMENTS_EXPRESSION_HISTORY_TABLE);
        convMainTemplate.update("TRUNCATE segments_update_queue");
    }

    @Test
    public void simpleCreate() {
        var segment = segmentsService.createSegment(FAKE_USER, buildSimpleSegment(), counterId);
        assertThat(segment.getSegmentId(), notNullValue());
        assertThat(segment.getCounterId(), equalTo(counterId));
        assertThat(segment.getExpression(), equalTo(segmentExpression));
        assertThat(segment.getName(), equalTo(segmentName));
        assertThat(segment.getExpressionVersion(), equalTo(1));
    }

    @Test
    public void multipleUpdates() {
        var expressionVer1 = segmentExpression;
        var expressionVer2 = "ym:s:regionCountry == 42";
        var expressionVer3 = "ym:s:regionCountry == 100500";

        var segment = segmentsService.createSegment(FAKE_USER, buildSimpleSegment(), counterId);
        markSegmentAsRetargeting(segment.getSegmentId());
        segment.setName("new simple name");

        // first update
        segment = segmentsService.updateSegment(FAKE_USER, segment.getSegmentId(), segment.getCounterId(), segment);
        assertThat(segment.getName(), equalTo("new simple name"));
        assertThat(segment.getExpression(), equalTo(segmentExpression));
        assertThat(segment.getExpressionVersion(), equalTo(1));
        assertUpdateQueueEmpty();

        segment.setExpression(expressionVer2);
        segment = segmentsService.updateSegment(FAKE_USER, segment.getSegmentId(), segment.getCounterId(), segment);
        assertThat(segment.getName(), equalTo("new simple name"));
        assertThat(segment.getExpression(), equalTo(expressionVer2));
        assertThat(segment.getExpressionVersion(), equalTo(2));
        assertUpdateQueueContains(Map.of(segment.getSegmentId(), SegmentUpdateReason.update));

        var expressionVer1FromDB = segmentsExpressionHistoryDao.getExpression(segment.getSegmentId(), 1);
        assertThat(expressionVer1FromDB, equalTo(Optional.of(expressionVer1)));

        segment.setExpression(expressionVer3);
        segment = segmentsService.updateSegment(FAKE_USER, segment.getSegmentId(), segment.getCounterId(), segment);
        assertThat(segment.getName(), equalTo("new simple name"));
        assertThat(segment.getExpression(), equalTo(expressionVer3));
        assertThat(segment.getExpressionVersion(), equalTo(3));
        assertUpdateQueueContains(Map.of(segment.getSegmentId(), SegmentUpdateReason.update));

        var expressionVer2FromDb = segmentsExpressionHistoryDao.getExpression(segment.getSegmentId(), 2);
        assertThat(expressionVer2FromDb, equalTo(Optional.of(expressionVer2)));
    }

    private void markSegmentAsRetargeting(int segmentId) {
        var i = convMainTemplate.update("update segments set direct_retargeting = 1 where segment_id = ?", segmentId);
        assertThat(i, equalTo(1));
    }

    private void assertUpdateQueueEmpty() {
        var count = convMainTemplate.queryForObject("select count(*) from segments_update_queue", RowMappers.INTEGER);
        assertThat(count, equalTo(0));
    }

    private void assertUpdateQueueContains(Map<Integer, SegmentUpdateReason> data) {
        var fromDb = new HashMap<Integer, SegmentUpdateReason>();
        convMainTemplate.query("select segment_id, reason from segments_update_queue", rs -> {
            fromDb.put(rs.getInt("segment_id"), SegmentUpdateReason.valueOf(rs.getString("reason")));
        });
        convMainTemplate.update("truncate segments_update_queue");
        assertThat(fromDb, equalTo(data));
    }

    @Nonnull
    static Segment buildSimpleSegment() {
        var simpleSegment = new Segment(null, null, segmentName, segmentExpression);
        simpleSegment.setSegmentSource(SegmentSource.API);
        return simpleSegment;
    }

    @Configuration
    @Import({JdbcTemplateConfig.class, SegmentsExpressionHistoryDaoTest.Config.class, SegmentDaoTest.Config.class})
    static class Config {

        @Bean
        public ApiUtils apiUtils() throws Exception {
            return new SimpleTestSetup().getApiUtils();
        }

        @Bean
        public SegmentParseService segmentParseService() throws Exception {
            return SegmentParseServiceStreamabilityClassificationTest.buildSegmentParseService(apiUtils());
        }

        @Bean
        public CounterLimitsService counterLimitsService(@Qualifier("convMainTemplate") MySqlJdbcTemplate template) {
            return new CounterOptionsService(new CounterOptionsDao(template));
        }

        @Bean
        public SegmentsService segmentsService(
                @Qualifier("convMainTemplate") MySqlJdbcTemplate template,
                SegmentParseService segmentParseService,
                SegmentsDao segmentsDao,
                SegmentsExpressionHistoryDao segmentsExpressionHistoryDao,
                CounterLimitsService counterLimitsService
        ) {
            template.update(
                    "create table if not exists segments_update_queue\n" +
                    "(\n" +
                    "    id         bigint unsigned auto_increment\n" +
                    "        primary key,\n" +
                    "    segment_id int unsigned                                                  not null,\n" +
                    "    add_time   timestamp default CURRENT_TIMESTAMP                           not null,\n" +
                    "    reason     enum ('create', 'update', 'delete', 'recount', 'move_to_big') null\n" +
                    ");"
            );
            var segmentsService = new SegmentsService();

            segmentsService.setConvMain(template);
            segmentsService.setRetargetingDb(template);
            segmentsService.setSegmentsDao(segmentsDao);
            segmentsService.setSegmentsExpressionHistoryDao(segmentsExpressionHistoryDao);
            segmentsService.setLimitsService(counterLimitsService);
            segmentsService.setSegmentParseService(segmentParseService);

            return segmentsService;
        }
    }

}
