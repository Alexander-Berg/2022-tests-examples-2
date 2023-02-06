package ru.yandex.autotests.metrika.tests.ft.management.counter.createdate;

import org.junit.After;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.everyItem;
import static org.hamcrest.Matchers.notNullValue;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultLabel;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by konkov on 05.12.2014.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.COUNTERS)
@Title("Проверка наличия даты создания счетчика в списке счетчиков, привязанных к метке")
public class CreateDateCounterListByLabelTest {
    private static UserSteps user;
    private Long counterId;
    private List<CounterFull> actualCounters;
    private Long labelId;

    @BeforeClass
    public static void init() {
        user = new UserSteps();
    }

    @Before
    public void setup() {
        counterId = user.onManagementSteps().onCountersSteps().addCounterAndExpectSuccess(getDefaultCounter()).getId();

        labelId = user.onManagementSteps().onLabelsSteps().addLabelAndExpectSuccess(getDefaultLabel()).getId();

        user.onManagementSteps().onLabelsSteps().joinCounterToLabelAndExpectSuccess(counterId, labelId);

        actualCounters = user.onManagementSteps().onLabelsSteps().getCountersByLabelAndExpectSuccess(labelId);
    }

    @Test
    public void createDateInCounterShouldBePresentTest() {
        assertThat("дата создания счетчика заполнена", actualCounters,
                everyItem(having(on(CounterFull.class).getCreateTime(), notNullValue())));
    }

    @After
    public void teardown() {
        user.onManagementSteps().onLabelsSteps().deleteLabelAndExpectSuccess(labelId);
        user.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);
    }
}
