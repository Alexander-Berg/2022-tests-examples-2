package ru.yandex.autotests.metrika.tests.ft.management.counter.mirrors;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.parameters.management.v1.Field;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static ch.lambdaj.function.matcher.AndMatcher.and;
import static java.util.Arrays.asList;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by proxeter on 30.07.2014.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.COUNTERS)
@Title("Проверка добавления счетчика с сайтом и с зеркалами")
public class AddCounterByMirrorsWithSiteTest {
    private UserSteps user;

    private Long counterId;
    private CounterFull counter;
    private CounterFull addedCounter;

    @Before
    public void before() {
        user = new UserSteps();
        counter = new CounterFull()
                        .withName(ManagementTestData.getCounterName())
                        .withSite(ManagementTestData.getCounterSite())
                        .withMirrors(asList(
                                ManagementTestData.getCounterSite(),
                                ManagementTestData.getCounterSite()));
        user.onManagementSteps().onCountersSteps().deleteAllCountersWithName(counter.getName());

        addedCounter = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(counter, Field.MIRRORS);
        counterId = addedCounter.getId();
    }

    @Test
    @Title("Счетчик: Сайт не должен быть null и совпадать с заданным")
    public void siteTest() {
        assertThat("Сайт счетчика должен быть null", addedCounter, and(
                having(on(CounterFull.class).getSite(), not(nullValue())),
                having(on(CounterFull.class).getSite(), equalTo(counter.getSite()))
        ));
    }

    @Test
    @Title("Счетчик: Первое зеркало счетчика должны содержать указанные значения")
    public void firstMirrorTest() {
        assertThat("Первое зеркало сайта должно совпадать с заданным", addedCounter.getMirrors().get(0),
                equalTo(counter.getMirrors().get(0)));
    }

    @Test
    @Title("Счетчик: Второе зеркало счетчика должны содержать указанные значения")
    public void secondMirrorTest() {
        assertThat("Второе зеркало сайта должно совпадать с заданным", addedCounter.getMirrors().get(1),
                equalTo(counter.getMirrors().get(1)));
    }

    @After
    public void after() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);
    }

}
