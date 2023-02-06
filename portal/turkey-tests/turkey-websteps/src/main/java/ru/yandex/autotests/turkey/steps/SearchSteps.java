package ru.yandex.autotests.turkey.steps;

import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordacommonsteps.utils.LinkInfo;
import ru.yandex.autotests.turkey.Properties;
import ru.yandex.autotests.turkey.pages.YandexComTrPage;
import ru.yandex.autotests.turkey.utils.TabInfo;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.allOf;
import static org.hamcrest.Matchers.anyOf;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.mordabackend.utils.LinkUtils.addLink;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.turkey.blocks.TabsBlock.Tab;
import static ru.yandex.autotests.turkey.data.SearchData.COM_TR_SEARCH_URL;
import static ru.yandex.autotests.turkey.data.SearchData.FAMILY_TABS_PARAMETER_MATCHER;
import static ru.yandex.autotests.turkey.data.SearchData.SEARCH_REQUEST;
import static ru.yandex.autotests.utils.morda.matchers.LoginMatcher.isLogged;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;

/**
 * User: leonsabr
 * Date: 05.10.12
 */
public class SearchSteps {
    private static final Properties CONFIG = new Properties();
    private WebDriver driver;
    private YandexComTrPage yandexComTrPage;


    public CommonMordaSteps userSteps;

    public SearchSteps(WebDriver driver) {
        this.driver = driver;
        userSteps = new CommonMordaSteps(driver);
        yandexComTrPage = new YandexComTrPage(driver);
    }

    @Step
    public void searchFor(String request) {
        userSteps.shouldSeeElement(yandexComTrPage.search.input);
        userSteps.entersTextInInput(yandexComTrPage.search.input, request);
        userSteps.clicksOn(yandexComTrPage.search.submit);
        userSteps.shouldSeePage(COM_TR_SEARCH_URL);
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
        userSteps.entersTextInInput(yandexComTrPage.search.input, SEARCH_REQUEST);
        userSteps.shouldSeeElementMatchingTo(tab, hasAttribute(HREF, tabInfo.request));
        addLink(tab.getAttribute(HREF.getValue()), CONFIG.getBaseDomain().getCapital(), isLogged().matches(driver),
                CONFIG.getLang(), UserAgent.FF_23);
    }

    @Step
    public void shouldSeeFamilyParameterThrown(List<Tab> tabs, TabInfo tabInfo) {
        Tab tab = userSteps.findFirst(tabs, on(Tab.class), hasText(tabInfo.text));
        userSteps.entersTextInInput(yandexComTrPage.search.input, SEARCH_REQUEST);
        userSteps.shouldSeeLinkLight(tab,
                new LinkInfo(
                        tabInfo.text,
                        allOf(anyOf(startsWith(tabInfo.baseSearchUrl), startsWith(tabInfo.alternativeSearchUrl),
                                        startsWith(tabInfo.imagesSearchUrl)),
                                FAMILY_TABS_PARAMETER_MATCHER)));
        addLink(tab.getAttribute(HREF.getValue()), CONFIG.getBaseDomain().getCapital(), isLogged().matches(driver),
                CONFIG.getLang(), UserAgent.FF_23);
    }
}
