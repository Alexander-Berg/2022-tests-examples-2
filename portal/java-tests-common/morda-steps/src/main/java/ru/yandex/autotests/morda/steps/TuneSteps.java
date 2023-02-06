package ru.yandex.autotests.morda.steps;

import org.openqa.selenium.By;
import org.openqa.selenium.Cookie;
import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.morda.utils.cookie.WebDriverCookieUtils;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.autotests.utils.morda.url.UrlManager;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.cookies.my.CookieMy;

import javax.ws.rs.core.UriBuilder;
import java.net.URI;
import java.util.HashMap;
import java.util.Map;

import static java.util.Arrays.asList;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.notNullValue;
import static ru.yandex.autotests.morda.steps.NavigationSteps.refresh;
import static ru.yandex.autotests.morda.utils.cookie.CookieUtilsFactory.cookieUtils;
import static ru.yandex.autotests.morda.utils.cookie.MordaCookieUtils.MY;
import static ru.yandex.autotests.morda.utils.cookie.MordaCookieUtils.YANDEX_GID;
import static ru.yandex.autotests.morda.utils.cookie.MordaCookieUtils.YP;
import static ru.yandex.autotests.utils.morda.language.Language.BE;
import static ru.yandex.autotests.utils.morda.language.Language.EN;
import static ru.yandex.autotests.utils.morda.language.Language.ID;
import static ru.yandex.autotests.utils.morda.language.Language.KK;
import static ru.yandex.autotests.utils.morda.language.Language.RU;
import static ru.yandex.autotests.utils.morda.language.Language.TR;
import static ru.yandex.autotests.utils.morda.language.Language.TT;
import static ru.yandex.autotests.utils.morda.language.Language.UK;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 07/04/15
 */
public class TuneSteps {

    private static final Map<Language, Integer> LANG_INT_VALUES = new HashMap<Language, Integer>() {{
        put(RU, 1);
        put(UK, 2);
        put(EN, 3);
        put(KK, 4);
        put(BE, 5);
        put(TT, 6);
        put(TR, 8);
        put(ID, 13);

    }};

    public static URI getTuneRegionUri(URI tuneUri, Region region, String retpath, String sk) {
        return UriBuilder.fromUri(tuneUri)
                .path("pages/region/do/save.xml")
                .queryParam("region_id", region.getRegionId())
                .queryParam("retpath", UrlManager.encode(retpath))
                .queryParam("sk", sk)
                .build();
    }

    public static URI getTuneLanguageUri(URI tuneUri, Language language, String retpath, String sk) {
        return UriBuilder.fromUri(tuneUri)
                .path("api")
                .path("lang")
                .path("v1.1")
                .path("save.xml")
                .queryParam("intl", language.getValue())
                .queryParam("retpath", UrlManager.encode(retpath))
                .queryParam("sk", sk)
                .build();
    }

    @Step("Set region {3}")
    public static void setRegion(WebDriver driver, URI tuneUri, String cookieDomain, Region region) {
        URI setRegionURI = getTuneRegionUri(tuneUri, region, driver.getCurrentUrl(),
                cookieUtils(driver).getSecretKey(cookieDomain));

        System.out.println(setRegionURI);

        driver.get(setRegionURI.toString());

        Cookie yandexGid = cookieUtils(driver).getCookieNamed(YANDEX_GID, cookieDomain);

        assertThat("Cookie yandex_gid not found", yandexGid, notNullValue());
        assertThat("Cookie yandex_gid", yandexGid.getValue(), equalTo(region.getRegionId()));
    }

    @Step("Set region {3} with retpath {4}")
    public static void setRegion(WebDriver driver, URI tuneUri, String cookieDomain, Region region, String retpath) {
        URI setRegionURI = getTuneRegionUri(tuneUri, region, retpath,
                cookieUtils(driver).getSecretKey(cookieDomain));

        System.out.println(setRegionURI);

        driver.get(setRegionURI.toString());

        Cookie yandexGid = cookieUtils(driver).getCookieNamed(YANDEX_GID, cookieDomain);

        assertThat("Cookie yandex_gid not found", yandexGid, notNullValue());
        assertThat("Cookie yandex_gid", yandexGid.getValue(), equalTo(region.getRegionId()));
    }

    @Step("Set language {3}")
    public static void setLanguage(WebDriver driver, URI tuneUri, String cookieDomain, Language language) {
        URI setLanguageURI = getTuneLanguageUri(tuneUri, language, driver.getCurrentUrl(),
                cookieUtils(driver).getSecretKey(cookieDomain));

        System.out.println(setLanguageURI);

        driver.get(setLanguageURI.toString());

//        Cookie yandexGid = cookieUtils(getDriver).getCookieNamed(MordaCookieNames.YANDEX_GID, cookieDomain);

//        assertThat("Cookie yandex_gid not found", yandexGid, notNullValue());
//        assertThat("Cookie yandex_gid", yandexGid.getValue(), equalTo(region.getRegionId()));
    }


