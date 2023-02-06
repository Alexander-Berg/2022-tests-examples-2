package ru.yandex.autotests.audience.management.tests.roles;

import com.google.common.collect.ImmutableList;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import ru.yandex.audience.BaseSegment;
import ru.yandex.autotests.audience.data.users.User;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;

import static org.apache.commons.lang3.ArrayUtils.toArray;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.audience.data.users.Users.*;
import static ru.yandex.autotests.audience.parameters.ULoginParameters.ulogin;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;

/**
 * Created by ava1on on 23.06.17.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({Requirements.Story.Management.GRANTS})
@Title("Роли: получение списка сегментов разными ролями")
@RunWith(Parameterized.class)
public class GetSegmentsListTest {
    public final User owner = USER_DELEGATOR_3;

    @Parameter
    public String description;

    @Parameter(1)
    public User userParam;

    @Parameterized.Parameters(name = "Пользователь {0}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.of(
                toArray("с правом на просмотр", USER_WITH_PERM_VIEW),
                toArray("с правом на редактирование", USER_WITH_PERM_EDIT),
                toArray("с ролью менеджер", MANAGER),
                toArray("с ролью суперпользователь", SUPER_USER)
        );
    }

    @Test
    public void checkSegmentList() {
        List<BaseSegment> userParamList = UserSteps.withUser(userParam).onSegmentsSteps().getSegments(ulogin(owner));
        List<BaseSegment> ownerList = UserSteps.withUser(owner).onSegmentsSteps().getSegments();

        assertThat("списки сегментов совпадают", ownerList,
                both(everyItem(isIn(userParamList))).and(iterableWithSize(userParamList.size())));
    }
}
