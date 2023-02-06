package ru.yandex.autotests.morda.steps;

import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.lib.junit.rules.passport.PassportRule;
import ru.yandex.qatools.usermanager.beans.UserData;

/**
 * User: asamar
 * Date: 11.01.17
 */
public class AuthSteps {

    public static void login(WebDriver driver, UserData user, String retpath) {
         login(driver, user.getLogin(), user.getPassword(), retpath);
    }

    public static void login(WebDriver driver, UserData user) {
        login(driver, user.getLogin(), user.getPassword());
    }

    public static void login(WebDriver driver, String login, String pass, String retpath) {
        new PassportRule(driver)
                .withLoginPassword(login, pass)
                .withRetpath(retpath)
                .login();

//        return MatcherDecorators.should(not(LoginMatcher.isLogged()))
//                .whileWaitingUntil(timeoutHasExpired(5000))
//                .matches(driver);
    }

    public static void login(WebDriver driver, String login, String pass) {
        new PassportRule(driver)
                .withLoginPassword(login, pass)
                .login();
//        return MatcherDecorators.should(not(LoginMatcher.isLogged()))
//                .whileWaitingUntil(timeoutHasExpired(5000))
//                .matches(driver);
    }



}
