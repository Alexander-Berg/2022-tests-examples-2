package ru.yandex.autotests.metrika.tests.ft.management.goals;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.goals.GoalCondition;
import ru.yandex.metrika.api.management.client.external.goals.GoalConditionType;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Arrays;
import java.util.Collections;

import static ru.yandex.autotests.metrika.errors.ManagementError.*;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getFileGoal;

@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.GOALS)
@Title("Цель по скачиванию файлов")
public class FileGoalTest {
    private UserSteps user;
    private Long counterId;

    @Before
    public void init() {
        user = new UserSteps();
        counterId = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter()).getId();
    }

    @Test
    public void createFileGoal() {
        user.onManagementSteps().onGoalsSteps().addGoal(
                counterId,
                getFileGoal().withConditions(
                        Arrays.asList(
                                getGoalCondition(GoalConditionType.FILE, "file.png")
                        )
                )
        );
    }

    @Test
    public void createFileGoalWithConditionTypeAllFiles() {
        user.onManagementSteps().onGoalsSteps().addGoal(
                counterId,
                getFileGoal().withConditions(
                        Arrays.asList(
                                getGoalCondition(GoalConditionType.ALL_FILES, "")
                        )
                )
        );
    }

    @Test
    public void tryToCreateFileGoalWithNoGoalCondition() {
        user.onManagementSteps().onGoalsSteps().addGoalAndExpectError(
                INVALID_FILE_GOAL_WITH_NO_CONDITIONS,
                counterId,
                getFileGoal().withConditions(
                        Collections.emptyList()
                )
        );
    }

    @Test
    public void tryToCreateFileGoalWithManyGoalConditions() {
        user.onManagementSteps().onGoalsSteps().addGoalAndExpectError(
                INVALID_FILE_GOAL_CONDITIONS,
                counterId,
                getFileGoal().withConditions(
                        Arrays.asList(
                                getGoalCondition(GoalConditionType.FILE, "file.png"),
                                getGoalCondition(GoalConditionType.FILE, "file2.png")
                        )
                )
        );
    }

    @Test
    public void tryToCreateFileGoalWithConditionTypeAllFilesAndWithNotEmptyConditionUrl() {
        user.onManagementSteps().onGoalsSteps().addGoalAndExpectError(
                INVALID_FILE_GOAL_WITH_CONDITION_TYPE_ALL_FILES_AND_WITH_NOT_EMPTY_CONDITION_URL,
                counterId,
                getFileGoal().withConditions(
                        Arrays.asList(
                                getGoalCondition(GoalConditionType.ALL_FILES, "file")
                        )
                )
        );
    }

    private GoalCondition getGoalCondition(GoalConditionType type, String url) {
        return new GoalCondition().withType(type).withUrl(url);
    }

    @After
    public void cleanup() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndIgnoreStatus(counterId);
    }
}
