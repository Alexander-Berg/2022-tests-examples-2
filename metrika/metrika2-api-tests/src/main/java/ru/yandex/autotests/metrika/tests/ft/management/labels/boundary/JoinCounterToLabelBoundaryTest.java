package ru.yandex.autotests.metrika.tests.ft.management.labels.boundary;

import org.junit.After;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.errors.ManagementError;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static ch.lambdaj.Lambda.on;
import static ch.lambdaj.collection.LambdaCollections.with;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounters;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultLabel;

/**
 * Created by konkov on 03.12.2014.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.LABELS)
@Title("Проверка привязки счетчика к метке: граничный тест")
public class JoinCounterToLabelBoundaryTest {

    public final static int MAXIMUM_ALLOWED_COUNTERS = ManagementTestData.MAX_COUNTERS_ON_UID;

    private static UserSteps user;

    private List<Long> counterIds;
    private Long labelId;

    @BeforeClass
    public static void init() {
        user = new UserSteps();
    }

    @Before
    public void setup() {
        counterIds = with(user.onManagementSteps().onCountersSteps()
                .addCounters(getDefaultCounters(MAXIMUM_ALLOWED_COUNTERS + 1)))
                .extract(on(CounterFull.class).getId());

        labelId = user.onManagementSteps().onLabelsSteps().addLabelAndExpectSuccess(getDefaultLabel()).getId();

        user.onManagementSteps().onLabelsSteps()
                .joinCountersToLabel(counterIds.subList(0, MAXIMUM_ALLOWED_COUNTERS), labelId);
    }

    @Test
    @Title("Метка: привязка счетчика к метке с максимально допустимым количеством привязанных счетчиков")
    public void joinMoreThanMaximumAllowedCountersToLabelTest() {
        user.onManagementSteps().onLabelsSteps()
                .joinCounterToLabelAndExpectError(
                        ManagementError.COUNTER_LIMIT_FOR_LABEL_EXCEEDED,
                        counterIds.get(MAXIMUM_ALLOWED_COUNTERS), labelId);
    }

    @After
    public void teardown() {
        user.onManagementSteps().onLabelsSteps().deleteLabelAndExpectSuccess(labelId);
        user.onManagementSteps().onCountersSteps().deleteCounters(counterIds);
    }
}
