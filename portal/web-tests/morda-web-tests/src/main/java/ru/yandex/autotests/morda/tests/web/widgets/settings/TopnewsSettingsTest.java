package ru.yandex.autotests.morda.tests.web.widgets.settings;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.pages.MordaType;
import ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda;
import ru.yandex.autotests.morda.pages.desktop.main.DesktopMainPage;
import ru.yandex.autotests.morda.pages.desktop.main.blocks.TopnewsBlock;
import ru.yandex.autotests.morda.pages.desktop.main.blocks.TopnewsSettingsBlock;
import ru.yandex.autotests.morda.tests.web.MordaWebTestsProperties;
import ru.yandex.autotests.morda.tests.web.utils.WidgetSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static org.junit.Assume.assumeFalse;
import static ru.yandex.autotests.morda.pages.desktop.main.blocks.TopnewsSettingsBlock.TopnewsRubricsType.SPORT;
import static ru.yandex.autotests.morda.steps.NavigationSteps.open;
import static ru.yandex.autotests.utils.morda.ParametrizationConverter.convert;
import static ru.yandex.autotests.utils.morda.region.Region.ASTANA;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 29/11/15
 */
@Aqua.Test(title = "Настройки виджета новостей")
@Features({"Main", "Widget", "Settings"})
@Stories("Topnews")
@RunWith(Parameterized.class)
public class TopnewsSettingsTest {
    private static final MordaWebTestsProperties CONFIG = new MordaWebTestsProperties();

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        List<DesktopMainMorda> data = new ArrayList<>();

        String scheme = CONFIG.getMordaScheme();
        String environment = CONFIG.getMordaEnvironment();

        data.addAll(DesktopMainMorda.getDefaultList(scheme, environment));
//        data.add(desktopMain(scheme, environment, MOSCOW, RU));
        return convert(MordaType.filter(data, CONFIG.getMordaPagesToTest()));
    }

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;
    private DesktopMainMorda morda;
    private WebDriver driver;
    private CommonMordaSteps user;
    private DesktopMainPage page;
    private WidgetSteps widgetSteps;

    public TopnewsSettingsTest(DesktopMainMorda morda) {
        this.morda = morda;
        this.mordaAllureBaseRule = this.morda.getRule();
        this.driver = mordaAllureBaseRule.getDriver();
        this.user = new CommonMordaSteps(driver);
        this.page = morda.getPage(driver);
        this.widgetSteps = new WidgetSteps(driver);
    }

    @Before
    public void initialize() {
        morda.initialize(driver);
        open(driver, morda.getEditUrl());
    }

    @Test
    public void hideNumbers() throws InterruptedException {
        TopnewsBlock topnewsBlock = page.getNewsBlock();

        topnewsBlock.setup()
                .showNumeration(false)
                .save();
        user.shouldNotSeeElement(topnewsBlock.topnewsSettingsBlock);

        widgetSteps.shouldNotSeeNumbers();

        page.getEditModeControls().saveSettings();

        widgetSteps.shouldNotSeeNumbers();
    }

    @Test
    public void numbersVisibleAgain() throws InterruptedException {
        TopnewsBlock topnewsBlock = page.getNewsBlock();

        topnewsBlock.setup()
                .showNumeration(false)
                .save();

        user.shouldNotSeeElement(topnewsBlock.topnewsSettingsBlock);

        widgetSteps.shouldNotSeeNumbers();

        topnewsBlock.setup()
                .showNumeration(true)
                .save();

        user.shouldNotSeeElement(topnewsBlock.topnewsSettingsBlock);

        widgetSteps.shouldSeeNumbers();

        page.getEditModeControls().saveSettings();

        widgetSteps.shouldSeeNumbers();
    }

    @Test
    public void sportRubric() {
        assumeFalse("В Астане нет настройки любимой рубрики", morda.getRegion().equals(ASTANA));
        TopnewsBlock topnewsBlock = page.getNewsBlock();

        topnewsBlock.setup()
                .sportRubric()
                .save();
        user.shouldNotSeeElement(topnewsBlock.topnewsSettingsBlock);

        widgetSteps.shouldSeeCustomRubric(SPORT, morda.getLanguage());

        page.getEditModeControls().saveSettings();

        widgetSteps.shouldSeeCustomRubric(SPORT, morda.getLanguage());

    }

    @Test
    public void autoUpdating() {
        TopnewsBlock topnewsBlock = page.getNewsBlock();

        topnewsBlock.setup()
                .autoUpdate(false)
                .save();
        user.shouldNotSeeElement(topnewsBlock.topnewsSettingsBlock);

        TopnewsSettingsBlock topnewsSettingsBlock = topnewsBlock.setup();
        topnewsSettingsBlock.autoUpdate.shouldNotBeChecked();
    }
}
