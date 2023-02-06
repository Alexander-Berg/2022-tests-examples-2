package ru.yandex.autotests.internalapid.tests;

import ru.yandex.autotests.internalapid.steps.UserSteps;

public class InternalApidTest {

    protected static final UserSteps userSteps = new UserSteps();

    static {
//        userSteps.onMySqlSteps().prepare();
    }
}
