package ru.yandex.metrika;

import ru.yandex.metrika.auth.AuthUtils;
import ru.yandex.metrika.auth.MetrikaUserDetails;

public class CommonTestsHelper {

    public static final MetrikaUserDetails FAKE_USER = AuthUtils.buildSimpleUserDetails(42, "localhost");
    public static final int counterId = 42;
}
