package ru.yandex.autotests.audience.internal.api.tests;

import java.util.Collection;
import java.util.List;

import org.hamcrest.Matchers;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.audience.intapi.direct.RetargetingConditionsWrapper;
import ru.yandex.audience.intapi.direct.UsersGoalsServiceInnerRetargetingConditionType;
import ru.yandex.autotests.audience.internal.api.steps.UserSteps;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.commons.clients.http.FreeFormParameters;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Title;

import static java.util.Arrays.asList;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.audience.intapi.direct.UsersGoalsServiceInnerRetargetingConditionType.AUDIENCE;
import static ru.yandex.audience.intapi.direct.UsersGoalsServiceInnerRetargetingConditionType.CDP_SEGMENT;
import static ru.yandex.audience.intapi.direct.UsersGoalsServiceInnerRetargetingConditionType.ECOMMERCE;
import static ru.yandex.audience.intapi.direct.UsersGoalsServiceInnerRetargetingConditionType.GOAL;
import static ru.yandex.audience.intapi.direct.UsersGoalsServiceInnerRetargetingConditionType.SEGMENT;
import static ru.yandex.autotests.audience.internal.api.IntapiFeatures.DIRECT;
import static ru.yandex.autotests.audience.internal.api.parameters.IdsParameters.ids;
import static ru.yandex.autotests.audience.internal.api.parameters.UidParameters.uid;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;

@Features(DIRECT)
@Title("Проверка условий ретаргетинга из ручки retargeting_conditions_by_uid2, особые кейсы.")
@RunWith(Parameterized.class)
public class DirectRetargetingConditionsByUid2Test {
    private static final UserSteps user = new UserSteps();

    @Parameterized.Parameter
    public UsersGoalsServiceInnerRetargetingConditionType type;
    @Parameterized.Parameter(1)
    public String prefix;
    @Parameterized.Parameter(2)
    public List<Long> ids;
    @Parameterized.Parameter(3)
    public boolean hasMoreElementsForLimitCheck;

    @Parameterized.Parameters(name = "Для типа {0}")
    public static Collection<Object[]> createParameters() {
        return asList(
                toArray(GOAL, "Вакансии", asList(4069052519L, 48305956L), true),
                toArray(SEGMENT, "Пришедшие", asList(1001404622L, 1001404652L), true),
                toArray(AUDIENCE, "regu", asList(2000998208L), false),
                toArray(ECOMMERCE, "Яндек", asList(3000115081L, 3000413990L), true),
                toArray(CDP_SEGMENT, "Сегмент", asList(2600000290L, 2600000269L), true)
        );
    }

    @Test
    public void limitCheck() {
        RetargetingConditionsWrapper conditions = getRetargetingConditionsByUid2(FreeFormParameters.makeParameters("limit", 1));
        assertThat("has more elements on limit check", conditions.getHasMoreConditions(),  Matchers.is(hasMoreElementsForLimitCheck));
    }

    @Test
    public void prefixCheck() {
        RetargetingConditionsWrapper conditions = getRetargetingConditionsByUid2(FreeFormParameters.makeParameters("prefix", prefix));
        assertThat("has elements on prefix check", conditions.getOwnerToConditions().isEmpty(),  Matchers.is(false));
    }

    @Test
    public void idsCheck() {
        RetargetingConditionsWrapper conditions = getRetargetingConditionsByUid2(ids(ids));
        assertThat("has elements on ids check", conditions.getOwnerToConditions().isEmpty(),  Matchers.is(false));
    }

    private RetargetingConditionsWrapper getRetargetingConditionsByUid2(IFormParameters parameters) {
        return user.onDirectSteps().getRetargentingConditionsByUid2(uid(83749751L), FreeFormParameters.makeParameters("type", type.value()), parameters);
    }
}
