package ru.yandex.autotests.morda.tests.web.common.skins;

import net.lightbody.bmp.core.har.HarEntry;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda;
import ru.yandex.autotests.morda.tests.web.MordaWebTestsProperties;
import ru.yandex.autotests.morda.tests.web.utils.SkinSteps;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.beans.themes.Theme;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.core.UriBuilder;
import java.net.URI;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.function.Predicate;

import static java.util.Collections.singletonList;
import static org.hamcrest.CoreMatchers.anyOf;
import static org.hamcrest.CoreMatchers.containsString;
import static org.junit.Assume.assumeThat;
import static org.openqa.selenium.remote.DesiredCapabilities.chrome;
import static ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda.desktopMain;
import static ru.yandex.autotests.morda.steps.NavigationSteps.open;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.THEMES;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.FF_34;
import static ru.yandex.autotests.mordacommonsteps.rules.proxy.actions.HarAction.addHar;
import static ru.yandex.autotests.utils.morda.region.Region.MOSCOW;

/**
 * User: asamar
 * Date: 27.07.16
 */
@Aqua.Test(title = "All skins chrome")
@RunWith(Parameterized.class)
@Features("Skins")
@Stories("Skins Actions")
public class AllSkinsChromeTest {
    private static final MordaWebTestsProperties CONFIG = new MordaWebTestsProperties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        List<Object[]> data = new ArrayList<>();
        URI mordaThemesUri = UriBuilder.fromUri("scheme://{env}yandex.ru/themes/")
                .scheme(CONFIG.getMordaScheme())
                .build(new Morda.MordaEnvironment("www", CONFIG.getMordaEnvironment(), true).parseEnvironment());

        Cleanvars cleanvars = new MordaClient(mordaThemesUri)
                .cleanvarsActions(MordaClient.getJsonEnabledClient())
                .get(FF_34, singletonList(THEMES));

        cleanvars.getThemes().getList().stream()
                .map(Theme::getId)
                .filter(skin -> !skin.equals("default") && !skin.equals("random"))
                .forEach(id ->
                                data.add(new Object[]{id})
                );

        return data;
    }

    private WebDriver driver;
    private CommonMordaSteps user;
    private SkinSteps userSkins;
    private DesktopMainMorda morda;
    private String id;

    public AllSkinsChromeTest(String id) {
        assumeThat("На девах не гоняем", CONFIG.getMordaEnvironment(),
                anyOf(containsString("rc"), containsString("production")));

        this.id = id;
        this.morda = desktopMain(CONFIG.getMordaScheme(), CONFIG.getMordaEnvironment(), MOSCOW);
        this.mordaAllureBaseRule = morda.getRule(chrome())
                .withProxyAction(addHar("skins_har"));
        this.driver = mordaAllureBaseRule.getDriver();
        this.user = new CommonMordaSteps(driver);
        this.userSkins = new SkinSteps(driver);

    }

    @Before
    public void init() {
        open(driver, morda.getThemeUrl() + id);
    }


    private final Predicate<HarEntry> EXCLUDE_XIVA =
            (harEntry) -> !harEntry.getRequest().getUrl().contains(
                            new Morda.MordaEnvironment("xiva", CONFIG.getMordaEnvironment(), false).parseEnvironment()
                            + "yandex.net");


    @Test
    public void skinStatic() throws Exception {
        userSkins.shouldSeeSkinInBrowser(id, mordaAllureBaseRule.getCaps().getBrowserName());
        userSkins.shouldSeeSkinResources(id);
        user.shouldSeeStaticIsDownloaded(mordaAllureBaseRule.getProxyServer().getHar(), EXCLUDE_XIVA);
    }
}
