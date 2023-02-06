package ru.yandex.autotests.morda.tests.web.widgets.skins;

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
import ru.yandex.autotests.morda.tests.web.utils.SkinSteps;
import ru.yandex.autotests.morda.tests.web.utils.WidgetSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static ru.yandex.autotests.mordacommonsteps.utils.Mode.WIDGET;
import static ru.yandex.autotests.utils.morda.ParametrizationConverter.convert;
import static ru.yandex.autotests.utils.morda.users.UserType.DEFAULT;

/**
 * User: asamar
 * Date: 02.08.16
 */
@Aqua.Test(title = "Skins")
@Features({"Main", "Widget", "Skins"})
@Stories("Skins")
@RunWith(Parameterized.class)
public class SkinTest {
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
    private DesktopMainPage page;
    private PatternSteps patternSteps;
    private WidgetSteps widgetSteps;
    private static final String skinId = "yoda";
    private SkinSteps skinSteps;


    public SkinTest(DesktopMainMorda morda) {
        this.morda = morda;
        this.mordaAllureBaseRule = morda.getRule();
        this.driver = mordaAllureBaseRule.getDriver();
        this.user = new CommonMordaSteps(driver);
        this.page = morda.getPage(driver);
        this.patternSteps = new PatternSteps(driver);
        this.widgetSteps = new WidgetSteps(driver);
        this.skinSteps = new SkinSteps(driver);
    }

    @Before
    public void initialize() throws InterruptedException, IOException {
        morda.initialize(driver);
        user.logsInAs(mordaAllureBaseRule.getUser(DEFAULT, WIDGET),
                morda.getPassportUrl().toURL(),
                morda.getUrl().toString());
        patternSteps.setWidgetModeLogged(morda.getUrl().toString());
    }

    @Test
    public void setSkin(){
        skinSteps.setSkin(skinId,
                morda.getThemeUrl().toString(),
                mordaAllureBaseRule.getCaps().getBrowserName()
        );
    }

    @Test
    public void skinResetFromPanel(){
        skinSteps.setSkinWithUrl(morda.getThemeUrl() + skinId);
        skinSteps.shouldSeeSkinInBrowser(skinId, mordaAllureBaseRule.getCaps().getBrowserName());
        skinSteps.resetSkinFromPanel(morda.getThemeUrl().toString());
    }

    @Test
    public void skinResetFromMenu(){
        skinSteps.setSkinWithUrl(morda.getThemeUrl() + skinId);
        skinSteps.shouldSeeSkinInBrowser(skinId, mordaAllureBaseRule.getCaps().getBrowserName());
        skinSteps.resetSkinFromMenu();
    }
}
