package ru.yandex.autotests.mordamobile.steps;

import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.mordamobile.pages.HomePage;
import ru.yandex.qatools.allure.annotations.Step;

import static org.junit.Assert.fail;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.exists;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18.04.13
 */
public class BannerSteps {
    private WebDriver driver;
    private HomePage homePage;

    public BannerSteps(WebDriver driver) {
        this.driver = driver;
        homePage = new HomePage(driver);
    }

    @Step
    public void shouldSeeBanner() {
        driver.manage().deleteAllCookies();
        for (int i = 0; i < 10; i++) {
            driver.get(driver.getCurrentUrl());
            if (exists().matches(homePage.banner)) {
                return;
            }
        }
        fail("Баннер не показался после 10 перезагрузок страницы");
    }
}
