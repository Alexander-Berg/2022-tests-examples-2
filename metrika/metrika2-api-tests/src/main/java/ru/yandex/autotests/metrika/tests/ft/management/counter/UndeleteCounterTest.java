package ru.yandex.autotests.metrika.tests.ft.management.counter;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData;
import ru.yandex.metrika.api.management.client.external.CounterBrief;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.metrika.api.management.client.external.MonitoringOptionsE;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static ch.lambdaj.collection.LambdaCollections.with;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by proxeter on 24.07.2014.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.COUNTERS)
@Title("Проверка восстановления счетчика")
public class UndeleteCounterTest {
    private UserSteps user;

    private Long counterId;
    private CounterFull counter;
    private CounterFull addedCounter;

    @Before
    public void before() {
        user = new UserSteps();
        counter = ManagementTestData.getDefaultCounter();
        user.onManagementSteps().onCountersSteps().deleteAllCountersWithName(counter.getName());

        counter.setMonitoring(new MonitoringOptionsE());
        addedCounter = user.onManagementSteps().onCountersSteps().addCounterAndExpectSuccess(counter);
        counterId = addedCounter.getId();
        user.onManagementSteps().onCountersSteps().setMonitoringEnabledFor(counterId, counter);
        user.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);
        user.onManagementSteps().onCountersSteps().undeleteCounter(counterId);
    }

    @Test
    @Title("Счетчик: восстановленный счетчик должен быть доступен")
    public void undeleteCounterTest() {
        List<CounterBrief> availableCounters =
                user.onManagementSteps().onCountersSteps().getAvailableCountersAndExpectSuccess();

        List<Long> availableCounterIds = with(availableCounters).extract(on(CounterBrief.class).getId());

        assertThat("Восстановленный счетчик присутствует в списке доступных счетчиков", availableCounterIds,
                hasItem(counterId));
    }

    @Test
    @Title("Счетчик: Имя счетчика должны совпадать с заданным после восстановления")
    public void counterNameTest() {
        CounterFull restoredCounter =
                user.onManagementSteps().onCountersSteps().getCounterInfo(counterId);

        assertThat("Имя и сайт счетчика должны совпадать с заданным", addedCounter,
                having(on(CounterFull.class).getName(), equalTo(restoredCounter.getName())));
    }

    @Test
    @Title("Счетчик: Сайт счетчика должны совпадать с заданным после восстановления")
    public void counterSiteTest() {
        CounterFull restoredCounter =
                user.onManagementSteps().onCountersSteps().getCounterInfo(counterId);

        assertThat("Имя и сайт счетчика должны совпадать с заданным", addedCounter,
                having(on(CounterFull.class).getSite(), equalTo(restoredCounter.getSite())));
    }

    @Test
    @Title("Счётчик: удалённый счётчик с мониторингом после восстановления теряет свой мониторинг")
    public void counterMonitoringTest() {
        CounterFull counterInfo = user.onManagementSteps().onCountersSteps().getCounterInfo(counterId);
        assertThat("Мониторинг после восстановления выключен", counterInfo.getMonitoring().getEnableMonitoring(), is(equalTo(0L)));
    }

    @After
    public void after() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);
    }

}
