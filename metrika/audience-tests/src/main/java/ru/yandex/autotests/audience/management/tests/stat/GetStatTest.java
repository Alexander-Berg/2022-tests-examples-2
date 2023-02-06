package ru.yandex.autotests.audience.management.tests.stat;

import com.google.common.collect.ImmutableList;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import ru.yandex.autotests.audience.beans.schemes.V1ManagementSegmentSegmentIdStatGETSchema;
import ru.yandex.autotests.audience.data.users.User;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.autotests.irt.testutils.beandiffer2.beanfield.BeanFieldPath;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.autotests.audience.data.users.User.GEO_SEGMENT_ID;
import static ru.yandex.autotests.audience.data.users.Users.*;
import static ru.yandex.autotests.metrika.commons.beans.BeanDifferMatchers.equivalentTo;
import static ru.yandex.autotests.audience.parameters.ULoginParameters.ulogin;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;

/**
 * Created by ava1on on 26.06.17.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({Requirements.Story.Management.GRANTS})
@Title("Роли: просмотр статистики сегмента разными ролями")
@RunWith(Parameterized.class)
public class GetStatTest {
    private final User owner = USER_DELEGATOR;

    @Parameter
    public String descripion;

    @Parameter(1)
    public User userParam;

    @Parameterized.Parameters(name = "пользователь {0}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.of(
                toArray("с правом на редактирование", USER_WITH_PERM_EDIT),
                toArray("с ролью суперпользователь", SUPER_USER),
                toArray("c доступом к сегменту", USER_GRANTEE),
                toArray("с правом на просмотр", USER_WITH_PERM_VIEW),
                toArray("с ролью менеджер", MANAGER)
        );
    }

    @Test
    public void getStat() {
        V1ManagementSegmentSegmentIdStatGETSchema userParamSchema = UserSteps.withUser(userParam).onSegmentsSteps()
                .getStat(owner.get(GEO_SEGMENT_ID), ulogin(owner));

        V1ManagementSegmentSegmentIdStatGETSchema ownerSchema = UserSteps.withUser(owner).onSegmentsSteps()
                .getStat(owner.get(GEO_SEGMENT_ID));

        assertThat("ответы совпадают", ownerSchema,
                equivalentTo(userParamSchema, BeanFieldPath.newPath("profile")));
    }
}
