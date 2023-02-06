package ru.yandex.autotests.audience.internal.api.tests;

import com.google.common.collect.ImmutableList;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.audience.intapi.direct.UsersGoalsServiceInnerRetargetingCondition;
import ru.yandex.autotests.audience.internal.api.data.GoalSubtype;
import ru.yandex.autotests.audience.internal.api.steps.UserSteps;
import ru.yandex.autotests.irt.testutils.beandiffer2.beanfield.BeanFieldPath;
import ru.yandex.autotests.metrika.commons.clients.http.FreeFormParameters;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.*;
import java.util.stream.Collectors;

import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.autotests.audience.internal.api.IntapiFeatures.DIRECT;
import static ru.yandex.autotests.audience.internal.api.parameters.UidParameters.uid;
import static ru.yandex.autotests.audience.internal.api.tests.IntapiTestData.*;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.commons.beans.BeanDifferMatchers.hasBeanEquivalent;

/**
 * Created by ava1on on 07.08.17.
 */
@Features({DIRECT})
@Title("Проверка условий ретаргетинга из ручки")
@RunWith(Parameterized.class)
public class RetargetingConditionsTest {
    private static final UserSteps user = new UserSteps();
    private static final String[] FIELDS_TO_EXCLUDE = {"name", "sectionId", "sectionName", "percent", "goalTrait", "ownerStr", "counterName"};

    private static Map<Long, List<UsersGoalsServiceInnerRetargetingCondition>> conditions;

    @Parameterized.Parameter
    public Long owner;

    @Parameterized.Parameter(1)
    public String description;

    @Parameterized.Parameter(2)
    public UsersGoalsServiceInnerRetargetingCondition expectedCondition;

    @Parameterized.Parameters(name = "{1}")
    public static Collection<Object[]> createParameters() {

        return ImmutableList.<Object[]>builder()
                .addAll(Arrays.stream(GoalSubtype.values())
                        .map(k -> toArray(ACCOUNT_UID, "сегмент Аудитории: " + k.toString(), getAudienceCondition(k)))
                        .collect(Collectors.toList()))
                .add(toArray(COUNTER_OWNER, "цель Метрики", getMetrikaGoal()))
                .add(toArray(COUNTER_OWNER, "сегмент Метрики", getMetrikaSegment()))
                .add(toArray(EXPERIMENT_OWNER, "экспериментальный сегмент", getExperimentSegment()))
                .add(toArray(GUEST_UID, "гостевой сегмент", getGuestAudienceSegment()))
                .add(toArray(ECOMMERCE_COUNTER_OWNER, "цель ecommerce", getEcommerceGoal()))
                .add(toArray(ACCOUNT_WITH_CDP, "сегмент cdp", getCdpSegment()))
                .build();
    }

    @BeforeClass
    public static void init() {
        conditions = new HashMap<>();
        mergeConditions(conditions, user.onDirectSteps().getRetargentingConditionsByUid(uid(EXPERIMENT_OWNER)));
        mergeConditions(conditions, user.onDirectSteps().getRetargentingConditionsByUid(
                FreeFormParameters.makeParameters("include_few_data_segments", "true").append(uid(ACCOUNT_UID))));
        mergeConditions(conditions, user.onDirectSteps().getRetargentingConditionsByUid(uid(ECOMMERCE_COUNTER_OWNER)));
        mergeConditions(conditions, user.onDirectSteps().getRetargentingConditionsByUid(uid(ACCOUNT_WITH_CDP)));
    }

    private static void mergeConditions(Map<Long, List<UsersGoalsServiceInnerRetargetingCondition>> allConditions,
                                        Map<Long, List<UsersGoalsServiceInnerRetargetingCondition>> input) {
        input.forEach((k, v) -> allConditions.computeIfAbsent(k, key -> new ArrayList<>()).addAll(v));
    }

    @Test
    public void checkRetargetingCondition() {
        assertThat("сегмент присутствует в списке целей", conditions.get(owner),
                hasBeanEquivalent(UsersGoalsServiceInnerRetargetingCondition.class, expectedCondition,
                        Arrays.stream(FIELDS_TO_EXCLUDE).map(BeanFieldPath::newPath).toArray(BeanFieldPath[]::new)));
    }

}
