package ru.yandex.autotests.mainmorda.widgettests.wproperties;

import org.hamcrest.Matcher;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mainmorda.steps.PatternsSteps;
import ru.yandex.autotests.mainmorda.steps.WidgetSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.Collection;

import static ru.yandex.autotests.mainmorda.data.CoordinatesData.AUTO_UPDATE_WIDGETS_FOR_DOMAINS;
import static ru.yandex.autotests.mainmorda.data.WidgetsData.WidgetInfo;
import static ru.yandex.autotests.mordacommonsteps.utils.Mode.WIDGET;

/**
 * User: alex89
 * Date: 06.12.12
 */

@Aqua.Test(title = "Автообновление блоков")
@RunWith(Parameterized.class)
@Features({"Main", "Widget", "Pattern"})
@Stories("Rebind")
public class RebindTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private PatternsSteps userPattern = new PatternsSteps(driver);
    private MainPage mainPage = new MainPage(driver);
    private WidgetSteps userWidget = new WidgetSteps(driver);

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> testData() {
        return ParametrizationConverter.convert(AUTO_UPDATE_WIDGETS_FOR_DOMAINS.get(CONFIG.getBaseDomain()));
    }

    private WidgetInfo widget;
    private Matcher<String> rebindValueMatcher;

    public RebindTest(WidgetInfo widget, Matcher<String> rebindValueMatcher) {
        this.widget = widget;
        this.rebindValueMatcher = rebindValueMatcher;
    }

    @Before
    public void before() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        userMode.setMode(WIDGET, mordaAllureBaseRule);
        userWidget.addWidget("_stocks");
        userMode.setEditMode(CONFIG.getBaseURL());
    }

    @Test
    public void rebindParameterIsCorrectForWidgets() {
        userPattern.shouldSeeRebindParameterInRequestForWidget(widget, rebindValueMatcher);
    }
}


