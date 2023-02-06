package ru.yandex.autotests.morda.tests.web.widgets.actions;

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
import ru.yandex.autotests.morda.pages.desktop.main.blocks.RssBlock;
import ru.yandex.autotests.morda.pages.desktop.main.blocks.RssSettingsBlock;
import ru.yandex.autotests.morda.tests.web.MordaWebTestsProperties;
import ru.yandex.autotests.morda.tests.web.utils.WidgetSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static ru.yandex.autotests.morda.steps.NavigationSteps.open;
import static ru.yandex.autotests.morda.tests.web.utils.WidgetSteps.rssBlockUrl;
import static ru.yandex.autotests.utils.morda.ParametrizationConverter.convert;

/**
 * User: asamar
 * Date: 02.08.16
 */
@Aqua.Test(title = "Cancel settings")
@Features({"Main", "Widget", "Cancel settings"})
@Stories("Cancel settings")
@RunWith(Parameterized.class)
public class CancelSettingsTest {
    private static final MordaWebTestsProperties CONFIG = new MordaWebTestsProperties();

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        List<DesktopMainMorda> data = new ArrayList<>();

        String scheme = CONFIG.getMordaScheme();
        String environment = CONFIG.getMordaEnvironment();

        data.addAll(DesktopMainMorda.getDefaultList(scheme, environment));
        return convert(MordaType.filter(data, CONFIG.getMordaPagesToTest()));
    }

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;
    private DesktopMainMorda morda;
    private WebDriver driver;
    private CommonMordaSteps user;
    private WidgetSteps widgetSteps;
    private DesktopMainPage page;

    public CancelSettingsTest(DesktopMainMorda morda) {
        this.morda = morda;
        this.mordaAllureBaseRule = this.morda.getRule();
        this.driver = mordaAllureBaseRule.getDriver();
        this.user = new CommonMordaSteps(driver);
        this.page = morda.getPage(driver);
        this.widgetSteps = new WidgetSteps(driver);
    }

    @Before
    public void init(){
        morda.initialize(driver);
    }

    @Test
    public void cancelDefaultWidgetSettings(){
        open(driver, morda.getEditUrl());

        page.getNewsBlock().setup()
                .showNumeration(false)
                .cancel();
        widgetSteps.shouldSeeNumbers();

        page.getEditModeControls().saveSettings();
        widgetSteps.shouldSeeNumbers();
    }

    @Test
    public void cancelRssWidgetSettings(){
        open(driver, rssBlockUrl(morda.getEditUrl()));

        RssBlock rssBlock = page.getRssBlock();
        widgetSteps.acceptAddition(rssBlock);

        rssBlock.setup()
                .showTitleOnly(false)
                .cancel();

        RssSettingsBlock rssSettingsBlock = rssBlock.setup();
        rssSettingsBlock.showTitleOnlyCheckBox.shouldBeChecked();
    }
}
