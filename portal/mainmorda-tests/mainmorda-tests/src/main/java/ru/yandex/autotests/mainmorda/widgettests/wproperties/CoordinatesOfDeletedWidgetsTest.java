package ru.yandex.autotests.mainmorda.widgettests.wproperties;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.blocks.Widget;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mainmorda.steps.PatternsSteps;
import ru.yandex.autotests.mainmorda.steps.WidgetSteps;
import ru.yandex.autotests.mainmorda.utils.WidgetPattern;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static ru.yandex.autotests.mainmorda.data.WidgetsData.RANDOM_REGION_WIDGET;
import static ru.yandex.autotests.mordacommonsteps.utils.Mode.WIDGET;

/**
 * User: alex89
 * Date: 03.12.12
 * <p/>
 * Date: 15.01.13
 */

@Aqua.Test(title = "Координаты виджетов при сохранении паттерна  (при удалении одного из виджетов)")
@Features({"Main", "Widget", "Widget Properties"})
@Stories("Coordinates")
public class CoordinatesOfDeletedWidgetsTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private WidgetSteps userWidget = new WidgetSteps(driver);
    private PatternsSteps userPattern = new PatternsSteps(driver);
    private MainPage mainPage = new MainPage(driver);

    @Before
    public void before() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        userMode.setMode(WIDGET, mordaAllureBaseRule);
        userMode.setEditMode(CONFIG.getBaseURL());
    }

    /**
     * Режим редактирования: удаляем виджет, должен сформироваться паттерн, удаленный виджет помечен removed=
     */
    @Test
    public void coordinatesAreCorrectInCaseOfDeleteWidget() {
        WidgetPattern workPattern = userPattern.getPatternInEditMode();

        userWidget.deleteWidget(RANDOM_REGION_WIDGET, workPattern);

        userPattern.shouldSeePatternRequest(workPattern);
    }

    /**
     * Режим редактирования: удаляем виджет и отменяем удаление, должен сформироваться паттерн,
     * передаться координаты и usrCh
     */
    @Test
    public void coordinatesAreCorrectInCaseOfDeleteAndRestoreWidget() {
        WidgetPattern workPattern = userPattern.getPatternInEditMode();

        Widget widget = userWidget.shouldSeeWidgetWithId(RANDOM_REGION_WIDGET.getWidgetId());
        user.shouldSeeElement(widget);
        user.shouldSeeElement(widget.closeCross);
        user.clicksOn(widget.closeCross);
        user.shouldSeeElement(mainPage.widgetSettingsHeader.undoButton);
        user.clicksOn(mainPage.widgetSettingsHeader.undoButton);

        userPattern.shouldSeePatternRequest(workPattern);
    }
}
