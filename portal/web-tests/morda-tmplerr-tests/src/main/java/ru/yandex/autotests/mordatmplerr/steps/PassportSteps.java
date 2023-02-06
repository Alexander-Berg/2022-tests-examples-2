package ru.yandex.autotests.mordatmplerr.steps;

import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordatmplerr.mordatypes.ComMorda;
import ru.yandex.autotests.mordatmplerr.mordatypes.ComTrMorda;
import ru.yandex.autotests.mordatmplerr.mordatypes.Morda;
import ru.yandex.qatools.allure.annotations.Step;

import java.net.MalformedURLException;
import java.net.URL;

import static ru.yandex.autotests.utils.morda.users.UserType.DEFAULT;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 06.05.14
 */
public class PassportSteps {
    private static final String COM_PASSPORT_HOST = "https://passport.yandex.com/";
    private static final String COM_TR_PASSPORT_HOST = "https://passport.yandex.com.tr/";
    private static final String PASSPORT_HOST = "https://passport.yandex.ru/";

    private CommonMordaSteps user;
    private MordaAllureBaseRule rule;

    public PassportSteps(WebDriver driver, MordaAllureBaseRule rule) {
        user = new CommonMordaSteps(driver);
        this.rule = rule;
    }

    @Step
    public void login(Morda morda, String retpath) {
        try {
            if (morda instanceof ComMorda) {
                user.logsInAs(rule.getUser(DEFAULT), new URL(COM_PASSPORT_HOST), retpath);

            } else if (morda instanceof ComTrMorda) {
                user.logsInAs(rule.getUser(DEFAULT), new URL(COM_TR_PASSPORT_HOST), retpath);
            } else {
                user.logsInAs(rule.getUser(DEFAULT), new URL(PASSPORT_HOST), retpath);
            }
        } catch (MalformedURLException e) {
            throw new RuntimeException(e);
        }
    }
}
