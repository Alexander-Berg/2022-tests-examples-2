package ru.yandex.autotests.turkey.steps;

import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.turkey.Properties;
import ru.yandex.autotests.turkey.data.FootballData.FootballClub;
import ru.yandex.autotests.turkey.pages.YandexComTrPage;
import ru.yandex.autotests.utils.morda.cookie.Cookie;
import ru.yandex.autotests.utils.morda.cookie.CookieManager;
import ru.yandex.qatools.allure.annotations.Step;

import static org.hamcrest.Matchers.containsString;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.CLASS;

/**
 * User: leonsabr
 * Date: 05.10.12
 */
public class FootballSteps {
    private static final Properties CONFIG = new Properties();
    private WebDriver driver;
    private YandexComTrPage yandexComTrPage;
    private CommonMordaSteps userSteps;

    public FootballSteps(WebDriver driver) {
        this.driver = driver;
        userSteps = new CommonMordaSteps(driver);
        yandexComTrPage = new YandexComTrPage(driver);
    }

    @Step("Set {0} football style")
    public void setFootballStyle(FootballClub club) {
        String ysCookie = CookieManager.getCookie(driver, Cookie.YS);
        userSteps.addCookie(driver, Cookie.MDA, "0");
        if(ysCookie == null){
            userSteps.addCookie(driver, Cookie.YS, "ybf." + club.getShortName());
        } else {
            CookieManager.deleteCookie(driver, Cookie.YS);
            userSteps.addCookie(driver, Cookie.YS, ysCookie + "#ybf." + club.getShortName());
        }
    }

    @Step("Should have {0} football style")
    public void shouldSeeFootballStyle(FootballClub club) {
        userSteps.shouldSeeElement(yandexComTrPage.footballStyle);
        userSteps.shouldSeeElementMatchingTo(yandexComTrPage.footballStyle,
                hasAttribute(CLASS, containsString("b-page_" + club.getShortName())));
    }
}
