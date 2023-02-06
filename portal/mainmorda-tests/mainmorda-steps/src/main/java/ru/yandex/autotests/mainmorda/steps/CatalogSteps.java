package ru.yandex.autotests.mainmorda.steps;

import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.blocks.Widget;
import ru.yandex.autotests.mainmorda.blocks.WidgetInCatalog;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.pages.WCatalogPage;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.element.HtmlElement;
import ru.yandex.qatools.htmlelements.element.Link;

import java.util.ArrayList;
import java.util.List;

import static ch.lambdaj.Lambda.*;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.allOf;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.is;
import static org.junit.Assert.assertTrue;
import static org.junit.Assert.fail;
import static ru.yandex.autotests.mainmorda.data.WidgetsData.WidgetInfo;
import static ru.yandex.autotests.mordacommonsteps.matchers.ModeMatcher.inWidgetMode;
import static ru.yandex.autotests.mordacommonsteps.matchers.RegexMatcher.matches;
import static ru.yandex.autotests.mordacommonsteps.matchers.WithWaitForMatcher.withWaitFor;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.exists;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.isDisplayed;

/**
 * User: alex89
 * Date: 19.12.12
 * Шаги для работы с каталогом виджетом
 */
public class CatalogSteps {
    private static final Properties CONFIG = new Properties();

    private static final String EDIT_URL = CONFIG.getBaseURL() + "/?edit=1";
    private static final String W_CATALOG_URL = "https://widgets.yandex" + CONFIG.getBaseDomain() + "/";
    private static final String ANCHOR_PATTERN = "#([0-9a-zA-Z_\\-]+)";
    public static final int NUMBER_OF_PAGES_FOR_FIND = 13;
    public static final int NUMBER_OF_ATTEMPTS = 3;

    private WebDriver driver;
    private CommonMordaSteps userSteps;
    private MainPage mainPage;
    private WCatalogPage wCatalogPage;

    public CatalogSteps(WebDriver driver) {
        this.driver = driver;
        this.userSteps = new CommonMordaSteps(driver);
        this.mainPage = new MainPage(driver);
        this.wCatalogPage = new WCatalogPage(driver);
    }

    @Step
    public void addWidgetFromCatalog(String rubric, String widgetId) {
        userSteps.opensPage(W_CATALOG_URL + rubric + getConsumer(rubric));
        addWidgetFromCurrentCatalogPage(widgetId);
    }

    @Step
    public void addWidgetFromCatalog(String rubric, WidgetInfo widget) {
        userSteps.opensPage(W_CATALOG_URL + rubric + getConsumer(rubric));
        addWidgetFromCurrentCatalogPage(widget.getName());
    }

    private static String getConsumer(String rubric) {
        if (CONFIG.getMordaEnv().isProd()) {
            return "";
        }
        if (rubric.contains("yandex")) {
            return "&consumer=" + CONFIG.getMordaEnv();
        }
        return "/?consumer=" + CONFIG.getMordaEnv();
    }

    @Step
    public void addWidgetFromEditCatalog(String rubric, String widgetId) {
        userSteps.opensPage(EDIT_URL);
        opensEditCatalog();
        chooseEditCatalogRubric(rubric);
        addWidgetFromCurrentEditCatalogPage(widgetId);
    }

    @Step
    public void opensEditCatalog() {
        mainPage.widgetSettingsHeader.inCatalogWidgets.click();
        switchDriverToEditCatalog();
        assertThat(wCatalogPage.catalog, withWaitFor(allOf(exists(), isDisplayed())));
    }

    @Step
    public void chooseEditCatalogRubric(String rubric) {
        List<Link> rubrics = wCatalogPage.getEditCatalogRubricLink(rubric);
        assertThat("Не найдена рубрика " + rubric + "!", rubrics.size(), equalTo(1));
        rubrics.get(0).click();
    }

    @Step
    public void addWidgetFromCurrentCatalogPage(String widgetId) {
        addWidgetFromCurrentCatalogPageMethod(widgetId);
    }

    @Step
    public void addWidgetFromCurrentEditCatalogPage(String widgetId) {
        addWidgetFromCurrentCatalogPageMethod(widgetId);
        switchDriverToMainPage();
    }

    @Step
    public void shouldSeeAnchorOnTheEndOfCurrentUrl() {
        assertThat("В конце текущего урла нет якоря!",
                driver.getCurrentUrl(), matches("([^#]+)" + ANCHOR_PATTERN));
    }

    @Step
    public void shouldSeeCatalogButtonInWidgetWithText(WidgetInfo widget, String expectedText) {
        userSteps.shouldSeeListWithSize(mainPage.catalogButtonList, equalTo(1));
        Widget widgetFromPage =
                userSteps.shouldSeeElementInList(mainPage.widgets, on(Widget.class).getWidgetName(), equalTo(widget.getName()));
        userSteps.shouldSeeElement(widgetFromPage);
        userSteps.shouldSeeElement(widgetFromPage.catalogButton);
        userSteps.shouldSeeElementWithText(widgetFromPage.catalogButton, expectedText);
    }

