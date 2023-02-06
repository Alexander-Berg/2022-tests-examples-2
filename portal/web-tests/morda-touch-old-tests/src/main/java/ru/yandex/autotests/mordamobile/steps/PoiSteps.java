package ru.yandex.autotests.mordamobile.steps;

import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordamobile.Properties;
import ru.yandex.autotests.mordamobile.pages.HomePage;
import ru.yandex.qatools.allure.annotations.Step;

import static ru.yandex.autotests.mordamobile.blocks.PoiBlock.PoiItem;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18.04.13
 */
public class PoiSteps {
    private static final Properties CONFIG = new Properties();

    private WebDriver driver;
    private HomePage homePage;
    public CommonMordaSteps userSteps;

    public PoiSteps(WebDriver driver) {
        this.driver = driver;
        userSteps = new CommonMordaSteps(driver);
        homePage = new HomePage(driver);
    }

    @Step
    public void shouldSeePoiItems() {
        for (PoiItem item : homePage.poiBlock.allItems) {
            userSteps.shouldSeeElement(item.icon);
        }
    }
}
