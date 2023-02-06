package ru.yandex.autotests.internalapid.tests.b2b;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import org.apache.commons.lang3.tuple.Triple;
import org.hamcrest.Matchers;
import org.joda.time.LocalDate;
import org.junit.Test;

import ru.yandex.autotests.internalapid.tests.InternalApidTest;
import ru.yandex.metrika.internalapid.direct.external.CounterGoalCount;
import ru.yandex.metrika.internalapid.direct.external.CounterGoalCountInnerGoalCount;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;

public class DirectB2bTest extends InternalApidTest {

    private static final double COMPARE_ACCURACY = 0.01;

    @Test
    @Title("Тест ручки /direct/get_goal_counts")
    public void testGetGoalCounts() {
        LocalDate today = LocalDate.now();
        int metricaCounterId = 24226447;
        List<CounterGoalCount> reaches =
                userSteps.onDirectSteps().getCounterGoalsReaches(Arrays.asList(metricaCounterId), today.minusDays(7), today.minusDays(2));
        List<CounterGoalCount> refReaches =
                userSteps.onDirectRefSteps().getCounterGoalsReaches(Arrays.asList(metricaCounterId), today.minusDays(7), today.minusDays(2));

        String comparison = compareResults(reaches, refReaches);
        assertThat("Результаты совпадают " + comparison, comparison.isEmpty(), Matchers.is(true));
    }

    private String compareResults(List<CounterGoalCount> reaches, List<CounterGoalCount> refReaches) {
        Map<Long, Long> reachesMap =
                reaches.get(0).getCounts().stream().collect(Collectors.toMap(CounterGoalCountInnerGoalCount::getGoalId,
                CounterGoalCountInnerGoalCount::getCount));
        Map<Long, Long> refReachesMap =
                reaches.get(0).getCounts().stream().collect(Collectors.toMap(CounterGoalCountInnerGoalCount::getGoalId,
                CounterGoalCountInnerGoalCount::getCount));
        List<Triple<Long, Long, Long>> goalIdToDifferentValues = new ArrayList<>();
        for (Map.Entry<Long, Long> reachEntry : reachesMap.entrySet()) {
            Long refReach = refReachesMap.getOrDefault(reachEntry.getKey(), 0L);
            if (Math.abs(refReach - reachEntry.getValue()) > reachEntry.getValue() * COMPARE_ACCURACY) goalIdToDifferentValues.add(Triple.of(reachEntry.getKey(), reachEntry.getValue(), refReach));
        }
        for (Map.Entry<Long, Long> refReachEntry : refReachesMap.entrySet()) {
            Long reach = reachesMap.getOrDefault(refReachEntry.getKey(), 0L);
            if (Math.abs(reach - refReachEntry.getValue()) > refReachEntry.getValue() * COMPARE_ACCURACY) goalIdToDifferentValues.add(Triple.of(refReachEntry.getKey(), reach, refReachEntry.getValue()));
        }
        return goalIdToDifferentValues.stream().map(t -> t.getLeft() + ":" + t.getMiddle() +"-" + t.getRight()).collect(Collectors.joining(","));
    }

}
