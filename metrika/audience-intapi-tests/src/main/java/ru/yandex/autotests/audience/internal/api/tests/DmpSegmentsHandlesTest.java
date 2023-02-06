package ru.yandex.autotests.audience.internal.api.tests;

import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.audience.dmp.DmpExternalSegment;
import ru.yandex.audience.intapi.direct.UsersGoalsServiceInnerDmpCondition;
import ru.yandex.autotests.audience.internal.api.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;
import java.util.Map;

import static org.hamcrest.Matchers.greaterThan;
import static org.hamcrest.Matchers.iterableWithSize;
import static ru.yandex.autotests.audience.internal.api.IntapiFeatures.DMP;
import static ru.yandex.autotests.audience.internal.api.parameters.UidParameters.uid;
import static ru.yandex.autotests.audience.internal.api.tests.IntapiTestData.ACCOUNT_UID;
import static ru.yandex.autotests.audience.internal.api.tests.IntapiTestData.CONDITION;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.commons.beans.BeanDifferMatchers.hasBeanEquivalent;

/**
 * Created by apuzikov on 12.07.17.
 */
@Features(DMP)
@Title("Проверка ручек intapi для dmp сегментов")
public class DmpSegmentsHandlesTest {
    private final static UserSteps user = new UserSteps();
    private static List<DmpExternalSegment> dmpSegments;
    private static Map<Long, ? extends List<UsersGoalsServiceInnerDmpCondition>> conditions;

    @BeforeClass
    public static void init(){
        dmpSegments = user.onDisplaySteps().getDmpSegments();
        conditions = user.onDisplaySteps().getConditionsByUid(uid(ACCOUNT_UID));
    }

    @Test
    @Title("Проверка ручки dmp_segments на возврат не пустого результата")
    public void testHandleDmpSegmentsFake() {
        assertThat("список сегментов не пуст", dmpSegments, iterableWithSize(greaterThan(0)));
    }

    @Test
    @Title("Проверка ручки dmp_conditions_by_uids на возврат не пустого результата")
    public void testHandleGetConditionsByUidFake() {
        assertThat("список сегментов не пуст", conditions.size(), greaterThan(0));
    }

    @Test
    @Title("Проверка одного элемента из ответа ручки dmp_conditions_by_uids")
    public void checkDmpSegmentForUser() {
        List<UsersGoalsServiceInnerDmpCondition> segments = conditions.get(ACCOUNT_UID);

        assertThat("в списке присутствует сегмент", segments,
                hasBeanEquivalent(UsersGoalsServiceInnerDmpCondition.class, CONDITION));
    }
}
