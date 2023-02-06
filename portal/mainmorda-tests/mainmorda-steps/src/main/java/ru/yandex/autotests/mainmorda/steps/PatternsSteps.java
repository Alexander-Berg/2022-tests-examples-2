package ru.yandex.autotests.mainmorda.steps;

import org.hamcrest.Matcher;
import org.hamcrest.Matchers;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.utils.WidgetPattern;
import ru.yandex.autotests.mainmorda.utils.WidgetPatternParameter;
import ru.yandex.autotests.mainmorda.utils.WidgetProperties;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.cookie.Cookie;
import ru.yandex.autotests.utils.morda.url.Domain;
import ru.yandex.autotests.utils.morda.url.UrlManager;
import ru.yandex.qatools.allure.annotations.Step;

import java.util.HashMap;
import java.util.regex.Pattern;

import static org.apache.commons.codec.digest.HmacUtils.hmacSha256Hex;
import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.greaterThan;
import static ru.yandex.autotests.mainmorda.data.CoordinatesData.MDA_DOMAINS;
import static ru.yandex.autotests.mainmorda.data.WidgetsData.FAKE_PARAMETERS;
import static ru.yandex.autotests.mainmorda.data.WidgetsData.FAKE_PATTERN;
import static ru.yandex.autotests.mainmorda.data.WidgetsData.LENTARU;
import static ru.yandex.autotests.mainmorda.data.WidgetsData.WidgetInfo;
import static ru.yandex.autotests.mainmorda.matchers.WidgetPatternMatcher.equalsToPattern;
import static ru.yandex.autotests.mainmorda.matchers.WidgetPatternMatcher.matchesToPattern;
import static ru.yandex.autotests.mainmorda.utils.WidgetPattern.createPatternFromMap;
import static ru.yandex.autotests.mainmorda.utils.WidgetPattern.createPatternFromString;
import static ru.yandex.autotests.mainmorda.utils.WidgetPattern.getParameterValue;
import static ru.yandex.autotests.mainmorda.utils.WidgetPatternParameter.DEFSKIN;
import static ru.yandex.autotests.mainmorda.utils.WidgetPatternParameter.YU;
import static ru.yandex.autotests.utils.morda.cookie.CookieManager.getCookie;
import static ru.yandex.autotests.utils.morda.cookie.CookieManager.getUid;

/**
 * User: alex89
 * Date: 07.12.12
 */

public class PatternsSteps {
    private static final Properties CONFIG = new Properties();

    private WebDriver driver;
    private CommonMordaSteps userSteps;
    private WidgetSteps userWidget;
    private MainPage mainPage;
    private ModeSteps userMode;

    public PatternsSteps(WebDriver driver) {
        this.driver = driver;
        this.userSteps = new CommonMordaSteps(driver);
        this.mainPage = new MainPage(driver);
        this.userWidget = new WidgetSteps(driver);
        this.userMode = new ModeSteps(driver);
    }

    public static void main(String[] args) {
        System.out.println(hmacSha256Hex("zxhCGbvp01cEvQCw", "0:6447714881391768016:1438861751"));
    }

    private String getQuery() {
        return (String) ((JavascriptExecutor) driver).executeScript("return window.wg.getQueryForSave()");
    }

    @Step
    public void shouldSeeFakePatternRequest() {
        String request = getQuery();
        WidgetPattern fakeActual = createPatternFromString(UrlManager.decode(request));
        assertThat("Некорректный формат фэйкового паттерн-запроса!", fakeActual,
                matchesToPattern(FAKE_PATTERN));

        String yu = getParameterValue(request, YU);
        String ts = yu.split("%3A")[1];

        String hmac = getHmac(ts);

        assertThat("В паттерн-запросе неверно считается yu как hmacSha256Hex(key, uid:yandexuid:ts):ts",
                yu,
                equalTo(hmac + "%3A" + ts));
    }

    @Step
    public void shouldSeeFakePatternRequestForSkin(final String skinId) {
        String request = getQuery();
        WidgetPattern fakeActual = createPatternFromString(UrlManager.decode(request));
        WidgetPattern fakeExpected = createPatternFromMap(
                new HashMap<WidgetPatternParameter, String>(FAKE_PARAMETERS) {{
                    put(DEFSKIN, skinId);
                }},
                new HashMap<String, WidgetProperties>()
        );

        String yu = getParameterValue(request, YU);
        String ts = yu.split("%3A")[1];

        String hmac = getHmac(ts);

        assertThat("Некорректный формат фэйкового паттерн-запроса!", fakeActual,
                matchesToPattern(fakeExpected));

        assertThat("В паттерн-запросе неверно считается yu как hmacSha256Hex(key, uid:yandexuid:ts):ts",
                yu,
                equalTo(hmac + "%3A" + ts));
    }

    private String getHmac(String ts) {
        return hmacSha256Hex("wDNS0i46do6S8eSzYcJl", getUid(getCookie(driver, Cookie.SESSION_ID)) + ":" +
                getCookie(driver, Cookie.YANDEXUID) + ":" + ts);
    }

    @Step
    public void shouldSeeRebindParameterInRequestForWidget(WidgetInfo widget, Matcher<String> valueMatcher) {
        String rebind = getRebindProperty(widget.getName());
        assertThat("Неправильный параметр автообновления у блока '" + widget + "'!",
                rebind, valueMatcher);
    }

