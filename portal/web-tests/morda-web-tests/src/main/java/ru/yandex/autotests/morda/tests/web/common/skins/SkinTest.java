package ru.yandex.autotests.morda.tests.web.common.skins;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.MordaType;
import ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda;
import ru.yandex.autotests.morda.pages.desktop.main.DesktopMainPage;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithServicesBlock;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.tests.web.MordaWebTestsProperties;
import ru.yandex.autotests.morda.tests.web.utils.SkinSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.net.MalformedURLException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static org.hamcrest.CoreMatchers.anyOf;
import static org.hamcrest.CoreMatchers.containsString;
import static org.junit.Assume.assumeThat;
import static ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda.desktopMain;
import static ru.yandex.autotests.mordacommonsteps.utils.Mode.WIDGET;
import static ru.yandex.autotests.utils.morda.ParametrizationConverter.convert;
import static ru.yandex.autotests.utils.morda.language.Language.RU;
import static ru.yandex.autotests.utils.morda.language.Language.UK;
import static ru.yandex.autotests.utils.morda.region.Region.KIEV;
import static ru.yandex.autotests.utils.morda.region.Region.MOSCOW;
import static ru.yandex.autotests.utils.morda.users.UserType.DEFAULT;

/**
 * User: asamar
 * Date: 27.11.2015.
 */
@Aqua.Test(title = "Reset/cancell/save skin")
@RunWith(Parameterized.class)
@Features("Skins")
@Stories("Skin Actions")
public class SkinTest {

    private static final MordaWebTestsProperties CONFIG = new MordaWebTestsProperties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;
    private WebDriver driver;


    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        List<Morda<? extends PageWithServicesBlock<? extends Validateable>>> data = new ArrayList<>();

        String scheme = CONFIG.getMordaScheme();
        String environment = CONFIG.getMordaEnvironment();

        data.add(desktopMain(scheme, environment, MOSCOW, RU));
        data.add(desktopMain(scheme, environment, KIEV, UK));

        return convert(MordaType.filter(data, CONFIG.getMordaPagesToTest()));
    }
    
    private DesktopMainMorda morda;
    private DesktopMainPage page;
    private CommonMordaSteps user;
    private SkinSteps skinSteps;
    private static final String skinId = "kyloren";

    public SkinTest(DesktopMainMorda morda) {
        assumeThat("На девах не гоняем", CONFIG.getMordaEnvironment(),
                anyOf(containsString("rc"), containsString("production")));

        this.mordaAllureBaseRule = morda.getRule();
        this.driver = mordaAllureBaseRule.getDriver();
        this.morda = morda;
        this.page = morda.getPage(driver);
        this.skinSteps = new SkinSteps(driver);
        this.user  = new CommonMordaSteps(driver);
    }

    @Before
    public void init() {
        morda.initialize(driver);
    }

    @Test
    public void skinSave() {
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

    @Test
    public void skinSaveInLoginMode() throws MalformedURLException {
        user.logsInAs(
                mordaAllureBaseRule.getUser(DEFAULT, WIDGET),
                morda.getPassportUrl().toURL(),
                morda.getUrl().toString()
        );
        skinSteps.setSkin(skinId,
                morda.getThemeUrl().toString(),
                mordaAllureBaseRule.getCaps().getBrowserName());
        skinSteps.resetSkins(morda.getThemeUrl().toString());
    }

    @Test
    public void skinResetFromPanelInLoginMode() throws MalformedURLException {
        user.logsInAs(
                mordaAllureBaseRule.getUser(DEFAULT, WIDGET),
                morda.getPassportUrl().toURL(),
                morda.getUrl().toString()
        );
        skinSteps.setSkinWithUrl(morda.getThemeUrl() + skinId);
        skinSteps.shouldSeeSkinInBrowser(skinId, mordaAllureBaseRule.getCaps().getBrowserName());
        skinSteps.resetSkinFromPanel(morda.getThemeUrl().toString());
    }

    @Test
    public void skinResetFromMenuInLoggedMode() throws MalformedURLException {
        user.logsInAs(
                mordaAllureBaseRule.getUser(DEFAULT, WIDGET),
                morda.getPassportUrl().toURL(),
                morda.getUrl().toString()
        );
        skinSteps.setSkinWithUrl(morda.getThemeUrl() + skinId);
        skinSteps.shouldSeeSkinInBrowser(skinId, mordaAllureBaseRule.getCaps().getBrowserName());
        skinSteps.resetSkinFromMenu();
    }

    @Test
    public void cancelAddingSkin() {
        skinSteps.opensThemeMenu(morda.getThemeUrl().toString() + skinId);
        skinSteps.shouldSeeSkinInBrowser(skinId, mordaAllureBaseRule.getCaps().getBrowserName());
        user.shouldSeeElement(page.getSkinsBlock().cancell);
        user.clicksOn(page.getSkinsBlock().cancell);
        user.shouldNotSeeElement(page.getSkinsBlock());
        skinSteps.shouldSeeDefaultMordaDesign();
    }

    @Test
    public void resetAddingSkin() {
        skinSteps.opensThemeMenu(morda.getThemeUrl().toString() + skinId);
        skinSteps.shouldSeeSkinInBrowser(skinId, mordaAllureBaseRule.getCaps().getBrowserName());
        user.shouldSeeElement(page.getSkinsBlock().reset);
        user.clicksOn(page.getSkinsBlock().reset);
        user.shouldNotSeeElement(page.getSkinsBlock());
        skinSteps.shouldSeeDefaultMordaDesign();
    }

}
