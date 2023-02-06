package ru.yandex.autotests.mordamobile.steps;

import org.openqa.selenium.Cookie;
import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordamobile.Properties;
import ru.yandex.autotests.mordamobile.pages.HomePage;
import ru.yandex.qatools.allure.annotations.Step;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.notNullValue;
import static ru.yandex.autotests.mordacommonsteps.matchers.RegexMatcher.matches;

/**
 * @author Ivan Nikolaev <ivannik@yandex-team.ru>
 */
public class TeaserSteps {
    private static final Properties CONFIG = new Properties();

    private WebDriver driver;
    private HomePage homePage;
    public CommonMordaSteps userSteps;

    public TeaserSteps(WebDriver driver) {
        this.driver = driver;
        userSteps = new CommonMordaSteps(driver);
        homePage = new HomePage(driver);
    }

    @Step
    public void shouldSeeYabsFrequencyCookie() {
        Cookie yfCookie = driver.manage().getCookieNamed("yabs-frequency");
        assertThat("Кука yabs-frequency отсутствует", yfCookie, notNullValue());
        assertThat("Кука yabs-frequency имеет неправильный формат", yfCookie.getValue(), matches("/\\d/\\d+/[^/]+/"));
    }
}
