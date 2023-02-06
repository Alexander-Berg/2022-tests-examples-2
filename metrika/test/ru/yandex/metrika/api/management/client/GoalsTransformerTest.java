package ru.yandex.metrika.api.management.client;

import java.util.ArrayList;
import java.util.Date;
import java.util.List;

import org.junit.Test;

import ru.yandex.metrika.api.management.client.external.goals.ActionGoal;
import ru.yandex.metrika.api.management.client.external.goals.CallGoal;
import ru.yandex.metrika.api.management.client.external.goals.CdpOrderInProgressGoal;
import ru.yandex.metrika.api.management.client.external.goals.CdpOrderPaidGoal;
import ru.yandex.metrika.api.management.client.external.goals.CompositeGoal;
import ru.yandex.metrika.api.management.client.external.goals.ConditionalGoal;
import ru.yandex.metrika.api.management.client.external.goals.DepthGoal;
import ru.yandex.metrika.api.management.client.external.goals.GoalE;
import ru.yandex.metrika.api.management.client.external.goals.GoalMarketType;
import ru.yandex.metrika.api.management.client.external.goals.GoalSource;
import ru.yandex.metrika.api.management.client.model.DatabaseGoal;

import static java.lang.Math.abs;
import static org.hamcrest.Matchers.samePropertyValuesAs;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertNull;
import static org.junit.Assert.assertThat;
import static org.junit.Assert.assertTrue;
import static ru.yandex.metrika.api.management.client.external.goals.GoalStatus.Deleted;
import static ru.yandex.metrika.api.management.client.external.goals.GoalType.call;
import static ru.yandex.metrika.api.management.client.external.goals.GoalType.cdp_order_in_progress;
import static ru.yandex.metrika.api.management.client.external.goals.GoalType.cdp_order_paid;

public class GoalsTransformerTest {

    Date createTime = new Date(System.currentTimeMillis());
    Double defaultPrice = 13.5;
    double epsilon = 0.00000001;

    @Test
    public void fromGoalMethodTestWhenAttributeIsCallGoal() {
        var goal = new CallGoal(1, 1, "test name", createTime, defaultPrice, true, 1, GoalSource.auto, false, null);

        DatabaseGoal dbGoal = GoalsTransformer.fromGoal(goal);

        assertEquals(1, dbGoal.getGoalId());
        assertEquals(1, dbGoal.getCounterId());
        assertEquals("test name", dbGoal.getName());
        assertEquals(createTime, dbGoal.getCreateTime());
        assertTrue(abs(dbGoal.getDefaultPrice() - defaultPrice) < epsilon);
        assertTrue(dbGoal.isRetargeting());
        assertEquals(1, dbGoal.getSerial());
        assertEquals(GoalSource.auto, dbGoal.getGoalSource());
        assertFalse(dbGoal.isFavorite());
    }

    @Test
    public void fromGoalMethodTestWhenAttributeIsCdpOrderInProgressGoal() {
        CdpOrderInProgressGoal goal = new CdpOrderInProgressGoal(1, 1, "test name", createTime,
                defaultPrice, true, 1, GoalSource.auto, false, null);

        DatabaseGoal dbGoal = GoalsTransformer.fromGoal(goal);

        assertEquals(1, dbGoal.getGoalId(), 1);
        assertEquals(1, dbGoal.getCounterId(), 1);
        assertEquals("test name", dbGoal.getName());
        assertEquals(createTime, dbGoal.getCreateTime());
        assertTrue(abs(dbGoal.getDefaultPrice() - defaultPrice) < epsilon);
        assertTrue(dbGoal.isRetargeting());
        assertEquals(1, dbGoal.getSerial());
        assertEquals(GoalSource.auto, dbGoal.getGoalSource());
        assertFalse(dbGoal.isFavorite());
    }

