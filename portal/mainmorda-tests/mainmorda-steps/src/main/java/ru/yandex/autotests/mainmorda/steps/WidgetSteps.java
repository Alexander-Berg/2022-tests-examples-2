package ru.yandex.autotests.mainmorda.steps;

import org.hamcrest.MatcherAssert;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.Keys;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.interactions.Actions;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.blocks.Widget;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.utils.WidgetPattern;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.element.HtmlElement;
import ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.TimeUnit;

import static ch.lambdaj.Lambda.exists;
import static ch.lambdaj.Lambda.extract;
import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static ch.lambdaj.Lambda.selectFirst;
import static java.lang.Thread.sleep;
import static org.hamcrest.CoreMatchers.allOf;
import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.greaterThan;
import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.Matchers.is;
import static org.hamcrest.Matchers.notNullValue;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;
import static org.openqa.selenium.lift.Matchers.displayed;
import static ru.yandex.autotests.mainmorda.data.WidgetsData.TV;
import static ru.yandex.autotests.mainmorda.data.WidgetsData.WidgetInfo;
import static ru.yandex.autotests.mainmorda.utils.WidgetPatternParameter.WAUTH;
import static ru.yandex.autotests.mordacommonsteps.matchers.AlertAcceptedMatcher.isAlertAccepted;
import static ru.yandex.autotests.mordacommonsteps.matchers.WithWaitForMatcher.withWaitFor;
import static ru.yandex.qatools.matchers.collection.HasSameItemsAsListMatcher.hasSameItemsAsList;

/**
 * User: ivannik
 * Date: 05.07.13
 * Time: 17:33
 */
public class WidgetSteps {
    private static final Properties CONFIG = new Properties();
    private static final String EDIT_URL_PART = "/?edit=1";
    private static final long SCRIPT_TIMEOUT = 5000;

    private WebDriver driver;
    private CommonMordaSteps userSteps;
    private EtrainsSteps userEtrains;
    private ModeSteps userMode;
    private MainPage mainPage;

    public WidgetSteps(WebDriver driver) {
        this.driver = driver;
        this.userSteps = new CommonMordaSteps(driver);
        this.userEtrains = new EtrainsSteps(driver);
        this.userMode = new ModeSteps(driver);
        this.mainPage = new MainPage(driver);
    }

    private String getQuery() {
        return (String) ((JavascriptExecutor) driver).executeScript("return window.wg.getQueryForSave()");
    }

    @Step
    public void updatesAllWidgets() {
        driver.manage().timeouts().setScriptTimeout(SCRIPT_TIMEOUT, TimeUnit.MILLISECONDS);
        Boolean response = (Boolean)
                ((JavascriptExecutor) driver).executeAsyncScript(
                        "var rebindWidgets = Widget.Framework.all()\n" +
                                "        .filter(function(widget) {\n" +
                                "            return !!widget.params.rebind;\n" +
                                "        });\n" +
                                "var F = function (callback, expectedCount) {\n" +
                                "    var counter = 0;\n" +
                                "    return function () {\n" +
                                "        counter++;\n" +
                                "        if (counter >= expectedCount)\n" +
                                "            setTimeout(function () {callback(true);}, 1000);\n" +
                                "        }\n" +
                                "}(arguments[arguments.length - 1],\n" +
                                "    rebindWidgets.length);\n" +
                                "rebindWidgets.map(function(widget) {\n" +
                                "        widget.reload(F);\n" +
                                "    });"
                );
        assertTrue("Обновления виджетов не получены в течении " + SCRIPT_TIMEOUT + " мс", response);
    }

    @Step
    public void deleteWidget(WidgetInfo widgetInfo) {
        Widget widget = shouldSeeWidgetWithId(widgetInfo.getWidgetId());
        userSteps.shouldSeeElement(widget);
        userSteps.shouldSeeElement(widget.closeCross);
        userSteps.clicksOn(widget.closeCross);
    }

    @Step
    public void deleteWidget(WidgetInfo widgetInfo, WidgetPattern workPattern) {
        deleteWidget(widgetInfo);
        workPattern.deleteWidget(widgetInfo.getWidgetId());
    }

    @Step
    public Widget shouldSeeWidgetWithId(String widgetId) {
        try {
            sleep(1000);
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        }
        Widget widget = selectFirst(mainPage.widgets,
                having(on(Widget.class).getWidgetId(), equalTo(widgetId)));
        assertThat("Виджет " + widgetId + " не найден", widget, is(notNullValue()));
        return widget;
    }

    @Step
    public Widget shouldEditableSeeWidgetWithId(String widgetId) {
        Widget widget = selectFirst(mainPage.allEditableWidgets,
                allOf(having(on(Widget.class).getWidgetId(), equalTo(widgetId)), displayed()));
        assertThat("Виджет " + widgetId + " не найден", widget, is(notNullValue()));
        return widget;
    }

    @Step
    public void shouldNotSeeWidgetWithId(String widgetId) {
        assertFalse("Виджет " + widgetId + " присутствует на странице",
                exists(mainPage.widgets,
                        allOf(having(on(Widget.class).getWidgetId(), equalTo(widgetId)), displayed())));
    }

