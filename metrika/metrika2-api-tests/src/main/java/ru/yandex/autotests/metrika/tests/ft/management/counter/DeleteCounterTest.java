package ru.yandex.autotests.metrika.tests.ft.management.counter;

import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.parameters.management.v1.AvailableCountersParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData;
import ru.yandex.metrika.api.management.client.external.CounterBrief;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static ch.lambdaj.Lambda.on;
import static ch.lambdaj.collection.LambdaCollections.with;
import static org.hamcrest.Matchers.hasItem;
import static org.hamcrest.Matchers.not;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;


/**
 * Created by proxeter on 24.07.2014.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.COUNTERS)
@Title("Проверка удаления счетчика")
public class DeleteCounterTest {
    private UserSteps user;
    private Long counterId;
    private CounterFull counter;
    private CounterFull addedCounter;

    @Before
    public void before() {
        user = new UserSteps();
        counter = ManagementTestData.getDefaultCounter();
        user.onManagementSteps().onCountersSteps().deleteAllCountersWithName(counter.getName());

        addedCounter = user.onManagementSteps().onCountersSteps().addCounterAndExpectSuccess(counter);
        counterId = addedCounter.getId();
    }

    @Test
    @Title("Счетчик: 200 статус после удаления счетчика")
    public void deleteCounterTest() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);
    }

    @Test
    @Title("Счетчик: добавленный счетчик отсутствует в списке доступных счетчиков после удаления")
    public void deletedCounterAvailableTest() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);

        List<CounterBrief> availableCounters =
                user.onManagementSteps().onCountersSteps()
                        .getAvailableCountersAndExpectSuccess(new AvailableCountersParameters());

        List<Long> counterIds = with(availableCounters).extract(on(CounterBrief.class).getId());

        assertThat("Добавленный счетчик присутствует в списке доступных счетчиков", counterIds,
                not(hasItem(counterId)));
    }

}
