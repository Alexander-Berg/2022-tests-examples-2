package ru.yandex.autotests.audience.management.tests.pixel;

import com.google.common.collect.ImmutableList;
import org.apache.commons.lang3.StringUtils;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static ru.yandex.autotests.audience.data.users.Users.SIMPLE_USER;
import static ru.yandex.autotests.audience.errors.ManagementError.INCORRECT_STRING_LENGTH;
import static ru.yandex.autotests.audience.errors.ManagementError.NOT_NULL;
import static ru.yandex.autotests.audience.management.tests.TestData.PIXEL_TOO_LONG_NAME;
import static ru.yandex.autotests.audience.management.tests.TestData.createPixelNegativeParam;

/**
 * Created by ava1on on 28.04.17.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({Requirements.Story.Management.PIXELS})
@Title("Pixel: создание пикселя (негативные тесты)")
@RunWith(Parameterized.class)
public class CreatePixelNegativeTest {
    private final UserSteps user = UserSteps.withUser(SIMPLE_USER);

    @Parameter
    public String description;

    @Parameter(1)
    public String name;

    @Parameter(2)
    public IExpectedError error;

    @Parameterized.Parameters(name = "{0}: {2}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.of(
                createPixelNegativeParam("пустое имя пикселя", StringUtils.EMPTY,
                        INCORRECT_STRING_LENGTH),
                createPixelNegativeParam("слишком длинное имя пикселя", PIXEL_TOO_LONG_NAME,
                        INCORRECT_STRING_LENGTH),
                createPixelNegativeParam("отсутствует параметр name",null, NOT_NULL)
        );
    }

    @Test
    public void checkTryCreatePixel() {
        user.onPixelsSteps().createPixelAndAndExpectError(error, name);
    }
}