    @Step
    public void editsNewsBlock() {
        userSteps.shouldSeeElement(mainPage.newsBlock);
        userSteps.shouldSeeElement(mainPage.newsBlock.editIcon);
        userSteps.clicksOn(mainPage.newsBlock.editIcon);
        userSteps.shouldSeeElement(mainPage.newsSettings);
        userSteps.shouldSeeElement(mainPage.newsSettings.enumerationSelect);
        userSteps.clicksOn(mainPage.newsSettings.enumerationSelect);
        userSteps.selectOption(mainPage.newsSettings.enumerationSelect, (1));
        userSteps.shouldSeeElement(mainPage.newsSettings.okButton);
        userSteps.clicksOn(mainPage.newsSettings.okButton);
    }

    @Step
    public void editsNewsBlock(WidgetPattern workPattern) {
        String widgetId = mainPage.newsBlock.getWidgetId();
        editsNewsBlock();
        workPattern.setEditWidget(widgetId);
    }

    @Step
    public void saveSettings() {
        userMode.saveSettings();
    }

    @Step
    public void saveSettings(WidgetPattern workPattern) {
        userMode.saveSettings();
        workPattern.clearRemoved();
    }

    @Step
    public void addWidget(String widgetName) {
        userSteps.opensPage(CONFIG.getBaseURL() + "/?add=" + widgetName);
        acceptWidgetAddition();
    }

    @Step
    public void addWidget(String url, String widgetName) {
        userSteps.opensPage(url + "/?add=" + widgetName);
        acceptWidgetAddition();
    }

    @Step
    public void addWidgetWithoutAcception(String widgetName) {
        userSteps.opensPage(CONFIG.getBaseURL() + "/?add=" + widgetName);
    }

    @Step
    public void addWidgetInEditMode(String widgetName) {
        userSteps.opensPage(CONFIG.getBaseURL() + EDIT_URL_PART + "&add=" + widgetName);
        acceptWidgetAddition();
    }

    @Step
    public void addWidgetInEditModeWithoutAcception(String widgetName) {
        userSteps.opensPage(CONFIG.getBaseURL() + EDIT_URL_PART + "&add=" + widgetName);
    }

    @Step
    public void addWidgetInEditMode(String widgetName, WidgetPattern workPattern) {
        addWidgetInEditMode(widgetName);
        workPattern.addWidget(widgetName);
        workPattern.getParameters().put(WAUTH, WidgetPattern.getParameterValue(getQuery(), WAUTH));
    }

    @Step
    public void editTvWidget() {
        userSteps.shouldSeeElement(mainPage.tvBlock);
        userSteps.clicksOn(mainPage.tvBlock.editIcon);
        userSteps.shouldSeeElement(mainPage.tvSettings);
        userSteps.shouldSeeElement(mainPage.tvSettings.addAllChannelsButton);
        userSteps.clicksOn(mainPage.tvSettings.addAllChannelsButton);
        userSteps.shouldSeeElement(mainPage.tvSettings.okButton);
        userSteps.clicksOn(mainPage.tvSettings.okButton);
        userSteps.shouldNotSeeElement(mainPage.tvSettings);
    }

    @Step
    public void editTvWidget(WidgetPattern workPattern) {
        editTvWidget();
        workPattern.setEditWidget(TV.getWidgetId());
        workPattern.getParameters().put(WAUTH, WidgetPattern.getParameterValue(getQuery(), WAUTH));
    }

    @Step
    public void acceptWidgetAddition() {
        userSteps.shouldSeeElement(mainPage.addWidgetBalloon.addButton);
        userSteps.clicksOn(mainPage.addWidgetBalloon.addButton);
        userSteps.shouldNotSeeElement(mainPage.addWidgetBalloon);
    }

    @Step
    public void declineWidgetAddition() {
        userSteps.shouldSeeElement(mainPage.addWidgetBalloon.deleteButton);
        userSteps.clicksOn(mainPage.addWidgetBalloon.deleteButton);
        userSteps.shouldNotSeeElement(mainPage.addWidgetBalloon);
    }

    @Step
    public void opensWidgetSettings(Widget widget) {
        if (widget != null) {
            userSteps.shouldSeeElement(widget.editIcon);
            userSteps.clicksOn(widget.editIcon);
            userSteps.shouldSeeElement(mainPage.widgetSettings);
        }
    }

    @Step
    public void resetsSettingsOfWidget(WidgetInfo widget) {
        Widget widgetHtml = shouldSeeWidgetWithId(widget.getWidgetId());
        opensWidgetSettings(widgetHtml);
        userSteps.shouldSeeElement(mainPage.widgetSettings.resetSettingsButton);
        userSteps.clicksOn(mainPage.widgetSettings.resetSettingsButton);
        userSteps.shouldNotSeeElement(mainPage.widgetSettings);
    }

