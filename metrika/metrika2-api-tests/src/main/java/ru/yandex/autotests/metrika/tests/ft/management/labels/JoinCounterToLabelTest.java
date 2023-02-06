package ru.yandex.autotests.metrika.tests.ft.management.labels;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.metrika.api.management.client.label.Label;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static ch.lambdaj.collection.LambdaCollections.with;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasItem;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by proxeter on 29.07.2014.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.LABELS)
@Title("Проверка привязки счетчика к метке")
public class JoinCounterToLabelTest {

    /**
     * Шаги
     */
    private UserSteps user;

    private Long labelId;
    private Long counterId;

    private Label label;
    private CounterFull counter;

    private Label addedLabel;
    private CounterFull addedCounter;

    @Before
    public void before() {
        user = new UserSteps();
        counter = ManagementTestData.getDefaultCounter();
        user.onManagementSteps().onCountersSteps().deleteAllCountersWithName(counter.getName());
        label = ManagementTestData.getDefaultLabel();
        addedCounter = user.onManagementSteps().onCountersSteps().addCounterAndExpectSuccess(counter);
        addedLabel = user.onManagementSteps().onLabelsSteps().addLabelAndExpectSuccess(label);

        counterId = addedCounter.getId();
        labelId = addedLabel.getId();
    }

    @Test
    @Title("Метка: привязка счетчика к метке")
    public void joinCounterToLabelTest() {

        user.onManagementSteps().onLabelsSteps().joinCounterToLabelAndExpectSuccess(counterId, labelId);

        List<CounterFull> countersByLabel = user.onManagementSteps().onLabelsSteps()
                .getCountersByLabelAndExpectSuccess(labelId);

        assertThat("Привязанный счетчик присутствует в списке счетчиков метки", countersByLabel,
                hasItem(having(on(CounterFull.class).getId(), equalTo(counterId))));
    }

    @After
    public void after() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);
        user.onManagementSteps().onLabelsSteps().deleteLabelAndExpectSuccess(labelId);
    }
}
