package ru.yandex.autotests.mainmorda.widgettests.wdelete;

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

import java.util.Collection;

import static ru.yandex.autotests.mainmorda.data.WidgetsData.DEFAULT_NUMBER_OF_WIDGETS;
import static ru.yandex.autotests.mainmorda.data.WidgetsData.WidgetInfo;
import static ru.yandex.autotests.mordacommonsteps.utils.Mode.WIDGET;

/**
 * User: alex89
 * Date: 25.12.12
 */

@Aqua.Test(title = "Удаление добавленных виджетов в режиме редактирования")
@RunWith(Parameterized.class)
@Features({"Main", "Widget", "Delete Widget"})
public class DeletionOfInsertedWidgetInEditModeTest {
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
        return ParametrizationConverter.convert(WidgetsData.WIDGETS_FOR_ADDITIONS_FROM_CATALOG);
    }

    public DeletionOfInsertedWidgetInEditModeTest(WidgetInfo widget) {
        this.widget = widget;
    }

    @Before
    public void before() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        userMode.setMode(WIDGET, mordaAllureBaseRule);
        userWidget.addWidget(widget.getName());
        userWidget.shouldSeeWidgetWithId(widget.getWidgetId());
        userWidget.shouldSeeWidgetsInAmount(DEFAULT_NUMBER_OF_WIDGETS + 1);
    }

    /**
     * Удаляем добавленные виджеты в режиме редактирования
     */
    @Test
    public void deleteInsertedWidgetInEditMode() {
        userMode.setEditMode();
        userWidget.deleteWidget(widget);
        userWidget.shouldNotSeeWidgetWithId(widget.getWidgetId());
        userWidget.shouldSeeWidgetsInAmount(DEFAULT_NUMBER_OF_WIDGETS);
        userCatalog.shouldSeeAnchorOnTheEndOfCurrentUrl();
        userMode.saveSettings();
        userWidget.shouldSeeWidgetsInAmount(DEFAULT_NUMBER_OF_WIDGETS);
        userWidget.shouldNotSeeWidgetWithId(widget.getWidgetId());
    }
}
