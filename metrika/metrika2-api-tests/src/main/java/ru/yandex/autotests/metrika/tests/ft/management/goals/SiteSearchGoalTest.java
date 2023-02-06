package ru.yandex.autotests.metrika.tests.ft.management.goals;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.goals.GoalCondition;
import ru.yandex.metrika.api.management.client.external.goals.GoalConditionType;
import ru.yandex.metrika.api.management.client.external.goals.SiteSearchGoal;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Arrays;
import java.util.Collections;

import static java.util.Collections.singletonList;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.metrika.errors.ManagementError.*;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getSiteSearchGoal;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.GOALS)
@Title("Цель поиск по сайту")
public class SiteSearchGoalTest {
    private UserSteps user;
    private Long counterId;

    @Before
    public void init() {
        user = new UserSteps();
        counterId = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter()).getId();
    }

    @Test
    public void createSiteSearchGoal() {
        user.onManagementSteps().onGoalsSteps().addGoal(
                counterId,
                getSiteSearchGoal().withConditions(
                        Arrays.asList(
                                getGoalCondition(GoalConditionType.SEARCH, "search,query,text")
                        )
                )
        );
    }

    @Test
    public void createSiteSearchGoalWithConditionUrlThatHasExtraSpaces() {
        SiteSearchGoal goal = (SiteSearchGoal) user.onManagementSteps().onGoalsSteps().addGoal(
                counterId,
                getSiteSearchGoal().withConditions(
                        Arrays.asList(
                                getGoalCondition(GoalConditionType.SEARCH, "   search  ,   query,   text   ")
                        )
                )
        );

        assertThat("создалась правильная условия цели где удалили лишние пробелы", goal.getConditions(), equalTo(
                singletonList(new GoalCondition().withType(GoalConditionType.SEARCH).withUrl("search,query,text")))
        );
    }

    @Test
    public void tryToCreateSiteSearchGoalWithMultipleGoalConditions() {
        user.onManagementSteps().onGoalsSteps().addGoalAndExpectError(
                SITE_SEARCH_GOAL_SHOULD_HAS_EXACTLY_ONE_GOAL_CONDITION,
                counterId,
                getSiteSearchGoal().withConditions(
                        Arrays.asList(
                                getGoalCondition(GoalConditionType.SEARCH, "search,query,text"),
                                getGoalCondition(GoalConditionType.EXACT, "blablabla")
                        )
                )
        );
    }

    @Test
    public void tryToCreateSiteSearchGoalWithoutGoalCondition() {
        user.onManagementSteps().onGoalsSteps().addGoalAndExpectError(
                INVALID_SITE_SEARCH_GOAL_WITH_NO_CONDITIONS,
                counterId,
                getSiteSearchGoal().withConditions(Collections.emptyList())
        );
    }

    @Test
    public void tryToCreateSiteSearchGoalWithWrongGoalConditionType() {
        user.onManagementSteps().onGoalsSteps().addGoalAndExpectError(
                NOT_VALID_GOAL_CONDITION,
                counterId,
                getSiteSearchGoal().withConditions(
                        Arrays.asList(
                                getGoalCondition(GoalConditionType.EXACT, "blablabla")
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
