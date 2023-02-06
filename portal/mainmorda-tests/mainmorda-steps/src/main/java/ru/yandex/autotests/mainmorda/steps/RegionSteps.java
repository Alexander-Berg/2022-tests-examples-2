package ru.yandex.autotests.mainmorda.steps;

import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.mainmorda.data.RegionBlockData;
import ru.yandex.autotests.mainmorda.pages.BasePage;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

/**
 * User: alex89
 * Date: 25.05.12
 */
public class RegionSteps {

    private WebDriver driver;
    private CommonMordaSteps userSteps;
    private BasePage basePage;

    public RegionSteps(WebDriver driver) {
        this.driver = driver;
        this.userSteps = new CommonMordaSteps(driver);
        this.basePage = new BasePage(driver);
    }

    @Step
    public void regionWidgetLinks() {
        for (HtmlElement link : basePage.regionBlock.widgetLinks) {
            userSteps.shouldSeeLinkLight(link, RegionBlockData.LINK);
        }
    }
}