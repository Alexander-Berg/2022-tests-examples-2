package ru.yandex.autotests.mainmorda.steps;

import org.openqa.selenium.WebDriver;
import ru.yandex.qatools.allure.annotations.Step;

import static ru.yandex.autotests.utils.morda.cookie.Cookie.YANDEXUID;
import static ru.yandex.autotests.utils.morda.cookie.CookieManager.addCookie;
import static ru.yandex.autotests.utils.morda.cookie.CookieManager.deleteCookie;

/**
 * User: lipka
 * Date: 05.08.13
 */
public class YandexUidSteps {
    public static final String COUNTER_UID = "7086015271313068940";

    private WebDriver driver;

    public YandexUidSteps(WebDriver driver) {
        this.driver = driver;
    }

    @Step
    public void setsUIDWithCounters() {
        deleteCookie(driver, YANDEXUID);
        addCookie(driver, YANDEXUID, COUNTER_UID);
    }
}
