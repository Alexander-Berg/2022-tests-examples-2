package ru.yandex.autotests.metrika.tests.ft.management.counter;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

import com.google.common.base.Joiner;
import org.apache.commons.lang3.RandomUtils;
import org.hamcrest.Matchers;
import org.junit.After;
import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.users.Users;
import ru.yandex.autotests.metrika.data.parameters.FreeFormParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.CounterBrief;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;

@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.COUNTERS)
@Title("Проверка получения списка доступных счетчиков по списку идентификаторов")
public class CounterListTest {
    private static final UserSteps user = new UserSteps().withUser(Users.SIMPLE_USER3);
    private static final int COUNTERS_TO_CREATE_NUM = 10;

    private static final List<Long> counterIds = new ArrayList<>();

    @Before
    public void setup() {
        for (int i = 0; i < COUNTERS_TO_CREATE_NUM; ++i) {
            counterIds.add(user.onManagementSteps().onCountersSteps().addCounterAndExpectSuccess(getDefaultCounter()).getId());
        }
        Collections.shuffle(counterIds);
    }

    @Test
    public void test() {
        List<Long> counterIdsToSelect = counterIds.subList(0, RandomUtils.nextInt(1, COUNTERS_TO_CREATE_NUM + 1));

        List<CounterBrief> result = user.onManagementSteps().onCountersSteps().getAvailableCountersAndExpectSuccess(
                FreeFormParameters.makeParameters().append("counter_ids", Joiner.on(',').join(counterIdsToSelect)));

        Assert.assertThat(
                result.stream().map(CounterBrief::getId).sorted().toList(),
                Matchers.is(counterIdsToSelect.stream().sorted().toList())
        );
    }


    @After
    public void cleanup() {
        user.onManagementSteps().onCountersSteps().deleteCounters(counterIds);
    }
}