    @Test
    public void fromGoalMethodTestWhenAttributeIsCdpOrderPaidGoal() {
        var goal = new CdpOrderPaidGoal(1, 1, "test name", createTime, defaultPrice, true, 1, GoalSource.auto, false, null);

        DatabaseGoal dbGoal = GoalsTransformer.fromGoal(goal);

        assertEquals(1, dbGoal.getGoalId());
        assertEquals(1, dbGoal.getCounterId());
        assertEquals("test name", dbGoal.getName());
        assertEquals(createTime, dbGoal.getCreateTime());
        assertTrue(abs(dbGoal.getDefaultPrice() - defaultPrice) < epsilon);
        assertTrue(dbGoal.isRetargeting());
        assertEquals(1, dbGoal.getSerial());
        assertEquals(GoalSource.auto, dbGoal.getGoalSource());
        assertFalse(dbGoal.isFavorite());
    }

    @Test
    public void getGoalMethodTestWhenDatabaseGoalTypeIsCall() {
        DatabaseGoal dbGoal = new DatabaseGoal(1, 1, 1, "test name", 1, call, Deleted, createTime, defaultPrice, "test flag", 1, 1, false, GoalSource.auto, false, false, 0);

        GoalE goal = GoalsTransformer.getGoal(dbGoal);

        assertEquals(1, goal.getId());
        assertEquals(1, goal.getCounterId());
        assertEquals(Integer.valueOf(1), goal.getSerial());
        assertEquals("test name", goal.getName());
        assertEquals(call, goal.getType());
        assertEquals(createTime, goal.getCreateTime());
        assertTrue(abs(goal.getDefaultPrice() - defaultPrice) < epsilon);
        assertEquals(false, goal.getIsRetargeting());
        assertEquals(GoalSource.auto, goal.getGoalSource());
        assertEquals(false, goal.getIsFavorite());
    }

    @Test
    public void getGoalMethodTestWhenDatabaseGoalTypeIsCdpOrderInProgress() {
        DatabaseGoal dbGoal = new DatabaseGoal(1, 1, 1, "test name", 1, cdp_order_in_progress, Deleted, createTime, defaultPrice, "test flag", 1, 1, false, GoalSource.auto, false, false, 0);

        GoalE goal = GoalsTransformer.getGoal(dbGoal);

        assertEquals(1, goal.getId());
        assertEquals(1, goal.getCounterId());
        assertEquals(Integer.valueOf(1), goal.getSerial());
        assertEquals("test name", goal.getName());
        assertEquals(cdp_order_in_progress, goal.getType());
        assertEquals(createTime, goal.getCreateTime());
        assertTrue(abs(goal.getDefaultPrice() - defaultPrice) < epsilon);
        assertEquals(false, goal.getIsRetargeting());
        assertEquals(GoalSource.auto, goal.getGoalSource());
        assertEquals(false, goal.getIsFavorite());
    }

    @Test
    public void getGoalMethodTestWhenDatabaseGoalTypeIsCdpOrderPaid() {
        DatabaseGoal dbGoal = new DatabaseGoal(1, 1, 1, "test name", 1, cdp_order_paid, Deleted, createTime, defaultPrice, "test flag", 1, 1, false, GoalSource.auto, false, false, 0);

        GoalE goal = GoalsTransformer.getGoal(dbGoal);

        assertEquals(1, goal.getId());
        assertEquals(1, goal.getCounterId());
        assertEquals(Integer.valueOf(1), goal.getSerial());
        assertEquals("test name", goal.getName());
        assertEquals(cdp_order_paid, goal.getType());
        assertEquals(createTime, goal.getCreateTime());
        assertTrue(abs(goal.getDefaultPrice() - defaultPrice) < epsilon);
        assertEquals(false, goal.getIsRetargeting());
        assertEquals(GoalSource.auto, goal.getGoalSource());
        assertEquals(false, goal.getIsFavorite());
    }