    @Step
    public void editsSettingsOfWidget(WidgetInfo widget) {
        Widget widgetHtml = shouldSeeWidgetWithId(widget.getWidgetId());
        opensWidgetSettings(widgetHtml);
        userSteps.shouldSeeElement(mainPage.widgetSettings.autoReloadCheckbox);
        userSteps.clicksOn(mainPage.widgetSettings.autoReloadCheckbox.input);
        userSteps.shouldSeeElement(mainPage.widgetSettings.okButton);
        userSteps.clicksOn(mainPage.widgetSettings.okButton);
        userSteps.shouldNotSeeElement(mainPage.widgetSettings);
    }

    @Step
    public void editsSettingsOfWidget(WidgetInfo widget, WidgetPattern workPattern) {
        editsSettingsOfWidget(widget);
        workPattern.setEditWidget(widget.getWidgetId());
    }

    public static List<String> getDisplayedWidgetsNames(List<Widget> widgets) {
        List<String> displayedWidgets = new ArrayList<String>();
        for (Widget widget : widgets) {
            if (widget.isDisplayed()) {
                displayedWidgets.add(widget.getWidgetName());
            }
        }
        return displayedWidgets;
    }

    @Step
    public void shouldSeeWidgetsInAmount(int amount) {
        assertThat("На морде не видно заданного количества виджетов!",
                getDisplayedWidgetsNames(mainPage.widgets),
                hasSize(amount));
    }

    @Step
    public void acceptWidgetDeletion() {
        userSteps.shouldSeeElement(mainPage.deleteWidgetBalloon.deleteButton);
        userSteps.clicksOn(mainPage.deleteWidgetBalloon.deleteButton);
        userSteps.shouldNotSeeElement(mainPage.deleteWidgetBalloon);
    }

    @Step
    public void declineWidgetDeletion() {
        userSteps.shouldSeeElement(mainPage.deleteWidgetBalloon.keepButton);
        userSteps.clicksOn(mainPage.deleteWidgetBalloon.keepButton);
        userSteps.shouldNotSeeElement(mainPage.deleteWidgetBalloon);
    }

    @Step
    public void approvesWidgetAdditionByPressingEnter() {
        userSteps.shouldSeeElement(mainPage.addWidgetBalloon.addButton);
        pressEnter();
        userSteps.shouldNotSeeElement(mainPage.addWidgetBalloon);
    }

    @Step
    public void pressEnter() {
        Actions builder = new Actions(driver);
        driver.switchTo().activeElement();
        builder.sendKeys(Keys.ENTER);
        builder.perform();
    }

    @Step
    public WidgetInfo addAnyWidgetFromRegBlock() {
        String widgetId;
        assertThat("В региональном блоке нет ссылок для добавления виджета!",
                mainPage.regionBlock.widgetLinks.size(), greaterThan(0));
        String href = mainPage.regionBlock.widgetLinks.get(0).getAttribute("href");
        widgetId = href.substring(href.indexOf("add=") + 4, href.indexOf("&"));
        mainPage.regionBlock.widgetLinks.get(0).click();
        return new WidgetInfo("Региональный виджет", widgetId);
    }

    @Step
    public void refreshesCurrentPageWithAlert() {
        driver.get(driver.getCurrentUrl());
        assertThat(driver,
                withWaitFor(isAlertAccepted()));
    }

    @Step
    public void cancelsWidgetAdditionByClickingAnywhere() {
        userSteps.shouldSeeElement(mainPage.addWidgetBalloon.deleteButton);
        userSteps.clicksOn(mainPage.veil);
        userSteps.shouldNotSeeElement(mainPage.addWidgetBalloon);
    }

    @Step
    public void clicksOnShareButtonForWidget(Widget widget) {
        userSteps.moveMouseOn(widget);
        userSteps.shouldSeeElement(widget.shareIcon);
        userSteps.clicksOn(widget.shareIcon);
    }

    @Step
    public void shouldSeeWidgets(List<WidgetInfo> expectedWidgets) {
        MatcherAssert.assertThat("На морде отображается неверный набор виджетов!",
                getDisplayedWidgetsNames(mainPage.widgets),
                hasSameItemsAsList(extract(expectedWidgets, on(WidgetInfo.class).getName())));
    }

    @Step
    public void clickOnResetButtonAndAcceptsAlert() {
        mainPage.widgetSettingsHeader.resetButton.click();
        assertThat(driver,
                withWaitFor(isAlertAccepted()));
    }

    @Step
    public void clickOnResetButtonAndRejectAlert() {
        mainPage.widgetSettingsHeader.resetButton.click();
//        waitForAlert(driver, ALERT_TIMEOUT);   //todo старый вейтер
        driver.switchTo().alert().dismiss();
    }

    @Step
    public void clickOnResetButtonAndShouldSeeAlertWithText(String expectedText) {
        mainPage.widgetSettingsHeader.resetButton.click();
//        waitForAlert(driver, ALERT_TIMEOUT);      //todo старый вейтер
        String alertText = driver.switchTo().alert().getText();
        assertThat("У алёрта сброса настроек некорректный текст!",
                alertText, equalTo(expectedText));
    }

    public void elementExists(HtmlElement element) {
        assertThat(element + " отсутствует в верстке страницы!", element,
                withWaitFor(WrapsElementMatchers.exists()));
    }
}
