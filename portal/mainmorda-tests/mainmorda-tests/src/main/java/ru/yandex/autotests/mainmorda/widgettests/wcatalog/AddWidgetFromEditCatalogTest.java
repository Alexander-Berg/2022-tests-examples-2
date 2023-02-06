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
import static ru.yandex.autotests.mordacommonsteps.utils.Mode.WIDGET;

/**
 * User: alex89
 * Date: 12.12.12
 */
@Aqua.Test(title = "Добавление из каталога виджетов в режиме редактирования")
@RunWith(Parameterized.class)
@Features({"Main", "Widget", "Widget Catalog"})
@Stories("Add From Edit Catalog")
public class AddWidgetFromEditCatalogTest {
    private static final Properties CONFIG = new Properties();
    private WidgetsData.WidgetInfo widget;
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

    public AddWidgetFromEditCatalogTest(WidgetsData.WidgetInfo widget) {
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
    public void addWidgetFromEditCatalog() {
        userCatalog.addWidgetFromEditCatalog(widgetRubric, widget.getName());
        userCatalog.acceptWidgetAddition();
        userCatalog.shouldSeeAnchorOnTheEndOfCurrentUrl();
        userCatalog.saveSettings();
        userWidget.shouldSeeWidgetWithId(widget.getWidgetId());
        userWidget.shouldSeeWidgetsInAmount(DEFAULT_NUMBER_OF_WIDGETS + 1);
        user.refreshPage();
        userWidget.shouldSeeWidgetWithId(widget.getWidgetId());
        userWidget.shouldSeeWidgetsInAmount(DEFAULT_NUMBER_OF_WIDGETS + 1);
    }

    /**
     * Добавить виджет из каталога виджетов, отменить добавление.<br>
     * После обновления на морде не должно быть виджета.
     */
    @Test
    public void cancelWidgetAdditionFromEditCatalog() {
        userCatalog.addWidgetFromEditCatalog(widgetRubric, widget.getName());
        userCatalog.declineWidgetAddition();
        userCatalog.shouldSeeAnchorOnTheEndOfCurrentUrl();
        userCatalog.saveSettings();
        userWidget.shouldNotSeeWidgetWithId(widget.getWidgetId());
        userWidget.shouldSeeWidgetsInAmount(DEFAULT_NUMBER_OF_WIDGETS);
        user.refreshPage();
        userWidget.shouldNotSeeWidgetWithId(widget.getWidgetId());
        userWidget.shouldSeeWidgetsInAmount(DEFAULT_NUMBER_OF_WIDGETS);
    }
}