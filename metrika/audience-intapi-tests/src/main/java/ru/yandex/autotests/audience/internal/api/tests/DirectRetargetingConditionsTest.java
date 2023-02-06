package ru.yandex.autotests.audience.internal.api.tests;

import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import org.junit.Test;

import ru.yandex.audience.intapi.direct.UsersGoalsServiceInnerRetargetingCondition;
import ru.yandex.autotests.audience.internal.api.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.Matchers.is;
import static org.hamcrest.Matchers.not;
import static ru.yandex.autotests.audience.internal.api.IntapiFeatures.DIRECT;
import static ru.yandex.autotests.audience.internal.api.parameters.IdsParameters.ids;
import static ru.yandex.autotests.audience.internal.api.parameters.IncludeFewDataSegmentsParameters.includeFewDataSegments;
import static ru.yandex.autotests.audience.internal.api.parameters.UidParameters.uid;
import static ru.yandex.autotests.audience.internal.api.tests.IntapiTestData.ACCOUNT_UID;
import static ru.yandex.autotests.audience.internal.api.tests.IntapiTestData.getFewDataAudienceCondition;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.commons.beans.BeanDifferMatchers.hasBeanEquivalent;

@Features(DIRECT)
@Title("Проверка условий ретаргетинга из ручки, особые кейсы.")
public class DirectRetargetingConditionsTest {
    private static final UserSteps user = new UserSteps();

    @Test
    public void checkRetargetingConditionWhenFewDataSegmentsAreIncluded() {
        Map<Long, List<UsersGoalsServiceInnerRetargetingCondition>> conditionsWithFewDataSegments = user.onDirectSteps().getRetargentingConditionsByUid(uid(ACCOUNT_UID), includeFewDataSegments(true));
        assertThat("сегмент присутствует в списке целей",
                conditionsWithFewDataSegments.get(ACCOUNT_UID),
                hasBeanEquivalent(UsersGoalsServiceInnerRetargetingCondition.class, getFewDataAudienceCondition()));
    }

    @Test
    public void checkRetargetingConditionWhenOnlyFullyProcessedSegmentsAreAllowed() {
        Map<Long, List<UsersGoalsServiceInnerRetargetingCondition>> conditionsWithFullyProcessedSegments = user.onDirectSteps().getRetargentingConditionsByUid(uid(ACCOUNT_UID));
        assertThat("сегмент не присутствует в списке целей",
                conditionsWithFullyProcessedSegments.get(ACCOUNT_UID),
                not(hasBeanEquivalent(UsersGoalsServiceInnerRetargetingCondition.class, getFewDataAudienceCondition())));
    }

    @Test
    public void checkNoDuplicatesInResponse() {
        long uid = 1143290725L;
        Map<Long, List<UsersGoalsServiceInnerRetargetingCondition>> conditionsMap = user.onDirectSteps().getRetargentingConditionsByUid(uid(uid));
        List<UsersGoalsServiceInnerRetargetingCondition> conditions =
                conditionsMap.get(uid);
        assertThat("Нет дупликатов", conditions.stream().map(UsersGoalsServiceInnerRetargetingCondition::getId).collect(Collectors.toSet()).size(), is(conditions.size()));
    }


    @Test
    public void checkRetargetingConditionsByUid() {
        long uid = 83749751L;
        long goalId = 4047630815L;
        long segmentId = 1000000002L;
        long audienceId = 2000998208L;
        long ecommerceId = 3062915509L;
        long cdpSegment = 2600000290L;

        Map<String, List<Long>> conditionsMap = user.onDirectSteps().checkRetargetingConditionsByUid(uid(uid, 2), ids(goalId, segmentId, audienceId, ecommerceId, cdpSegment, 1));
        Map<String, List<Long>> expected = new HashMap<>();
        expected.put(""+44214498, Arrays.asList(goalId));
        expected.put(""+83749751, Arrays.asList(segmentId, ecommerceId));
        expected.put(""+495130696, Arrays.asList(audienceId));
        assertThat("Правильная проверка check", conditionsMap, is(expected));
    }
}
