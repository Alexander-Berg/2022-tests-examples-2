package ru.yandex.autotests.metrika.tests.ft.management.counter;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static org.hamcrest.Matchers.hasItem;
import static org.hamcrest.Matchers.not;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultLabel;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by vananos on 19.07.16.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.COUNTERS)
@Title("Удаленный счетчик не доступен при получении счетчиков, привязанных к метке")
public class DeletedCounterIsNotAvailableTest {

    private UserSteps user = new UserSteps();
    private List<CounterFull> counters;
    private CounterFull counter;
    private long counterId;
    private long labelId;

    @Before
    public void setup() {
        counter = getDefaultCounter();
        counterId = user.onManagementSteps().onCountersSteps().addCounterAndExpectSuccess(counter).getId();
        labelId = user.onManagementSteps().onLabelsSteps().addLabelAndExpectSuccess(getDefaultLabel()).getId();
        user.onManagementSteps().onLabelsSteps().joinCounterToLabelAndExpectSuccess(counterId, labelId);

        user.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);

        counters = user.onManagementSteps().onLabelsSteps().getCountersByLabelAndExpectSuccess(labelId);
    }

    @Test
    @Title("Счетчик не привязан к метке")
    public void deletedCounterShouldNotBeInCountersList() {
        assertThat("удаленный счетчик отсутствует в списке", counters, not(hasItem(beanEquivalent(counter))));
    }

    @After
    public void tearDown() {
        user.onManagementSteps().onLabelsSteps().deleteLabelAndExpectSuccess(labelId);
    }
}
