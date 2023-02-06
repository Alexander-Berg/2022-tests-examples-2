package ru.yandex.audience.intapi.direct;

import java.util.Arrays;
import java.util.List;

import org.junit.Test;

import ru.yandex.audience.rbac.AudienceRbac;
import ru.yandex.audience.rbac.ExperimentsRbac;
import ru.yandex.audience.rbac.SegmentsRbac;
import ru.yandex.metrika.api.management.client.segments.SegmentParseService;
import ru.yandex.metrika.cdp.dao.SegmentsDao;
import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;
import ru.yandex.metrika.managers.GoalIdsDao;
import ru.yandex.metrika.rbac.metrika.CountersRbac;
import ru.yandex.metrika.rbac.metrika.MetrikaRbac;
import ru.yandex.metrika.util.concurrent.AbortPolicy;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.mock;

public class UsersGoalsServiceTest {

    @Test
    public void generatesPlaceholder() {
        UsersGoalsService usersGoalsService = new UsersGoalsService();
        assertThat(usersGoalsService.placeholderForItems(Arrays.asList("one", "two", "three")))
                .isEqualTo("?,?,?");
    }

    @Test(expected = AbortPolicy.AbortException.class)
    public void getAbortException() {
        UsersGoalsService goalsService = new UsersGoalsService();

        goalsService.setMaxQueueSize(2);
        goalsService.setMaxThreadCount(2);

        MySqlJdbcTemplate convMain = mock(MySqlJdbcTemplate.class);
        MySqlJdbcTemplate audienceMain = mock(MySqlJdbcTemplate.class);
        MetrikaRbac metrikaRbac = mock(MetrikaRbac.class);
        AudienceRbac audienceRbac = mock(AudienceRbac.class);
        CountersRbac countersRbac = mock(CountersRbac.class);
        SegmentsRbac segmentsRbac = mock(SegmentsRbac.class);
        ExperimentsRbac experimentsRbac = mock(ExperimentsRbac.class);
        SegmentParseService segmentParseService = mock(SegmentParseService.class);
        SegmentsDao cdpSegmentsDao = mock(SegmentsDao.class);
        GoalIdsDao goalIdsDao = mock(GoalIdsDao.class);
        goalsService.setConvMain(convMain);
        goalsService.setAudienceMain(audienceMain);
        goalsService.setMetrikaRbac(metrikaRbac);
        goalsService.setAudienceRbac(audienceRbac);
        goalsService.setCountersRbac(countersRbac);
        goalsService.setSegmentsRbac(segmentsRbac);
        goalsService.setExperimentsRbac(experimentsRbac);
        goalsService.setSegmentParseService(segmentParseService);
        goalsService.setCdpSegmentsDao(cdpSegmentsDao);
        goalsService.setGoalIdsDao(goalIdsDao);
        goalsService.afterPropertiesSet();

        goalsService.getRetargetingConditions(List.of(637757172L));
    }

}
