package ru.yandex.autotests.metrika.tests.ft.internal.abexperiments;

import java.util.Arrays;
import java.util.Collection;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.counters.Counters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.junit.Assert.assertEquals;
import static ru.yandex.autotests.metrika.data.common.users.Users.MANAGER;

@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.COUNTERS)
@Title("Тесты на произвольные условия для AB-тестов метрики")
@RunWith(Parameterized.class)
public class AbExperimentConditionsTest {

    public static final int COUNTER = (int) Counters.SENDFLOWERS_RU.getId();
    private UserSteps user = new UserSteps().withUser(MANAGER);

    @Parameterized.Parameter()
    public String condition;

    @Parameterized.Parameter(1)
    public Integer counterId;

    @Parameterized.Parameter(2)
    public Long puid;

    @Parameterized.Parameter(3)
    public String yuid;

    @Parameterized.Parameter(4)
    public Boolean expectedResult;

    @Parameterized.Parameters(name = "condition = {0}, counter_id = {1}, puid = {2}, yuid = {3}")
    public static Collection<Object[]> createParameters() {
        return Arrays.asList(new Object[][]{
                {"counterId == 101024", COUNTER, null, null, true},
                {"counterCreateDate() < '2020-01-01'", COUNTER, null, null, true},
                {"isFilterRobots()", COUNTER, null, null, null},
                {"publishersEnabled()", COUNTER, null, null, false},
                {"counterSource()==null", COUNTER, null, null, true},
                {"hasCounterFeature(\"ecommerce\")", COUNTER, null, null, true},
                {"hasCounterFeature(\"ecommerce\") OR isFilterRobots()", COUNTER, null, null, true},
                {"hasCounterFeature(\"ecommerce\") AND counterCreateDate() < '2020-01-01'", COUNTER, null, null, true},
                {"autogoalsEnabled()", COUNTER, null, null, null},
                {"hasCounterFlag(\"customflag42\")", COUNTER, null, null, null},
                {"hasPassportUidFlag(\"puidflag222\")", COUNTER, 222L, null, null},
                {"hasYandexUidFlag(\"someFlag\")", COUNTER, null, "AA23342434AA434234", null},
        });
    }

    @Test
    public void checkConditionTest() {
        Boolean result = user.onAbExperimentsSteps()
                .checkConditionAndExpectSuccess(condition, counterId, puid, yuid).getValue();
        if (expectedResult != null) {
            assertEquals(result, expectedResult);
        }
    }
}
