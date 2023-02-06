package ru.yandex.autotests.morda.tests.auth;

import org.junit.Rule;
import ru.yandex.autotests.morda.api.MordaClient;
import ru.yandex.autotests.morda.rules.allure.AllureLoggingRule;
import ru.yandex.autotests.morda.rules.users.MordaUserManagerRule;
import ru.yandex.autotests.morda.tests.MordaTestsProperties;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 19/09/16
 */
public abstract class AuthTest {
    protected static final MordaTestsProperties CONFIG = new MordaTestsProperties();

    @Rule
    public AllureLoggingRule allureLoggingRule = new AllureLoggingRule();
    @Rule
    public MordaUserManagerRule userManagerRule = new MordaUserManagerRule();

    protected MordaClient client = new MordaClient();
}
