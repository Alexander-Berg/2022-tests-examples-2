package ru.yandex.autotests.mainmorda.steps;

import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.data.ResourcesData;
import ru.yandex.qatools.allure.annotations.Step;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.containsString;
import static org.junit.Assume.assumeFalse;
import static ru.yandex.autotests.mainmorda.data.ResourcesData.MACHINE_NAME;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 11.04.13
 */
public class ResourcesSteps {
    private static final Properties CONFIG = new Properties();

    private WebDriver driver;

    public ResourcesSteps(WebDriver driver) {
        this.driver = driver;
    }

    @Step
    public void shouldSeeServerName() {
        String html = driver.getPageSource();
        assertThat(html, containsString(MACHINE_NAME));
        String name = html.substring(0, html.indexOf(MACHINE_NAME) + MACHINE_NAME.length());
        name = name.substring(name.lastIndexOf("<!--"));
        assertThat(name, ResourcesData.MACHINE_NAME_MATCHER);
    }

    @Step
    public void shouldNotSeeDevResources() {
        String html = driver.getPageSource();
        assertThat(html, ResourcesData.DEV_RESOURCES_MATCHER);
    }

    @Step
    public void ifNotDev() {
        assumeFalse("Need not dev", CONFIG.getMordaEnv().isDev());
    }
}
