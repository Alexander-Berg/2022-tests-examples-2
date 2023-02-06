package ru.yandex.autotests.morda.tests.web.common.skins;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda;
import ru.yandex.autotests.morda.pages.desktop.main.widgets.SkinsBlock;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithSkinsBlock;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollectorRule;
import ru.yandex.autotests.morda.tests.web.MordaWebTestsProperties;
import ru.yandex.autotests.morda.tests.web.utils.SkinSteps;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.beans.themes.Theme;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;

import static ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda.desktopMain;
import static ru.yandex.autotests.utils.morda.language.Language.RU;

/**
 * User: asamar
 * Date: 02.12.2015.
 */
@Aqua.Test(title = "Share skin")
@Features("Skins")
@Stories("Skins Actions")
public class ShareSkinTest {
    private static final MordaWebTestsProperties CONFIG = new MordaWebTestsProperties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;

    private WebDriver driver;
    private Cleanvars cleanvars;
    private DesktopMainMorda morda;
    private PageWithSkinsBlock<SkinsBlock> page;
    private SkinSteps skinSteps;
    private HierarchicalErrorCollectorRule collectorRule;
    private String id;

    public ShareSkinTest() {
        this.morda = desktopMain(CONFIG.getMordaScheme(), CONFIG.getMordaEnvironment(), Region.SANKT_PETERBURG, RU);
        this.collectorRule = new HierarchicalErrorCollectorRule();
        this.mordaAllureBaseRule = morda.getRule().withRule(collectorRule);
        this.driver = mordaAllureBaseRule.getDriver();
        this.skinSteps = new SkinSteps(driver);
        this.page = morda.getPage(driver);
    }

    @Before
    public void init() {
        morda.initialize(driver);
        skinSteps.resetSkins(morda.getThemeUrl().toString());
        skinSteps.opensThemeMenu(morda.getThemeUrl().toString());

        String requestId = (String) ((JavascriptExecutor) driver)
                .executeScript("return document.getElementById('requestId').innerHTML");
        System.out.println(requestId);

        Client client = MordaClient.getJsonEnabledClient();
        cleanvars = client.target("http://morda-mocks.wdevx.yandex.ru/api/v1/dumps/" + requestId + "/cleanvars")
                .request()
                .buildGet()
                .invoke()
                .readEntity(Cleanvars.class);
        id = cleanvars.getThemes().getList().stream()
                .map(Theme::getId)
                .filter(skin -> !skin.equals("default") && !skin.equals("random"))
                .findAny()
                .get();
        skinSteps.clickSkinOnPanel(id);
    }

    @Test
    public void shareSkinTest() throws Exception {
        Validator<DesktopMainMorda> validator = new Validator<>(driver, morda).withCleanvars(cleanvars);

        collectorRule.getCollector()
                .check(page.getSkinsBlock().validateShareSkin(id, validator));
    }

}
