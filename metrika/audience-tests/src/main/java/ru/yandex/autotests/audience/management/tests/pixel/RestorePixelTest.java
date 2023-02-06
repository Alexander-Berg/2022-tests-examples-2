package ru.yandex.autotests.audience.management.tests.pixel;

import com.google.common.collect.ImmutableList;
import org.junit.After;
import org.junit.Before;
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

import static ru.yandex.autotests.audience.data.users.Users.USER_DELEGATOR;
import static ru.yandex.autotests.audience.management.tests.TestData.*;
import static ru.yandex.autotests.metrika.commons.beans.BeanDifferMatchers.hasBeanEquivalent;
import static ru.yandex.autotests.audience.parameters.ULoginParameters.ulogin;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;

/**
 * Created by ava1on on 28.04.17.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({Requirements.Story.Management.PIXELS})
@Title("Pixel: восстановление пикселя")
@RunWith(Parameterized.class)
public class RestorePixelTest {
    private final User owner = USER_DELEGATOR;

    private Pixel pixel;
    private Long pixelId;
    private UserSteps user;

    @Parameter
    public User userParam;

    @Parameter(1)
    public String userDescription;

    @Parameterized.Parameters(name = "пользователь {1}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.of(
                getSuperUser().toArray(),
                getUserWithPermEdit().toArray(),
                getOwner().toArray()
        );
    }

    @Before
    public void setup() {
        user = UserSteps.withUser(userParam);
        pixel = user.onPixelsSteps().createPixel(getPixelName(), ulogin(owner));
        pixelId = pixel.getId();
        user.onPixelsSteps().deletePixel(pixelId, ulogin(owner));

        user.onPixelsSteps().restorePixel(pixelId, ulogin(owner));
    }

    @Test
    public void checkPixelIsInList() {
        List<Pixel> pixels = user.onPixelsSteps().getPixels(ulogin(owner));

        assertThat("восстановленный пиксель присутствует в списке", pixels,
                hasBeanEquivalent(Pixel.class, pixel));
    }

    @After
    public void tearDown() {
        user.onPixelsSteps().deletePixelAndIgnoreStatus(pixelId, ulogin(owner));
    }
}
