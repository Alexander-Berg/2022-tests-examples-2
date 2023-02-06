package ru.yandex.autotests.mainmorda.steps;

import org.hamcrest.Matchers;
import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.data.TabsData;
import ru.yandex.autotests.mainmorda.pages.BasePage;
import ru.yandex.autotests.mainmorda.utils.TabInfo;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordacommonsteps.utils.LinkInfo;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.ArrayList;
import java.util.List;

import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.everyItem;
import static org.hamcrest.Matchers.startsWith;
import static org.hamcrest.collection.IsIn.isIn;
import static org.junit.Assert.fail;
import static ru.yandex.autotests.mainmorda.blocks.PageBlock.TABS;
import static ru.yandex.autotests.mainmorda.data.TabsData.FAMILY_TABS_PARAMETER_MATCHER;
import static ru.yandex.autotests.mordabackend.utils.LinkUtils.addLink;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.utils.morda.matchers.LoginMatcher.isLogged;

/**
 * User: eoff
 * Date: 03.12.12
 */
public class TabSteps {
    private static final Properties CONFIG = new Properties();

    private WebDriver driver;
    private CommonMordaSteps userSteps;
    private BasePage basePage;
    private LinksSteps userLink;

    public TabSteps(WebDriver driver) {
        this.driver = driver;
        this.userSteps = new CommonMordaSteps(driver);
        this.basePage = new BasePage(driver);
        this.userLink = new LinksSteps(driver);
    }

    @Step
    public void shouldSeeTabRequestCorrectlyThrown(List<HtmlElement> tabs, TabInfo tabInfo) {
        HtmlElement tab = findTabOnPage(tabs, tabInfo);
        userSteps.entersTextInInput(basePage.search.input, TabsData.REQUEST);
        userSteps.shouldSeeElementMatchingTo(tab, hasAttribute(HREF, tabInfo.request));
        addLink(tab.getAttribute(HREF.getValue()), CONFIG.getBaseDomain().getCapital(), isLogged().matches(driver),
                CONFIG.getLang(), UserAgent.FF_34);
    }

    @Step
    public void shouldSeeTab(List<HtmlElement> tabs, TabInfo tabInfo) {
        HtmlElement tab = findTabOnPage(tabs, tabInfo);
        userSteps.shouldSeeElement(tab);
        userLink.shouldSeeLink(tab, tabInfo, TABS);
    }

    @Step
    public HtmlElement findTabOnPage(List<HtmlElement> list, TabInfo tab) {
        for (HtmlElement element : list) {
            if (tab.text.matches(element.getText())) {
                return element;
            }
        }
        fail("Не нашли соответствующего таба в списке табов");
        return new HtmlElement();
    }

    @Step
    public List<HtmlElement> getVisibleElements(List<HtmlElement> list) {
        List<HtmlElement> result = new ArrayList<HtmlElement>();
        for (HtmlElement element : list) {
            if (element.isDisplayed()) {
                result.add(element);
            }
        }
        return result;
    }

    @Step
    public void canSeeAllTabsRequired(List<HtmlElement> list, List<TabInfo> expectedTabs) {
        assertThat("Размеры списков не совпадают", list.size(), equalTo(expectedTabs.size()));
        List<String> elements = new ArrayList<String>();
        List<String> elementsExpected = new ArrayList<String>();
        for (TabInfo tab : expectedTabs) {
            System.out.println(tab.text.toString());
            elementsExpected.add(tab.text.toString().substring(1, tab.text.toString().length() - 1));

        }
        for (HtmlElement element : list) {
            System.out.println(element.getText());
            elements.add(element.getText());
        }
        System.out.println(elements);
        System.out.println(elementsExpected);
        assertThat("На морде лишний таб!", elements,
                everyItem(isIn(elementsExpected)));
        assertThat("Не все табы есть на морде!", elementsExpected,
                everyItem(isIn(elements)));
    }

    public void shouldSeeFamilyParameterThrown(List<HtmlElement> tabs, TabInfo tabInfo) {
        HtmlElement tab = findTabOnPage(tabs, tabInfo);
        userSteps.entersTextInInput(basePage.search.input, TabsData.REQUEST);
        userSteps.shouldSeeLinkLight(tab,
                new LinkInfo(tabInfo.text, Matchers.<String>allOf(
                        startsWith(tabInfo.baseSearchUrl),
                        FAMILY_TABS_PARAMETER_MATCHER),
                        hasAttribute(HREF, FAMILY_TABS_PARAMETER_MATCHER)));
        addLink(tab.getAttribute(HREF.getValue()), CONFIG.getBaseDomain().getCapital(), isLogged().matches(driver),
                CONFIG.getLang(), UserAgent.FF_34);
    }
}
