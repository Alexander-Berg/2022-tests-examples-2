package ru.yandex.autotests.morda.tests.web.widgets.pattern;

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
import ru.yandex.autotests.morda.tests.web.MordaWebTestsProperties;
import ru.yandex.autotests.morda.tests.web.utils.PatternSteps;
import ru.yandex.autotests.morda.tests.web.utils.WidgetSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static ru.yandex.autotests.morda.steps.NavigationSteps.open;
import static ru.yandex.autotests.morda.tests.web.utils.WidgetSteps.rssBlockUrl;
import static ru.yandex.autotests.mordacommonsteps.utils.Mode.WIDGET;
import static ru.yandex.autotests.utils.morda.ParametrizationConverter.convert;
import static ru.yandex.autotests.utils.morda.users.UserType.DEFAULT;

/**
 * User: asamar
 * Date: 29.02.16
 */
@Aqua.Test(title = "Cancel pattern")
@Features({"Main", "Widget", "Pattern"})
@Stories("Cancel pattern")
@RunWith(Parameterized.class)
public class CancelPatternTest {

    private static final MordaWebTestsProperties CONFIG = new MordaWebTestsProperties();


    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        List<DesktopMainMorda> data = new ArrayList<>();

        String scheme = CONFIG.getMordaScheme();
        String environment = CONFIG.getMordaEnvironment();

        data.addAll(DesktopMainMorda.getDefaultList(scheme, environment));
//        data.add(desktopMain(scheme, environment, SANKT_PETERBURG));

        return convert(MordaType.filter(data, CONFIG.getMordaPagesToTest()));
    }

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;
    private DesktopMainMorda morda;
    private WebDriver driver;
    private CommonMordaSteps user;
    private DesktopMainPage page;
    private PatternSteps patternSteps;
    private WidgetSteps widgetSteps;

    public CancelPatternTest(DesktopMainMorda morda) {
        this.morda = morda;
        this.mordaAllureBaseRule = this.morda.getRule();
        this.driver = mordaAllureBaseRule.getDriver();
        this.user = new CommonMordaSteps(driver);
        this.page = morda.getPage(driver);
        this.patternSteps = new PatternSteps(driver);
        this.widgetSteps = new WidgetSteps(driver);
    }

    @Before
    public void initialize() throws InterruptedException, IOException {
        morda.initialize(driver);
        user.logsInAs(mordaAllureBaseRule.getUser(DEFAULT, WIDGET),
                morda.getPassportUrl().toURL(),
                morda.getUrl().toString());
        patternSteps.setPlainModeLogged(morda.getUrl().toString());
    }

    @Test
    public void cancellPatternByResetSettings() throws IOException, InterruptedException {
        open(driver, rssBlockUrl(morda.getEditUrl()));

        page.getRssBlock().widgetAddControls.acceptAddition();

        page.getNewsBlock().widgetControls.removeWidget();

        page.getTvBlock().setup()
                .sevenChannels()
                .save();

        widgetSteps.resetSettings();
        patternSteps.shouldSeePlainPatternMeta();
    }

    @Test
    public void cancellPatternByCancelSettings() throws IOException {

        open(driver, rssBlockUrl(morda.getEditUrl()));
//        page.getRssBlock().widgetAddControls.acceptAddition();
        widgetSteps.acceptAddition(page.getRssBlock());

        page.getNewsBlock().widgetControls.removeWidget();

        page.getTvBlock().setup()
                .sevenChannels()
                .save();

        page.getEditModeControls().cancelSettings();
//        user.refreshPage();
        patternSteps.shouldSeePlainPatternMeta();
    }

//    @Test
    public void cancellPatternByUndoDeletionAndSave() throws IOException {
        open(driver, morda.getEditUrl());
        page.getNewsBlock().widgetControls.removeWidget();
        page.getEditModeControls().undoDeletion();
        page.getEditModeControls().saveSettings();
        user.refreshPage();
        patternSteps.shouldSeePlainPattern();
    }

}
