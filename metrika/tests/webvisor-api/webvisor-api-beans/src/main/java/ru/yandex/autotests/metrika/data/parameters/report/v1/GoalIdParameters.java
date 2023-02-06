package ru.yandex.autotests.metrika.data.parameters.report.v1;

import ru.yandex.autotests.httpclient.lite.core.AbstractFormParameters;
import ru.yandex.autotests.httpclient.lite.core.FormParameter;
import ru.yandex.autotests.metrika.data.common.counters.Counter;

import static ru.yandex.autotests.metrika.data.common.counters.Counter.GOAL_ID;

/**
 * Created by konkov on 28.08.2015.
 */
public class GoalIdParameters extends AbstractFormParameters {

    @FormParameter("goal_id")
    private String goalId;

    public String getGoalId() {
        return goalId;
    }

    public void setGoalId(String goalId) {
        this.goalId = goalId;
    }

    public GoalIdParameters withGoalId(final String goalId) {
        this.goalId = goalId;
        return this;
    }

    public static GoalIdParameters goalId(String goalId) {
        return new GoalIdParameters().withGoalId(goalId);
    }

    public static GoalIdParameters goalId(Long goalId) {
        return goalId(String.valueOf(goalId));
    }

    public static GoalIdParameters goalId(Counter counter) {
        return goalId(counter.get(GOAL_ID));
    }
}
