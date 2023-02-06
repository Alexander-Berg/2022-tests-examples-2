package ru.yandex.audience.intapi.estimate;

import java.time.LocalDate;
import java.util.Collections;

import org.junit.Before;
import org.junit.Test;

import ru.yandex.audience.estimate.EstimateRequest;
import ru.yandex.audience.estimate.EstimateRequestParser;
import ru.yandex.audience.estimate.filter.AndNode;
import ru.yandex.audience.estimate.filter.AudienceNode;
import ru.yandex.audience.estimate.filter.CounterNode;
import ru.yandex.audience.estimate.filter.GoalNode;
import ru.yandex.audience.estimate.filter.NotNode;
import ru.yandex.audience.estimate.filter.OrNode;
import ru.yandex.audience.estimate.filter.SegmentNode;
import ru.yandex.audience.util.RetargetingId;
import ru.yandex.metrika.api.management.client.GoalsService;
import ru.yandex.metrika.api.management.client.segments.Segment;
import ru.yandex.metrika.api.management.client.segments.SegmentsDao;

import static org.junit.Assert.assertEquals;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.Matchers.anyList;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;


public class EstimateRequestParserTest {
    private final LocalDate today = LocalDate.now();
    private EstimateRequestParser target;

    @Before
    public void setUp() {
        target = new EstimateRequestParser();

        GoalsService goalsService = mock(GoalsService.class);
        when(goalsService.getCounterIdByGoalId(anyLong())).thenReturn(41);
        target.setGoalDao2(goalsService);

        SegmentsDao segmentsDao = mock(SegmentsDao.class);
        Segment segment = new Segment();
        segment.setCounterId(34);
        segment.setExpression("ym:s:gender=='male'");
        when(segmentsDao.getSegments(anyList())).thenReturn(Collections.singletonList(segment));
        target.setSegmentsDao(segmentsDao);
    }

    @Test
    public void testGoal() {
        EstimateRequest parse = target.parse("id==42 interval 1 days", today);
        assertEquals(parse.tree, new GoalNode(41, new RetargetingId(42), today, today));
    }

    @Test
    public void testCounter() {
        EstimateRequest parse = target.parse("id==4000000042 interval 1 days", today);
        assertEquals(parse.tree, new CounterNode(new RetargetingId(4000000042L), today, today));
    }

    @Test
    public void testDays() {
        EstimateRequest parse = target.parse("id==42 interval 90 days", today);
        assertEquals(parse.tree, new GoalNode(41, new RetargetingId(42), today.minusDays(89), today));
    }

    @Test
    public void testSegment() {

        EstimateRequest parse = target.parse("id==1000000042 interval 1 days", today);
        assertEquals(parse.tree, new SegmentNode(34, new RetargetingId(1000000042), "ym:s:gender=='male'", today, today));
    }

    @Test
    public void testAudience() {
        EstimateRequest parse = target.parse("id==2000000042 interval 3 days", today);
        assertEquals(parse.tree, new AudienceNode(new RetargetingId(2000000042)));
    }

    @Test
    public void testNot() {
        EstimateRequest parse = target.parse("not id==2000000042 interval 3 days", today);
        assertEquals(parse.tree, new NotNode(new AudienceNode(new RetargetingId(2000000042))));
    }

    @Test
    public void testAnd() {
        EstimateRequest parse = target.parse("id==2000000042 interval 3 days and id==4000000042 interval 3 days", today);
        assertEquals(parse.tree, new AndNode(new AudienceNode(new RetargetingId(2000000042)), new CounterNode(new RetargetingId(4000000042L), today.minusDays(2), today)));
    }

    @Test
    public void testOr() {
        EstimateRequest parse = target.parse("id==2000000042 interval 3 days or id==4000000042 interval 3 days", today);
        assertEquals(parse.tree, new OrNode(new AudienceNode(new RetargetingId(2000000042)), new CounterNode(new RetargetingId(4000000042L), today.minusDays(2), today)));
    }

    @Test
    public void testPriotiry() {
        EstimateRequest parse = target.parse("not id==2000000042 interval 3 days and id==2000000042 interval 2 days or id==4000000042 interval 4 days", today);
        assertEquals(parse.tree, new OrNode(
                new AndNode(
                        new NotNode(new AudienceNode(new RetargetingId(2000000042))),
                        new AudienceNode(new RetargetingId(2000000042L))),
                new CounterNode(new RetargetingId(4000000042L), today.minusDays(3), today)));
    }

}
