package ru.yandex.metrika.api.management.tests.medium.client.segments;

import org.junit.Assert;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringRunner;

import ru.yandex.metrika.api.management.client.segments.SegmentRetargeting;
import ru.yandex.metrika.api.management.client.segments.SegmentsDao;
import ru.yandex.metrika.api.management.client.segments.streamabillity.StreamabilityClass;
import ru.yandex.metrika.api.management.config.JdbcTemplateConfig;
import ru.yandex.metrika.dbclients.MySqlTestSetup;
import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;

import static ru.yandex.metrika.CommonTestsHelper.FAKE_USER;
import static ru.yandex.metrika.CommonTestsHelper.counterId;

@RunWith(SpringRunner.class)
@ContextConfiguration
public class SegmentDaoTest {

    @BeforeClass
    public static void beforeClass() throws Exception {
        MySqlTestSetup.globalSetup();
    }

    @Autowired
    public SegmentsDao segmentsDao;

    @Test
    public void save() {
        var segment = SegmentServiceTest.buildSimpleSegment();
        segment.setSegmentRetargeting(SegmentRetargeting.ALLOW);
        segment.setStreamabilityClass(StreamabilityClass.NOT_STREAMABLE);
        int segmentId = segmentsDao.createSegment(FAKE_USER, segment, counterId);

        segment.setSegmentId(segmentId);
        segment.setCounterId(counterId);

        var fromDb = segmentsDao.getSegment(segmentId);

        Assert.assertEquals(segment, fromDb);
    }

    @Configuration
    @Import(JdbcTemplateConfig.class)
    static class Config {
        @Bean
        public SegmentsDao segmentsDao(MySqlJdbcTemplate convMainTemplate) {
            return new SegmentsDao(convMainTemplate);
        }
    }
}
