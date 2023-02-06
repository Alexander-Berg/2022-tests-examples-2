package ru.yandex.autotests.mordacom.steps;

import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordacom.Properties;
import ru.yandex.autotests.mordacom.pages.HomePage;
import ru.yandex.autotests.mordacom.utils.TabInfo;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordacommonsteps.utils.LinkInfo;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

import static ch.lambdaj.Lambda.on;
import static ru.yandex.autotests.mordabackend.utils.LinkUtils.addLink;
import static ru.yandex.autotests.mordacom.data.SearchData.COM_SEARCH_URL;
import static ru.yandex.autotests.mordacom.data.SearchData.SEARCH_REQUEST;
import static ru.yandex.autotests.mordacom.pages.TabsBlock.Tab;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.utils.morda.matchers.LoginMatcher.isLogged;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;

/**
 * User: leonsabr
 * Date: 05.10.12
 */
public class SearchSteps {
    private static final Properties CONFIG = new Properties();
    private WebDriver driver;
    private HomePage homePage;


    public CommonMordaSteps userSteps;

    public SearchSteps(WebDriver driver) {
        this.driver = driver;
        userSteps = new CommonMordaSteps(driver);
        homePage = new HomePage(driver);
    }

    @Step
    public void searchFor(String request) {
        userSteps.shouldSeeElement(homePage.search.input);
        userSteps.entersTextInInput(homePage.search.input, request);
        userSteps.clicksOn(homePage.search.submit);
        userSteps.shouldSeePage(COM_SEARCH_URL);
    }

    @Step
    public void shouldSeeTab404(List<HtmlElement> tabs, LinkInfo tabInfo) {
        HtmlElement tab = userSteps.findFirst(tabs, on(HtmlElement.class), hasText(tabInfo.text));
        userSteps.shouldSeeElement(tab);
        userSteps.shouldSeeLinkLight(tab, tabInfo);
    }

    @Step
    public void shouldSeeNewTab(List<Tab> tabs, TabInfo tabInfo) {
        Tab tab = userSteps.findFirst(tabs, on(Tab.class), hasText(tabInfo.text));
        userSteps.shouldSeeElement(tab);
        userSteps.shouldSeeElement(tab.icon);
        userSteps.shouldSeeLinkLight(tab, tabInfo);
    }

    @Step
    public void shouldSeeTabRequestCorrectlyThrown(List<Tab> tabs, TabInfo tabInfo) {
        Tab tab = userSteps.findFirst(tabs, on(Tab.class), hasText(tabInfo.text));
        userSteps.entersTextInInput(homePage.search.input, SEARCH_REQUEST);
        userSteps.shouldSeeElementMatchingTo(tab, hasAttribute(HREF, tabInfo.request));
        addLink(tab.getAttribute(HREF.getValue()), Region.MOSCOW, isLogged().matches(driver),
                null, UserAgent.FF_23);
    }
}
