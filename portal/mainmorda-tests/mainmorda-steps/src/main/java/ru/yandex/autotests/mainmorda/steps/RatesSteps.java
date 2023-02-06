package ru.yandex.autotests.mainmorda.steps;

import org.hamcrest.Matcher;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.data.RatesData;
import ru.yandex.autotests.mainmorda.pages.BasePage;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute;
import ru.yandex.autotests.mordacommonsteps.utils.LinkInfo;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.element.HtmlElement;
import ru.yandex.qatools.htmlelements.element.Select;

import java.util.ArrayList;
import java.util.List;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.everyItem;
import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.Matchers.isIn;
import static ru.yandex.autotests.mainmorda.blocks.PageBlock.RATES;
import static ru.yandex.autotests.mainmorda.matchers.RateCashMatcher.rateCashMatcher;
import static ru.yandex.autotests.mainmorda.matchers.RateCurrencyMatcher.rateCurrencyMatcher;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.qatools.htmlelements.matchers.common.DoesElementExistMatcher.exists;

/**
 * User: eoff
 * Date: 25.12.12
 */
public class RatesSteps {
    private static final Properties CONFIG = new Properties();

    private WebDriver driver;
    private CommonMordaSteps userSteps;
    private BasePage basePage;
    private MainPage mainPage;
    private ModeSteps userMode;
    private LinksSteps userLink;

    public RatesSteps(WebDriver driver) {
        this.driver = driver;
        this.userSteps = new CommonMordaSteps(driver);
        this.basePage = new BasePage(driver);
        this.mainPage = new MainPage(driver);
        this.userMode = new ModeSteps(driver);
        this.userLink = new LinksSteps(driver);
    }

    @Step
    public void shouldSeeRatesTitle(Matcher<String> title) {
        String allText = userSteps.getElementText(mainPage.ratesSettings.ratesTitle);
        assertThat("Неверный title котировок", allText.substring(0, allText.indexOf("\n")), title);
    }

    @Step
    public void shouldSeeOptionsNumberInSelect(Select select, int size) {
        assertThat("Неверное количество опций в селекторе", select.getOptions().size(), equalTo(size));
    }

    @Step
    public void shouldSeeRate(String rateName) {
        for (HtmlElement element : basePage.ratesBlock.ratesLinks) {
            userSteps.shouldSeeElementWithText(element, equalTo(rateName));
        }
    }

    @Step
    public String selectRandomRate() {
        userSteps.clicksOn(mainPage.ratesSettings.removeAllRatesButton);
        userSteps.selectRandomOption(mainPage.ratesSettings.selectRatesToAdd);
        String rate = mainPage.ratesSettings.selectRatesToAdd.getFirstSelectedOption().getText();
        userSteps.clicksOn(mainPage.ratesSettings.addOneRateButton);
        userSteps.selectOption(mainPage.ratesSettings.selectRatesToRemove, 0);
        userSteps.clicksOn(mainPage.ratesSettings.removeOneRateButton);
        return rate;
    }

    @Step
    public void shouldSeeRatesLink(List<HtmlElement> ratesLinks, int n, boolean isShort) {
        HtmlElement element = ratesLinks.get(n);
        userSteps.shouldSeeElement(element);
        String href = getHref(element);
        String textPattern = RatesData.getText(RatesData.getStocksId(href), isShort);
        System.out.println(href + " " + textPattern);
        LinkInfo info = new LinkInfo(
                equalTo(String.format(textPattern, element.getText())),
                equalTo(href),
                hasAttribute(HtmlAttribute.HREF, equalTo(href)));
        userLink.shouldSeeLink(element, info, RATES);
    }

    @Step
    public void shouldSeeDefaultRate(List<HtmlElement> ratesLinks, int n) {
        HtmlElement e = ratesLinks.get(n);
        String href = e.getAttribute(HtmlAttribute.HREF.toString());
        String stocksId = RatesData.getStocksId(href);
        assertThat("Данной котировки не должно быть в дефолтных!" + stocksId, stocksId, isIn(RatesData.DEFAULT_RATES));
    }

    @Step
    public void shouldSeeDefaultInlineRate(List<HtmlElement> ratesLinks, int n) {
        HtmlElement e = ratesLinks.get(n);
        String href = e.getAttribute(HtmlAttribute.HREF.toString());
        String stocksId = RatesData.getStocksId(href);
        assertThat("Данной котировки не должно быть в дефолтных!" + stocksId, stocksId, isIn(RatesData.DEFAULT_INLINE_RATES));
    }

    @Step
    public String getHref(HtmlElement element) {
        return element.getAttribute(HtmlAttribute.HREF.toString());
    }

    @Step
    public List<String> getHotRatesTexts() {
        List<String> result = new ArrayList<String>();
        for (WebElement element : basePage.ratesBlock.hotRates) {
            result.add(element.getText());
        }
        return result;
    }

    @Step
    public void shouldSeeHotRates(List<String> hotRates) {
        List<String> newHotRates = getHotRatesTexts();
        assertThat("У списка неверный размер", newHotRates, hasSize(hotRates.size()));
        assertThat("Какая-то опция не была горячей", newHotRates, everyItem(isIn(hotRates)));
    }

    @Step
    public void turnOffHighLightning() {
        userMode.setEditMode(CONFIG.getBaseURL());
        userSteps.shouldSeeElement(basePage.ratesBlock);
        userSteps.clicksOn(basePage.ratesBlock.editIcon);
        userSteps.shouldSeeElement(mainPage.ratesSettings);
        userSteps.deselectElement(mainPage.ratesSettings.highlightCheckbox);
        userSteps.clicksOn(mainPage.ratesSettings.okButton);
        userSteps.shouldSeeElement(mainPage.widgetSettingsHeader);
        userMode.saveSettings();
    }

    @Step
    public void turnOnHighLightning() {
        userMode.setEditMode(CONFIG.getBaseURL());
        userSteps.shouldSeeElement(basePage.ratesBlock);
        userSteps.clicksOn(basePage.ratesBlock.editIcon);
        userSteps.shouldSeeElement(mainPage.ratesSettings);
        userSteps.selectElement(mainPage.ratesSettings.highlightCheckbox);
        userSteps.clicksOn(mainPage.ratesSettings.okButton);
        userSteps.shouldSeeElement(mainPage.widgetSettingsHeader);
        userMode.saveSettings();
    }

    @Step
    public void shouldSeeRateNumerals() {
        assertThat(basePage.ratesBlock.ratesStringsCurrency,
                everyItem(rateCurrencyMatcher(basePage.ratesBlock.tomorrow)));
        assertThat(basePage.ratesBlock.ratesStringsCash,
                everyItem(rateCashMatcher()));
    }


    @Step
    public void tomorrowText() {
        if (exists().matches(basePage.ratesBlock.tomorrow)) {
            userSteps.shouldSeeElementWithText(basePage.ratesBlock.tomorrow,
                    RatesData.TOMORROW_BUY_TEXT);
        }
    }

}
