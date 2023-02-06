package ru.yandex.autotests.metrika.tests.ft.management.counter;

import java.util.List;

import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.errors.ManagementError;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.counter.CounterFlags;
import ru.yandex.metrika.api.management.client.counter.CounterFlagsInnerIncognito;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static com.google.common.collect.Lists.newArrayList;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectError;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;

@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.COUNTERS)
@Title("Проверка изменения флагов счетчика")
public class CounterFlagsEditTest {
    private UserSteps user = new UserSteps();
    private CounterFull counter;

    @Before
    public void setup() {
        counter = user.onManagementSteps().onCountersSteps().addCounterAndExpectSuccess(getDefaultCounter());
    }

    @Test
    public void testUsual() {
        List<CounterFlags> flags = user.onManagementSteps().onCountersSteps().getCounterFlagsAndExpectSuccess(newArrayList(counter.getId()));
        Assert.assertEquals(1, flags.size());
        CounterFlags counterFlags = flags.get(0);
        counterFlags.setCollectFirstPartyData(true);
        counterFlags.setUseInBenchmarks(true);

        flags = user.onManagementSteps().onCountersSteps().editCounterFlagsAndExpectSuccess(newArrayList(counterFlags));

        Assert.assertEquals(1, flags.size());

        Assert.assertTrue(flags.get(0).getCollectFirstPartyData());
        Assert.assertTrue(flags.get(0).getUseInBenchmarks());
        user.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counter.getId());
    }

    @Test
    public void testDeleted() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counter.getId());
        CounterFlags counterFlags = new CounterFlags();
        counterFlags.setCounterId(counter.getId());
        counterFlags.setIncognito(CounterFlagsInnerIncognito.DISABLED);
        user.onManagementSteps().onCountersSteps().editCounterFlagsAndExpectError(newArrayList(counterFlags),
                expectError(ManagementError.NOT_FOUND));
    }
}
