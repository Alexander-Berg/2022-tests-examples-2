package ru.yandex.autotests.morda.steps;

import org.openqa.selenium.By;
import org.openqa.selenium.Cookie;
import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.morda.pages.MordaLanguage;
import ru.yandex.autotests.morda.utils.cookie.WebDriverCookieUtils;
import ru.yandex.geobase.regions.GeobaseRegion;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.cookies.my.CookieMy;

import static java.util.Arrays.asList;
import static org.hamcrest.CoreMatchers.containsString;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.notNullValue;
import static ru.yandex.autotests.morda.steps.NavigationSteps.refresh;
import static ru.yandex.autotests.morda.utils.cookie.CookieUtilsFactory.cookieUtils;
import static ru.yandex.autotests.morda.utils.cookie.MordaCookieUtils.MY;
import static ru.yandex.autotests.morda.utils.cookie.MordaCookieUtils.YANDEX_GID;
import static ru.yandex.autotests.morda.utils.cookie.MordaCookieUtils.YP;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 07/04/15
 */
public class TuneSteps {

    @Step("Set region {2} with cookie \"yandex_gid\"")
    public static void setRegionWithCookie(WebDriver driver, String cookieDomain, GeobaseRegion region) {
//        Cookie yp = cookieUtils(driver).getCookies().stream()
//                .filter(e -> "yp".equals(e.getName()))
//                .findFirst()
//                .orElseThrow(() -> new RuntimeException("yp cookie is missing"));
//
//        String newYpValue = yp.getValue().replaceAll("(?<=\\.ygu\\.)\\d", "0");
//
//        cookieUtils(driver).addCookie(YP, newYpValue, cookieDomain);
        cookieUtils(driver).addCookie(YANDEX_GID, String.valueOf(region.getRegionId()), cookieDomain);

        refresh(driver);

        shouldSeeRegion(driver, cookieDomain, region);
    }

    @Step("Set language {2} with cookie \"my\"")
    public static void setLanguageWithCookie(WebDriver driver, String cookieDomain, MordaLanguage language) {
        WebDriverCookieUtils utils = cookieUtils(driver);

        String cookieMyValue = utils.getCookieValue(utils.getCookieNamed(MY, cookieDomain));
        CookieMy cookieMy = new CookieMy(cookieMyValue);

        cookieMy.setBlock(39, asList(0, language.getIntl()));

        utils.addCookie(MY, cookieMy.toString(), cookieDomain);

        refresh(driver);

        shouldSeeLangInCookieMy(driver, cookieDomain, language);

        String languageInMordaCode = driver.findElement(By.xpath("//html")).getAttribute("lang");
        assertThat("Не тот язык на морде", languageInMordaCode, equalTo(language.getValue()));
    }

    @Step("Should see lang {2} in cookie \"my\"")
    public static void shouldSeeLangInCookieMy(WebDriver driver, String cookieDomain, MordaLanguage language) {
        WebDriverCookieUtils utils = cookieUtils(driver);
        String newCookieMyValue = utils.getCookieValue(utils.getCookieNamed(MY, cookieDomain));
        Integer langNumber = new CookieMy(newCookieMyValue).getBlock(39).get(1);
        assertThat("Кука \"my\" не поставилась", langNumber, equalTo(language.getIntl()));
    }

    @Step("Should see region {2} in cookie \"yandex_gid\"")
    public static void shouldSeeRegion(WebDriver driver, String cookieDomain, GeobaseRegion region) {
        Cookie yandexGid = cookieUtils(driver).getCookieNamed(YANDEX_GID, cookieDomain);

        assertThat("Cookie yandex_gid not found", yandexGid, notNullValue());
        assertThat("Cookie yandex_gid", yandexGid.getValue(), equalTo(String.valueOf(region.getRegionId())));
    }

    @Step("YP should contains {2}")
    public static void ypShouldContains(WebDriver driver, String cookieDomain, String subString) {
        Cookie yp = cookieUtils(driver).getCookieNamed(YP, cookieDomain);

        assertThat("Cookie yp not found", yp, notNullValue());
        assertThat("Cookie yp", yp.getValue(), containsString(subString));
    }

    @Step("MY should contains {2}")
    public static void myShouldContains(WebDriver driver, String cookieDomain, int block) {
        WebDriverCookieUtils utils = cookieUtils(driver);
        String myValue = utils.getCookieValue(utils.getCookieNamed(MY, cookieDomain));
        Integer num = new CookieMy(myValue).getBlock(block).get(0);
        assertThat("Кука \"my\" неверная", num, equalTo(1));
    }


}