    @Step
    public void shouldSeeCatalogButtonsOnPageInAmount(int expectedAmount) {
        assertThat("Кнопка возврата в каталог представленна в нужном количестве!",
                mainPage.catalogButtonList.size(), equalTo(expectedAmount));
    }

    @Step
    public void shouldSeeThatCatalogButtonLeadsToCatalogPage() {
        clicksOnCatalogButton();
        userSteps.shouldSeePage(W_CATALOG_URL);
    }

    @Step
    public void clicksOnCatalogButton() {
        userSteps.shouldSeeListWithSize(mainPage.catalogButtonList, equalTo(1));
        userSteps.shouldSeeElement(mainPage.catalogButtonList.get(0));
        userSteps.clicksOn(mainPage.catalogButtonList.get(0));
    }

    /*
    * Методы с click через js
     */
    @Step
    public void jsClicksOn(HtmlElement element) {
        ((JavascriptExecutor) driver).executeScript("arguments[0].click();", element);
    }

    @Step
    public void acceptWidgetAddition() {
        userSteps.shouldSeeElement(mainPage.addWidgetBalloon.addButton);
        jsClicksOn(mainPage.addWidgetBalloon.addButton);
        userSteps.shouldNotSeeElement(mainPage.addWidgetBalloon);
    }

    @Step
    public void declineWidgetAddition() {
        userSteps.shouldSeeElement(mainPage.addWidgetBalloon.deleteButton);
        jsClicksOn(mainPage.addWidgetBalloon.deleteButton);
        userSteps.shouldNotSeeElement(mainPage.addWidgetBalloon);
    }

    @Step
    public void saveSettings() {
        for (int cnt = 0; cnt < NUMBER_OF_ATTEMPTS; cnt++) {
            tryClick(mainPage.widgetSettingsHeader.saveButton);
            if (withWaitFor(is(inWidgetMode())).matches(driver)) {
                try {
                    Thread.sleep(500);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
                return;
            }
        }
        fail("Не удалось сохранить настройки, выставленные в режиме редактирования!");
    }

    private void tryClick(HtmlElement element) {
        if (withWaitFor(exists()).matches(element)) {
            ((JavascriptExecutor) driver).executeScript("arguments[0].click();", element);
        }
    }

    /*
    * Вспомогательные методы
    */
    private void switchDriverToEditCatalog() {
        driver.getTitle(); //нужно время, чтобы подождать
        driver.switchTo().frame(mainPage.catalogIframe);
        driver.getTitle();
    }

    private void switchDriverToMainPage() {
        driver.switchTo().defaultContent();
    }

    private boolean needLookingForWidgetOnNextPage(String widgetId) {
        return getCatalogWidgetsWithIdName(wCatalogPage.widgetsInCatalog, widgetId).size() == 0
                && exists().matches(wCatalogPage.next);
    }

    private void findPageWithWidgetId(String widgetId) throws InterruptedException {
        for (int cnt = 1; cnt <= NUMBER_OF_PAGES_FOR_FIND; cnt++) {
            if (needLookingForWidgetOnNextPage(widgetId)) {
                wCatalogPage.next.click();
                Thread.sleep(500);

                withWaitFor(allOf(exists(), isDisplayed())).matches(wCatalogPage.next);
            } else {
                break;
            }
        }
    }

    private void addWidgetFromCurrentCatalogPageMethod(String widgetId) {
        //todo нужен эксперимент: превратить в степгруппу
        try {
            Thread.sleep(500);
            withWaitFor(allOf(exists())).matches(wCatalogPage.next);
            System.out.println(exists().matches(wCatalogPage.next));

            findPageWithWidgetId(widgetId);

            List<WidgetInCatalog> targetWidget
                    = getCatalogWidgetsWithIdName(wCatalogPage.widgetsInCatalog, widgetId);
            assertTrue("Не получилось добавить виджет, т.к. виджета нет в каталоге (" + widgetId + ")",
                    targetWidget.size() > 0);
            targetWidget.get(0).click();
        } catch (Exception e) {
            throw new AssertionError("Не получилось добавить виджет без подтверждения!", e);
        }
    }

    private static List<WidgetInCatalog> getCatalogWidgetsWithIdName(List<WidgetInCatalog> widgets, String idName) {
        List<WidgetInCatalog> targetWidgets = new ArrayList<WidgetInCatalog>();
        for (WidgetInCatalog widget : widgets) {
            if (widget.getWidgetName().equals(idName)) {
                targetWidgets.add(widget);
            }
        }
        return targetWidgets;
    }
}




