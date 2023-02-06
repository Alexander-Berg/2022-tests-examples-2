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

import java.util.Collections;

import static java.util.Collections.emptyList;
import static org.hamcrest.Matchers.empty;
import static org.hamcrest.Matchers.is;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.COUNTERS)
@Title("Проверка редактирования счетчика с сайтом и с зеркалами")
public class CounterMirrorsManipulationTest {

    private UserSteps user;

    private Long counterId;
    private CounterFull counter;

    @Before
    public void before() {
        user = new UserSteps();
        String mirrorsSite = ManagementTestData.getCounterSite();
        counter = new CounterFull()
                .withName(ManagementTestData.getCounterName())
                .withSite(ManagementTestData.getCounterSite())
                .withMirrors(Collections.singletonList(mirrorsSite));
        user.onManagementSteps().onCountersSteps().deleteAllCountersWithName(counter.getName());

        counterId = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(counter, Field.MIRRORS).getId();
    }


    @Test
    @Title("Счётчик: последнее зеркало удаляется")
    public void testDeleteLastMirror() {
        counter.setMirrors2(emptyList());
        counter.setMirrors(null);
        CounterFull editedCounter = user.onManagementSteps().onCountersSteps().editCounter(counterId, counter);
        assertThat("После удаления последнего зеркала, список зеркал пуст", editedCounter.getMirrors2(), is(empty()));
    }

    @After
    public void after() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);
    }

}
