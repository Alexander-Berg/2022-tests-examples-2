package ru.yandex.autotests.mainmorda.widgettests.wdelete;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.blocks.Widget;
import ru.yandex.autotests.mainmorda.data.WidgetsData;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.CatalogSteps;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mainmorda.steps.WidgetSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.Collection;

import static ru.yandex.autotests.mainmorda.data.WidgetsData.DEFAULT_NUMBER_OF_WIDGETS;
import static ru.yandex.autotests.mainmorda.data.WidgetsData.WidgetInfo;
import static ru.yandex.autotests.mordacommonsteps.utils.Mode.WIDGET;

/**
 * User: alex89
 * Date: 25.12.12
 */

@Aqua.Test(title = "Удаление добавленных виджетов")
@RunWith(Parameterized.class)
@Features({"Main", "Widget", "Delete Widget"})
public class DeletionOfInsertedWidgetTest {
    private static final Properties CONFIG = new Properties();
    private WidgetInfo widget;

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
        return ParametrizationConverter.convert(WidgetsData.WIDGETS_FOR_DELETE);
    }

    public DeletionOfInsertedWidgetTest(WidgetInfo widget) {
        this.widget = widget;
    }

    @Before
    public void before() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        userMode.setMode(WIDGET, mordaAllureBaseRule);
        userWidget.addWidget(widget.getName());
        userWidget.shouldSeeWidgetsInAmount(DEFAULT_NUMBER_OF_WIDGETS + 1);
    }

    /**
     * Удаляем добавленные виджеты с помощью появляющегося крестика
     */
    @Test
    public void deleteInsertedWidget() {
        Widget widgetHtml = userWidget.shouldSeeWidgetWithId(widget.getWidgetId());
        user.moveMouseOn(widgetHtml);
        userWidget.deleteWidget(widget);
        userWidget.acceptWidgetDeletion();

        userWidget.shouldNotSeeWidgetWithId(widget.getWidgetId());
        userWidget.shouldSeeWidgetsInAmount(DEFAULT_NUMBER_OF_WIDGETS);
        userCatalog.shouldSeeAnchorOnTheEndOfCurrentUrl();
        user.refreshPage();
        userWidget.shouldSeeWidgetsInAmount(DEFAULT_NUMBER_OF_WIDGETS);
        userWidget.shouldNotSeeWidgetWithId(widget.getWidgetId());
    }

    /**
     * Удаляем добавленные виджеты с помощью появляющегося url-a
     */
    @Test
    public void cancelDeletionOfInsertedWidget() {
        Widget widgetHtml = userWidget.shouldSeeWidgetWithId(widget.getWidgetId());
        user.moveMouseOn(widgetHtml);
        userWidget.deleteWidget(widget);
        userWidget.declineWidgetDeletion();

        userWidget.shouldSeeWidgetWithId(widget.getWidgetId());
        userWidget.shouldSeeWidgetsInAmount(DEFAULT_NUMBER_OF_WIDGETS + 1);
        userCatalog.shouldSeeAnchorOnTheEndOfCurrentUrl();
        user.refreshPage();
        userWidget.shouldSeeWidgetsInAmount(DEFAULT_NUMBER_OF_WIDGETS + 1);
        userWidget.shouldSeeWidgetWithId(widget.getWidgetId());
    }
}
