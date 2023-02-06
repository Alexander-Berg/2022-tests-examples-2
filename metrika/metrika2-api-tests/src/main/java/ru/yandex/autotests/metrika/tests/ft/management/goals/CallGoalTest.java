package ru.yandex.autotests.metrika.tests.ft.management.goals;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.irt.testutils.RandomUtils;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.management.v1.offlineconversion.CallsOfflineConversionUploadingData;
import ru.yandex.autotests.metrika.data.parameters.management.v1.OfflineConversionParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.goals.CallGoal;
import ru.yandex.metrika.api.management.client.external.goals.GoalE;
import ru.yandex.metrika.api.management.client.external.goals.GoalType;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Issue;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.data.management.v1.offlineconversion.OfflineConversionType.CALLS;
import static ru.yandex.autotests.metrika.errors.ManagementError.INVALID_GOAL_TYPE;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getCallGoal;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.offlineconversion.OfflineConversionUploadingTestData.createBaseData;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;
import static ru.yandex.metrika.api.management.client.external.offlineconversion.OfflineConversionUploadingClientIdType.CLIENT_ID;

/**
 * @author zgmnkv
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.GOALS)
@Title("Цель для звонков")
public class CallGoalTest {

    private static final List<CallsOfflineConversionUploadingData> DATA = createBaseData(CALLS, CLIENT_ID);

    private static final String GOAL_NAME = RandomUtils.getString(10);

    private UserSteps user;
    private Long counterId;
    private double defaultPrice = 199.99;

    @Before
    public void init() {
        user = new UserSteps();
        counterId = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter()).getId();
    }

    @Test
    public void checkCreateOnUpload() {
        GoalE callGoal = uploadAndGetGoal();
        assertThat("цель с типом звонок создалась", callGoal, beanEquivalent(new CallGoal()
                .withType(GoalType.CALL)));
    }

    @Test
    public void checkCreateOnUploadWithName() {
        GoalE callGoal = uploadAndGetGoal(GOAL_NAME);
        assertThat("цель с типом звонок создалась", callGoal, beanEquivalent(new CallGoal()
                .withType(GoalType.CALL)
                .withName(GOAL_NAME)));
    }

    @Test
    public void checkCreateManualDisabled() {
        user.onManagementSteps().onGoalsSteps()
                .addGoalAndExpectError(INVALID_GOAL_TYPE, counterId, getCallGoal());
    }

    @Test
    public void checkUpdate() {
        GoalE callGoal = uploadAndGetGoal();

        CallGoal changedGoal = getCallGoal();
        GoalE updatedGoal = user.onManagementSteps().onGoalsSteps()
                .editGoal(counterId, callGoal.getId(), changedGoal);

        assertThat("цель успешно изменена", updatedGoal, beanEquivalent(changedGoal));
    }

    @Test
    public void checkDelete() {
        GoalE callGoal = uploadAndGetGoal();
        user.onManagementSteps().onGoalsSteps()
                .deleteGoal(counterId, callGoal.getId());
    }

    @Test
    @Issue("METR-39010")
    public void checkChangeDefaultPrice() {
        GoalE callGoal = uploadAndGetGoal();
        GoalE result = user
                .onManagementSteps()
                .onGoalsSteps()
                .editGoal(
                        counterId,
                        callGoal.getId(),
                        callGoal.withDefaultPrice(this.defaultPrice)
                );
        assertThat(
                "цель с типом звонок изменила стоимость по умолчанию",
                result,
                beanEquivalent(
                    callGoal.withDefaultPrice(this.defaultPrice)
                )
        );

    }

    @Test
    @Issue("METR-39010")
    public void checkChangeName() {
        String newName = RandomUtils.getString(10);
        GoalE callGoal = uploadAndGetGoal();
        GoalE result = user
                .onManagementSteps()
                .onGoalsSteps()
                .editGoal(
                        counterId,
                        callGoal.getId(),
                        callGoal.withName(newName)
                );
        assertThat(
                "цель с типом звонок изменила имени",
                result,
                beanEquivalent(
                        callGoal.withName(newName)
                )
        );
    }

    @Test
    @Issue("METR-39010")
    public void checkFetchGoal() {
        GoalE callGoal = uploadAndGetGoal();
        user
            .onManagementSteps()
            .onGoalsSteps()
            .getGoal(counterId, callGoal.getId());
    }

    private GoalE uploadAndGetGoal() {
        return uploadAndGetGoal(null);
    }

    private GoalE uploadAndGetGoal(String newGoalName) {
        user.onManagementSteps().onOfflineConversionSteps()
                .upload(CALLS, counterId, DATA, new OfflineConversionParameters()
                                .withClientIdType(CLIENT_ID)
                                .withNewGoalName(newGoalName)
                                .withIgnoreCallsVisitJoinThreshold(1));

        return user.onManagementSteps().onGoalsSteps()
                .getGoals(counterId)
                .stream()
                .filter(goalE -> goalE.getType() == GoalType.CALL)
                .findAny()
                .orElse(null);
    }

    @After
    public void cleanup() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndIgnoreStatus(counterId);
    }
}
