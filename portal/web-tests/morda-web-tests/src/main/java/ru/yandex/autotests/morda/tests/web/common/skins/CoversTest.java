package ru.yandex.autotests.morda.tests.web.common.skins;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda;
import ru.yandex.autotests.morda.tests.web.MordaWebTestsProperties;
import ru.yandex.autotests.morda.tests.web.utils.SkinSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordaexportsclient.beans.CoversV14Entry;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static org.hamcrest.CoreMatchers.anyOf;
import static org.hamcrest.CoreMatchers.containsString;
import static org.hamcrest.collection.IsIn.isOneOf;
import static org.junit.Assume.assumeThat;
import static ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda.desktopMain;
import static ru.yandex.autotests.morda.steps.NavigationSteps.open;
import static ru.yandex.autotests.mordacommonsteps.rules.proxy.actions.HarAction.addHar;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.COVERS_V14;
import static ru.yandex.autotests.mordaexportslib.ExportProvider.exports;
import static ru.yandex.autotests.mordaexportslib.matchers.DomainMatcher.domain;
import static ru.yandex.autotests.utils.morda.region.Region.MOSCOW;

/**
 * User: asamar
 * Date: 04.08.16
 */
@Aqua.Test(title = "Covers test")
@RunWith(Parameterized.class)
@Features("Skins")
@Stories("Covers test")
public class CoversTest {
    private static final MordaWebTestsProperties CONFIG = new MordaWebTestsProperties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        List<Object[]> data = new ArrayList<>();

        List<CoversV14Entry> covers = exports(COVERS_V14, domain(isOneOf("ru", "all", "kub", "kubr-ua")));

        covers.stream()
                .filter(e -> e.getDisabled() != 1)
                .map(CoversV14Entry::getIdEvent)
                .distinct()
                .forEach(id ->
                        data.add(new Object[]{id}));

        return data;
    }

    private WebDriver driver;
    private CommonMordaSteps user;
    private SkinSteps skinSteps;
    private static DesktopMainMorda morda = desktopMain(CONFIG.getMordaScheme(), CONFIG.getMordaEnvironment(), MOSCOW);
    private String id;

    public CoversTest(String id) {
        assumeThat("На девах не гоняем", CONFIG.getMordaEnvironment(),
                anyOf(containsString("rc"), containsString("production")));

        this.id = id;
        this.mordaAllureBaseRule = morda.getRule()
                .withProxyAction(addHar("covers_har"));
        this.driver = mordaAllureBaseRule.getDriver();
        this.user = new CommonMordaSteps(driver);
        this.skinSteps = new SkinSteps(driver);

    }

    @Before
    public void init() {
        open(driver, morda.getUrl() + "?cover=" + id);
    }

    @Test
    public void coverStatic() throws Exception {
        skinSteps.shouldSeeCoverInBrowser(id);
        skinSteps.shouldSeeCoverInResources(id);
        user.shouldSeeStaticIsDownloaded(mordaAllureBaseRule.getProxyServer().getHar());
    }
}
