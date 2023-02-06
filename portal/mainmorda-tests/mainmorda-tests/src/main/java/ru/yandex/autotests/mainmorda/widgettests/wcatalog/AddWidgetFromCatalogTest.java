package ru.yandex.autotests.mainmorda.widgettests.wcatalog;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.data.WidgetsData;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.CatalogSteps;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mainmorda.steps.WidgetSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.Collection;

import static ru.yandex.autotests.mainmorda.data.WidgetsData.DEFAULT_NUMBER_OF_WIDGETS;
import static ru.yandex.autotests.mainmorda.data.WidgetsData.WidgetInfo;
import static ru.yandex.autotests.mordacommonsteps.utils.Mode.WIDGET;

/**
 * User: alex89
 * Date: 12.12.12
 */
@Aqua.Test(title = "Добавление виджета из каталога виджетов")
@RunWith(Parameterized.class)
@Features({"Main", "Widget", "Widget Catalog"})
@Stories("Add From Catalog")
public class AddWidgetFromCatalogTest {
    private static final Properties CONFIG = new Properties();
    private WidgetInfo widget;
    private String widgetRubric;

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private WidgetSteps userWidget = new WidgetSteps(driver);
    private CatalogSteps userCatalog = new CatalogSteps(driver);
    private MainPage mainPage = new MainPage(driver);

    @Parameterized.Parameters
    public static Collection<Object[]> testData() {
        return ParametrizationConverter.convert(WidgetsData.WIDGETS_FOR_ADDITIONS_FROM_CATALOG);
    }

    public AddWidgetFromCatalogTest(WidgetInfo widget) {
        this.widget = widget;
        widgetRubric = WidgetsData.getWidgetRubric(widget);
    }

    @Before
    public void before() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        userMode.setMode(WIDGET, mordaAllureBaseRule);
    }

    /**
     * Добавление виджета из Каталога Виджетов (фото rss, календарь, погода):
     * - добавляем виджет из каталога
     * - виджет добавился
     */
    @Test
    public void addWidgetFromCatalog() {
        userCatalog.addWidgetFromCatalog(widgetRubric, widget.getName());
        userWidget.acceptWidgetAddition();
        userWidget.shouldSeeWidgetWithId(widget.getWidgetId());
        userWidget.shouldSeeWidgetsInAmount(DEFAULT_NUMBER_OF_WIDGETS + 1);
        user.refreshPage();
        userWidget.shouldSeeWidgetWithId(widget.getWidgetId());
        userWidget.shouldSeeWidgetsInAmount(DEFAULT_NUMBER_OF_WIDGETS + 1);
        userCatalog.shouldSeeAnchorOnTheEndOfCurrentUrl();
    }

    /**
     * Добавить виджет из каталога виджетов, отменить добавление.<br>
     * После обновления на морде не должно быть виджета.
     */
    @Test
    public void cancelWidgetAdditionFromCatalog() {
        userCatalog.addWidgetFromCatalog(widgetRubric, widget.getName());
        userWidget.declineWidgetAddition();
        user.opensPage(CONFIG.getBaseURL());
        userWidget.shouldNotSeeWidgetWithId(widget.getWidgetId());
        userWidget.shouldSeeWidgetsInAmount(DEFAULT_NUMBER_OF_WIDGETS);
    }

    /**
     * Добавить виджет из каталога виджетов, нажав enter<br>
     * После обновления виджет должен остаться на морде
     */
    @Test
    public void addWidgetByEnterAfterRefresh() {
        userCatalog.addWidgetFromCatalog(widgetRubric, widget.getName());
        userWidget.approvesWidgetAdditionByPressingEnter();
        userWidget.shouldSeeWidgetWithId(widget.getWidgetId());
        userWidget.shouldSeeWidgetsInAmount(DEFAULT_NUMBER_OF_WIDGETS + 1);
        userCatalog.shouldSeeAnchorOnTheEndOfCurrentUrl();
        user.refreshPage();
        userWidget.shouldSeeWidgetWithId(widget.getWidgetId());
        userWidget.shouldSeeWidgetsInAmount(DEFAULT_NUMBER_OF_WIDGETS + 1);
    }

}