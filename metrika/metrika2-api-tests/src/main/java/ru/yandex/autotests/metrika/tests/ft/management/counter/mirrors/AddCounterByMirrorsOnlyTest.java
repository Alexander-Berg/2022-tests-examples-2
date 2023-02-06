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

import java.util.Arrays;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by proxeter on 30.07.2014.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.COUNTERS)
@Title("Проверка добавления счетчика без сайта, но с зеркалами")
public class AddCounterByMirrorsOnlyTest {
    private UserSteps user;

    private Long counterId;
    private CounterFull counter;
    private CounterFull addedCounter;

    @Before
    public void before() {
        user = new UserSteps();
        counter = new CounterFull()
                        .withName(ManagementTestData.getCounterName())
                        .withMirrors(Arrays.asList(ManagementTestData.getCounterSite(), ManagementTestData.getCounterSite()));
        user.onManagementSteps().onCountersSteps().deleteAllCountersWithName(counter.getName());

        addedCounter = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(counter, Field.MIRRORS);
        counterId = addedCounter.getId();
    }

    @Test
    @Title("Зеркала сайта: сайт счетчика должен заменен первым зеркалом")
    public void siteTest() {
        assertThat("Сайт счетчика совпадает с первым указанным зеркалом", addedCounter,
                having(on(CounterFull.class).getSite(),
                        not(nullValue())));
    }

    @Test
    @Title("Зеркала сайта: второе зеркало должно стать первым")
    public void mirrorTest() {
        String expectedMirror = counter.getMirrors().get(1);
        String resultMirror = addedCounter.getMirrors().get(0);

        assertThat("Второе зеркало должно стать первым", expectedMirror, equalTo(resultMirror));
    }

    @After
    public void after() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);
    }

}