    @Test
    public void mergeWithExistingGoalMethodTest() {
        GoalE goal = new CallGoal();
        GoalE existingGoal = new CallGoal(1, 1, "test name", createTime,
                defaultPrice, true, 1,
                GoalSource.auto, false, null);

        assertEquals(0, goal.getId());
        assertEquals(call, goal.getType());
        assertEquals(0, goal.getCounterId());
        assertNull(goal.getName());
        assertNull(goal.getCreateTime());
        assertNull(goal.getDefaultPrice());
        assertNull(goal.getIsRetargeting());
        assertNull(goal.getSerial());

        GoalsTransformer.mergeWithExistingGoal(goal, existingGoal);

        assertEquals(existingGoal.getType(), goal.getType());
        assertEquals(existingGoal.getCounterId(), goal.getCounterId());
        assertEquals(existingGoal.getName(), goal.getName());
        assertEquals(existingGoal.getCreateTime(), goal.getCreateTime());
        assertTrue(abs(goal.getDefaultPrice() - existingGoal.getDefaultPrice()) < epsilon);
        assertEquals(existingGoal.getIsRetargeting(), goal.getIsRetargeting());
        assertEquals(existingGoal.getSerial(), goal.getSerial());
        assertEquals(GoalSource.auto, goal.getGoalSource());
        assertEquals(false, goal.getIsFavorite());
    }

    @Test
    public void mergeWithExistingConditionalGoalMethodTest() {
        ActionGoal goal = new ActionGoal();
        ActionGoal existingGoal = new ActionGoal(
                1,
                1,
                "test name",
                createTime,
                defaultPrice,
                GoalMarketType.basket,
                new ArrayList<>(),
                true,
                1,
                1,
                GoalSource.user,
                false,
                0,
                null
        );

        assertNull(goal.getFlag());
        assertNull(goal.getConditions());

        GoalsTransformer.mergeWithExistingConditionalGoal(goal, existingGoal);

        assertEquals(existingGoal.getFlag(), goal.getFlag());
        assertEquals(existingGoal.getConditions(), goal.getConditions());
    }

    @Test
    public void mergeWithExistingDepthGoalMethodTest() {
        DepthGoal goal = new DepthGoal();

        DepthGoal existingGoal = new DepthGoal(1, 1, "test name", createTime, defaultPrice, 10, true, 1, GoalSource.auto, false, null);

        assertNull(goal.getDepth());

        GoalsTransformer.mergeWithExistingDepthGoal(goal, existingGoal);

        assertEquals(existingGoal.getDepth(), goal.getDepth());
    }

    @Test
    public void mergeWithExistingCompositeGoalMethodTest() {
        CompositeGoal goal = new CompositeGoal();

        CompositeGoal existingGoal = new CompositeGoal(1, 1, "test name", createTime, true, 1, GoalSource.auto, false, null);

        existingGoal.setSteps(new ArrayList<>());

        assertNull(goal.getSteps());

        GoalsTransformer.mergeWithExistingCompositeGoal(goal, existingGoal);

        List<ConditionalGoal> existingGoalSteps = existingGoal.getSteps();
        List<ConditionalGoal> goalSteps = goal.getSteps();

        assertEquals(existingGoalSteps.size(), goalSteps.size());

        for (int i = 0; i < existingGoalSteps.size(); ++i) {
            assertThat(goalSteps.get(i), samePropertyValuesAs(existingGoalSteps.get(i)));
        }
    }

    @Test
    public void mergeWithExistingCompositeGoalMethodTestWhenStepsIsNotNull() {
        CompositeGoal goal = new CompositeGoal();

        ActionGoal emptyActionGoal = new ActionGoal();
        emptyActionGoal.setId(1);

        goal.setSteps(
                List.of(emptyActionGoal)
        );

        CompositeGoal existingGoal = new CompositeGoal(1, 1, "test name", createTime, true, 1, GoalSource.user, false, null);

        ActionGoal actionGoal = new ActionGoal(
                1,
                1,
                "test name",
                createTime,
                defaultPrice,
                GoalMarketType.basket,
                new ArrayList<>(),
                true,
                1,
                0,
                GoalSource.user,
                false,
                0,
                null
        );
        existingGoal.setSteps(
                List.of(actionGoal)
        );

        GoalsTransformer.mergeWithExistingCompositeGoal(goal, existingGoal);

        List<ConditionalGoal> existingGoalSteps = existingGoal.getSteps();
        List<ConditionalGoal> goalSteps = goal.getSteps();

        assertEquals(existingGoalSteps.size(), goalSteps.size());

        for (int i = 0; i < existingGoalSteps.size(); ++i) {
            assertThat(goalSteps.get(i), samePropertyValuesAs(existingGoalSteps.get(i)));
        }
    }
}
