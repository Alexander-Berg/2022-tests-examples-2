package ru.yandex.autotests.audience.management.tests.pixel;

import com.google.common.collect.ImmutableList;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import ru.yandex.audience.pixel.Pixel;
import ru.yandex.autotests.audience.data.users.User;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;

import static org.apache.commons.lang3.ArrayUtils.toArray;
import static org.hamcrest.Matchers.both;
import static org.hamcrest.Matchers.iterableWithSize;
import static org.hamcrest.collection.IsIn.isIn;
import static org.hamcrest.core.Every.everyItem;
import static ru.yandex.autotests.audience.data.users.Users.*;
import static ru.yandex.autotests.audience.parameters.ULoginParameters.ulogin;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;

/**
 * Created by ava1on on 23.06.17.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({Requirements.Story.Management.GRANTS})
@Title("Роли: получение списка пикселей разными ролями")
@RunWith(Parameterized.class)
public class GetPixelsListTest {
    private final User owner = USER_DELEGATOR_3;

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
    public void checkPixelList() {
        List<Pixel> userParamList = UserSteps.withUser(userParam).onPixelsSteps().getPixels(ulogin(owner));
        List<Pixel> ownerList = UserSteps.withUser(owner).onPixelsSteps().getPixels();

        assertThat("список пикселей совпадает", userParamList,
                both(everyItem(isIn(ownerList))).and(iterableWithSize(ownerList.size())));
    }
}
