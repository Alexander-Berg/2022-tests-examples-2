package ru.yandex.autotests.mordamobile.steps;

import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordacommonsteps.utils.LinkInfo;
import ru.yandex.autotests.mordamobile.pages.HomePage;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

import static org.junit.Assert.fail;
import static ru.yandex.autotests.mordamobile.data.MenuData.TabInfo;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 22.05.13
 */
public class MenuSteps {

    private WebDriver driver;
    private HomePage homePage;
    public CommonMordaSteps userSteps;

    public MenuSteps(WebDriver driver) {
        this.driver = driver;
        userSteps = new CommonMordaSteps(driver);
        homePage = new HomePage(driver);
    }

    @Step
    public HtmlElement findLinkOnPage(List<HtmlElement> list, LinkInfo link) {
        for (HtmlElement element : list) {
            if (link.text.matches(element.getText())) {
                return element;
            }
        }
        fail("Ссылка " + link.text + " не найдена!");
        return null;
    }

    @Step
    public void shouldSeeMenuLink(List<HtmlElement> list, TabInfo linkInfo) {
        HtmlElement link = findLinkOnPage(list, linkInfo);
        if (link != null) {
            userSteps.shouldSeeLinkLight(link, linkInfo);
        }
    }

    @Step
    public void shouldSeeMenuLinkRequestThrown(List<HtmlElement> list, TabInfo linkInfo) {
        HtmlElement link = findLinkOnPage(list, linkInfo);
        if (link != null) {
            userSteps.clicksOn(link);
            userSteps.shouldSeePage(linkInfo.getRequest());
        }
    }

}