    private String getRebindProperty(String widget) {
        JavascriptExecutor js = (JavascriptExecutor) driver;
        String script = js.executeScript(
                String.format("return window.document.getElementById('wd-wrapper-%s-%s')." +
                        "previousElementSibling.innerHTML", widget, "_stocks".equals(widget) ? "2" : "1")).toString();
        if (script == null) {
            return "null";
        } else {
            return parseRebindProperty(script);
        }
    }

    private String parseRebindProperty(String script) {
        java.util.regex.Matcher rebindParameterFinder =
                Pattern.compile("(?<=,rebind:\\s?\")\\d*(?=\",)").matcher(script);
        if (rebindParameterFinder.find()) {
            return rebindParameterFinder.group();
        } else {
            return "none";
        }
    }

    @Step
    public WidgetPattern getPatternInEditMode() {
        return createPatternFromString(UrlManager.decode(getQuery()));
    }

    @Step
    public void shouldSeePatternRequest(WidgetPattern workPattern) {
        String request = getQuery();

        String yu = getParameterValue(request, YU);
        String ts = yu.split("%3A")[1];

        String hmac = getHmac(ts);

        WidgetPattern actualPattern = createPatternFromString(UrlManager.decode(request));
        assertThat(actualPattern, equalsToPattern(workPattern));
        assertThat("В паттерн-запросе неверно считается yu как hmacSha256Hex(key, uid:yandexuid:ts):ts",
                yu,
                equalTo(hmac + "%3A" + ts));
    }

    /*
    * Сбрасываем настройки морды во всех доменах.
    */
    @Step
    public void resetSettingsInAllDomains() {
        for (Domain domain : MDA_DOMAINS) {
            String url = CONFIG.getBaseURL().replace(CONFIG.getBaseDomain().toString(), domain.toString());
            userMode.resetSettings(url);
        }
    }

    @Step
    public void setWidgetModeInMdaDomains() {
        for (Domain domain : MDA_DOMAINS) {
            userSteps.setsRegion(domain.getCapital());
            userMode.setWidgetMode(CONFIG.getBaseURL().replace(Domain.RU.toString(), domain.toString()));
        }
    }


    @Step
    public void addLentaRuWidgetByUrl(String url) {
        driver.get(url);
    }

    @Step
    public void deleteNewsBlock() {
        userSteps.shouldSeeElement(mainPage.newsBlock.closeCross);
        userSteps.clicksOn(mainPage.newsBlock.closeCross);
        userSteps.shouldNotSeeElement(mainPage.newsBlock);
    }

    @Step
    public void setupServicesWidget() {
        userSteps.shouldSeeElement(mainPage.servicesBlock.editIcon);
        userSteps.clicksOn(mainPage.servicesBlock.editIcon);
        userSteps.shouldSeeElement(mainPage.servicesSettings);
        userSteps.shouldSeeElement(mainPage.servicesSettings.removeAllServicesButton);
        userSteps.clicksOn(mainPage.servicesSettings.removeAllServicesButton);
        userSteps.shouldSeeElement(mainPage.servicesSettings.okButton);
        userSteps.clicksOn(mainPage.servicesSettings.okButton);
        userSteps.shouldNotSeeElement(mainPage.servicesSettings);
    }

    @Step
    public void addLentaWidget(String url) {
        userWidget.addWidget(url, LENTARU.getName());
        userSteps.opensPage(url);
    }

    @Step
    public void setPattern(String url) {
        userMode.setEditMode(url);
        deleteNewsBlock();
        setupServicesWidget();
        userMode.saveSettings();
        addLentaWidget(url);
    }

    @Step
    public void shouldNotSeePattern() {
        userSteps.shouldSeeElement(mainPage.newsBlock);
        userSteps.shouldNotSeeElement(mainPage.lentaRuWidget);
        userSteps.shouldSeeListWithSize(mainPage.servicesBlock.allServices, greaterThan(1));
    }

    @Step
    public void shouldSeePattern() {
        userMode.shouldSeeWidgetMode();
        userSteps.shouldNotSeeElement(mainPage.newsBlock);
        userSteps.shouldSeeElement(mainPage.lentaRuWidget);
        userSteps.shouldSeeListWithSize(mainPage.servicesBlock.allServices, Matchers.equalTo(1));
    }

    @Step
    public void shouldNotSeeSavedPatternInMdaDomains() {
        for (Domain domain : MDA_DOMAINS) {
            userSteps.setsRegion(domain.getCapital());
            shouldNotSeePattern();
        }
    }

    @Step
    public void shouldSeeThatSomeImportantMordaElementsArePresent() {
        userSteps.shouldSeeElement(mainPage.headerBlock);
        userSteps.shouldSeeElement(mainPage.footerBlock);
        userSteps.shouldSeeElement(mainPage.footerBlock.designTextAndLink);
        userSteps.shouldSeeElement(mainPage.search.input);
        userSteps.shouldSeeElement(mainPage.search.submit);
        userSteps.shouldSeeListWithSize(mainPage.search.tabs, greaterThan(5));
    }
}
