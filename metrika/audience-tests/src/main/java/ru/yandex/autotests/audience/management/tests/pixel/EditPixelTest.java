package ru.yandex.autotests.audience.management.tests.pixel;

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
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;

import static ru.yandex.autotests.audience.data.users.Users.USER_DELEGATOR;
import static ru.yandex.autotests.audience.data.wrappers.WrapperBase.wrap;
import static ru.yandex.autotests.audience.management.tests.TestData.*;
import static ru.yandex.autotests.metrika.commons.beans.BeanDifferMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.commons.beans.BeanDifferMatchers.hasBeanEquivalent;
import static ru.yandex.autotests.audience.parameters.ULoginParameters.ulogin;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;

/**
 * Created by ava1on on 28.04.17.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({Requirements.Story.Management.PIXELS})
@Title("Pixel: редактирование пикселя")
@RunWith(Parameterized.class)
public class EditPixelTest {
    private final User owner = USER_DELEGATOR;

    private Pixel editedPixel;
    private Pixel expectedPixel;
    private Long pixelId;
    private UserSteps user;

    @Parameter
    public String newName;

    @Parameter(1)
    public User userParam;

    @Parameter(2)
    public String userDescription;

    @Parameterized.Parameters(name = "пользователь {2}, новое имя: {0}")
    public static Collection<Object[]> createParameters() {
        return CombinatorialBuilder.builder()
                .values(getPixelName(), PIXEL_BOUNDARY_LENGTH_NAME)
                .vectorValues(getSuperUser(), getUserWithPermEdit(), getOwner())
                .build();
    }

    @Before
    public void setup() {
        user = UserSteps.withUser(userParam);
        Pixel createdPixel = user.onPixelsSteps().createPixel(getPixelName(), ulogin(owner));
        pixelId = createdPixel.getId();

        editedPixel = user.onPixelsSteps().editPixel(pixelId, newName, ulogin(owner));
        expectedPixel = wrap(createdPixel).getClone().withName(newName);
    }

    @Test
    public void checkEditPixel() {
        assertThat("измененный пиксель совпадает с ожидаемым", editedPixel,
                equivalentTo(expectedPixel));
    }

    @Test
    public void checkEditedPixelInList() {
        List<Pixel> pixels = user.onPixelsSteps().getPixels(ulogin(owner));

        assertThat("измененный пиксель присутстует в списке", pixels,
                hasBeanEquivalent(Pixel.class, expectedPixel));
    }

    @After
    public void tearDown() {
        user.onPixelsSteps().deletePixelAndIgnoreStatus(pixelId, ulogin(owner));
    }
}
