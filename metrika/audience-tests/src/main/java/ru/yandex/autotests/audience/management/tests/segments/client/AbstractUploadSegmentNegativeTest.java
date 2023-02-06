package ru.yandex.autotests.audience.management.tests.segments.client;

import java.io.InputStream;
import java.util.Collection;
import java.util.function.Supplier;

import com.google.common.collect.ImmutableList;
import org.junit.runners.Parameterized;

import ru.yandex.autotests.audience.data.users.User;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.autotests.irt.testutils.RandomUtils;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;

import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.autotests.audience.data.users.Users.INTERNAL_DMP_UPLOADER;
import static ru.yandex.autotests.audience.data.users.Users.USER_FOR_INTERNAL_DMP;
import static ru.yandex.autotests.audience.errors.ManagementError.ACCESS_DENIED;
import static ru.yandex.autotests.audience.errors.ManagementError.USER_NOT_FOUND;

public class AbstractUploadSegmentNegativeTest {
    protected static final UserSteps userUploader = UserSteps.withUser(INTERNAL_DMP_UPLOADER);
    protected static final User TARGET_USER = USER_FOR_INTERNAL_DMP;

    @Parameterized.Parameter
    public String description;

    @Parameterized.Parameter(1)
    public UserSteps userParamUploader;

    @Parameterized.Parameter(2)
    public String userParam;

    @Parameterized.Parameter(3)
    public InputStream content;

    @Parameterized.Parameter(4)
    public IExpectedError error;

    public static Collection<Object[]> getParams(Supplier<InputStream> content) {
        return ImmutableList.of(
                toArray("нет прав \"заливателя\"", UserSteps.withDefaultUser(), TARGET_USER.toString(), content.get(),
                        ACCESS_DENIED),
                toArray("не существует аккаунт", userUploader, RandomUtils.getString(16), content.get(),
                        USER_NOT_FOUND)
        );
    }

}
