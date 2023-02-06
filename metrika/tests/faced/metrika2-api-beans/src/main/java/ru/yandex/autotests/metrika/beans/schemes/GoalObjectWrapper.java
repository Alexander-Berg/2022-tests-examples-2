package ru.yandex.autotests.metrika.beans.schemes;

import com.rits.cloning.Cloner;
import ru.yandex.metrika.api.management.client.external.goals.GoalE;

/**
 * Created by hamilkar on 10/13/16.
 */
public class GoalObjectWrapper {
    private final static Cloner CLONER = new Cloner();
    private final GoalE goal;

    public GoalObjectWrapper(GoalE goal) {
        this.goal = goal;
    }

    public GoalE getGoal() {
        return goal;
    }

    public String toString() {
        return goal == null ? "null"
                : goal.getName();
    }

    public GoalE getClone() {
        return CLONER.deepClone(goal);
    }
}