    @Step("Set language new tune{3}")
    public static void setLanguageNewTune(WebDriver driver, URI tuneUri, String cookieDomain, Language language) {
        WebDriverCookieUtils utils = cookieUtils(driver);

        URI setLanguageURI = getLanguageUri(
                tuneUri,
                language,
                driver.getCurrentUrl(),
                cookieUtils(driver).getSecretKey(cookieDomain));

        System.out.println(setLanguageURI);

        driver.get(setLanguageURI.toString());

        String cookieMyValue = utils.getCookieValue(utils.getCookieNamed(MY, cookieDomain));
        Integer langNumber = new CookieMy(cookieMyValue).getBlock(39).get(1);
        String languageInMordaCode = driver.findElement(By.xpath("//html")).getAttribute("lang");

        assertThat("Кука \"my\" не поставилась", langNumber, equalTo(LANG_INT_VALUES.get(language)));
        assertThat("Не тот язык на морде", languageInMordaCode, equalTo(language.getValue()));
    }

    @Step("Set region new tune {3}")
    public static void setRegionNewTune(WebDriver driver, URI tuneUri, String cookieDomain, Region region) {
        URI setRegionURI = getRegionUri(tuneUri, region, driver.getCurrentUrl(),
                cookieUtils(driver).getSecretKey(cookieDomain));

        System.out.println(setRegionURI);

        driver.get(setRegionURI.toString());

        Cookie yandexGid = cookieUtils(driver).getCookieNamed(YANDEX_GID, cookieDomain);

        assertThat("Cookie yandex_gid not found", yandexGid, notNullValue());
        assertThat("Cookie yandex_gid", yandexGid.getValue(), equalTo(region.getRegionId()));
    }

    public static URI getLanguageUri(URI tuneUri, Language language, String retpath, String sk) {
        return UriBuilder.fromUri(tuneUri)
                .path("portal")
                .path("set")
                .path("lang")
                .queryParam("sk", sk)
                .queryParam("intl", language.getValue())
                .queryParam("retpath", UrlManager.encode(retpath))
                .build();
    }

    public static URI getRegionUri(URI tuneUri, Region region, String retpath, String sk) {
        return UriBuilder.fromUri(tuneUri)
                .path("portal")
                .path("set")
                .path("region")
                .queryParam("sk", sk)
                .queryParam("id", region.getRegionId())
                .queryParam("retpath", UrlManager.encode(retpath))
                .build();
    }

    @Step("Set region {2} with cookie \"yandex_gid\"")
    public static void setRegionWithCookie(WebDriver driver, String cookieDomain, Region region) {
        Cookie yp = cookieUtils(driver).getCookies().stream()
                .filter(e -> "yp".equals(e.getName()))
                .findFirst()
                .orElseThrow(() -> new RuntimeException("yp cookie is missing"));

        String newYpValue = yp.getValue().replaceAll("(?<=\\.ygu\\.)\\d", "0");

        cookieUtils(driver).addCookie(YP, newYpValue, cookieDomain);
        cookieUtils(driver).addCookie(YANDEX_GID, region.getRegionId(), cookieDomain);

        refresh(driver);

        shouldSeeRegion(driver, cookieDomain, region);
    }

    @Step("Set language {2} with cookie \"my\"")
    public static void setLanguageWithCookie(WebDriver driver, String cookieDomain, Language language) {
        WebDriverCookieUtils utils = cookieUtils(driver);

        String cookieMyValue = utils.getCookieValue(utils.getCookieNamed(MY, cookieDomain));
        CookieMy cookieMy = new CookieMy(cookieMyValue);

        cookieMy.setBlock(39, asList(0, LANG_INT_VALUES.get(language)));

        utils.addCookie(MY, cookieMy.toString(), cookieDomain);

        refresh(driver);

        shouldSeeLangInCookieMy(driver, cookieDomain, language);

        String languageInMordaCode = driver.findElement(By.xpath("//html")).getAttribute("lang");
        assertThat("Не тот язык на морде", languageInMordaCode, equalTo(language.getValue()));
    }

    @Step("Should see lang {2} in cookie \"my\"")
    public static void shouldSeeLangInCookieMy(WebDriver driver, String cookieDomain, Language language) {
        WebDriverCookieUtils utils = cookieUtils(driver);
        String newCookieMyValue = utils.getCookieValue(utils.getCookieNamed(MY, cookieDomain));
        Integer langNumber = new CookieMy(newCookieMyValue).getBlock(39).get(1);
        assertThat("Кука \"my\" не поставилась", langNumber, equalTo(LANG_INT_VALUES.get(language)));
    }

    @Step("Should see region {2} in cookie \"yandex_gid\"")
    public static void shouldSeeRegion(WebDriver driver, String cookieDomain, Region region) {
        Cookie yandexGid = cookieUtils(driver).getCookieNamed(YANDEX_GID, cookieDomain);
        assertThat("Cookie yandex_gid not found", yandexGid, notNullValue());
        assertThat("Cookie yandex_gid", yandexGid.getValue(), equalTo(region.getRegionId()));
    }


}
