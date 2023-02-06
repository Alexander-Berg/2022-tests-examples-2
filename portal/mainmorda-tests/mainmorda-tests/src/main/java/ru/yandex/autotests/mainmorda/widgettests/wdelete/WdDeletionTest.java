package ru.yandex.autotests.mainmorda.widgettests.wdelete;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.CatalogSteps;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mainmorda.steps.WidgetSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;

import static ru.yandex.autotests.mainmorda.data.WidgetsData.DEFAULT_NUMBER_OF_WIDGETS;
import static ru.yandex.autotests.mainmorda.data.WidgetsData.SHUFFLED_DEFAULT_WIDGETS;
import static ru.yandex.autotests.mordacommonsteps.utils.Mode.WIDGET;

/**
 * User: alex89
 * Date: 12.04.12
 * Проверка удаления виджетов по-умолчанию в режиме редактирования
 * Проверка отмены удаления виджетов по-умолчанию в режиме редактирования
 */
@Aqua.Test(title = "Удаление Виджетов по-умолчанию в режиме редактирования")
@Features({"Main", "Widget", "Delete Widget"})
public class WdDeletionTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private WidgetSteps userWidget = new WidgetSteps(driver);
    private CatalogSteps userCatalog = new CatalogSteps(driver);
    private MainPage mainPage = new MainPage(driver);

    @Before
    public void before() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        userMode.setMode(WIDGET, mordaAllureBaseRule);
        userWidget.shouldSeeWidgetsInAmount(DEFAULT_NUMBER_OF_WIDGETS);
        userMode.setEditMode();
    }

    @Test
    public void deletionOfDefaultWidgets() {
        userWidget.deleteWidget(SHUFFLED_DEFAULT_WIDGETS.get(0));
        userWidget.shouldSeeWidgetsInAmount(DEFAULT_NUMBER_OF_WIDGETS - 1);
        userWidget.shouldNotSeeWidgetWithId(SHUFFLED_DEFAULT_WIDGETS.get(0).getWidgetId());
        userCatalog.shouldSeeAnchorOnTheEndOfCurrentUrl();

        userWidget.deleteWidget(SHUFFLED_DEFAULT_WIDGETS.get(1));
        userWidget.shouldSeeWidgetsInAmount(DEFAULT_NUMBER_OF_WIDGETS - 2);
        userWidget.shouldNotSeeWidgetWithId(SHUFFLED_DEFAULT_WIDGETS.get(1).getWidgetId());
        userCatalog.shouldSeeAnchorOnTheEndOfCurrentUrl();

        userMode.saveSettings();
        userWidget.shouldSeeWidgetsInAmount(DEFAULT_NUMBER_OF_WIDGETS - 2);
        userWidget.shouldNotSeeWidgetWithId(SHUFFLED_DEFAULT_WIDGETS.get(0).getWidgetId());
        userWidget.shouldNotSeeWidgetWithId(SHUFFLED_DEFAULT_WIDGETS.get(1).getWidgetId());
    }

    /**
     * Проверка отмены удаления виджета. Виджет должен стать снова видимым.
     */
    @Test
    public void cancelDeletionOfDefaultWidget() {
        userWidget.deleteWidget(SHUFFLED_DEFAULT_WIDGETS.get(0));
        userWidget.deleteWidget(SHUFFLED_DEFAULT_WIDGETS.get(1));

        user.shouldSeeElement(mainPage.widgetSettingsHeader.undoButton);
        user.clicksOn(mainPage.widgetSettingsHeader.undoButton);
        userWidget.shouldSeeWidgetsInAmount(DEFAULT_NUMBER_OF_WIDGETS - 1);
        userWidget.shouldSeeWidgetWithId(SHUFFLED_DEFAULT_WIDGETS.get(1).getWidgetId());
        userCatalog.shouldSeeAnchorOnTheEndOfCurrentUrl();

        user.shouldSeeElement(mainPage.widgetSettingsHeader.undoButton);
        user.clicksOn(mainPage.widgetSettingsHeader.undoButton);
        userWidget.shouldSeeWidgetsInAmount(DEFAULT_NUMBER_OF_WIDGETS);
        userWidget.shouldSeeWidgetWithId(SHUFFLED_DEFAULT_WIDGETS.get(0).getWidgetId());
        userCatalog.shouldSeeAnchorOnTheEndOfCurrentUrl();
        user.shouldNotSeeElement(mainPage.widgetSettingsHeader.undoButton);

        userMode.saveSettings();
        userWidget.shouldSeeWidgetsInAmount(DEFAULT_NUMBER_OF_WIDGETS);
    }
}
