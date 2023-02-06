package ru.yandex.autotests.morda.tests.web.common.clid;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.MordaType;
import ru.yandex.autotests.morda.pages.desktop.com.DesktopComMorda;
import ru.yandex.autotests.morda.pages.desktop.firefox.DesktopFirefoxMorda;
import ru.yandex.autotests.morda.pages.interfaces.blocks.BlockWithSearchForm;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithSearchBlock;
import ru.yandex.autotests.morda.pages.touch.ru.TouchRuMorda;
import ru.yandex.autotests.morda.tests.web.MordaWebTestsProperties;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.net.URI;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static javax.ws.rs.core.UriBuilder.fromUri;
import static org.hamcrest.Matchers.containsString;
import static ru.yandex.autotests.morda.pages.desktop.comtr.DesktopComTrMorda.desktopComTr;
import static ru.yandex.autotests.morda.pages.desktop.comtr.DesktopComTrMorda.desktopFamilyComTr;
import static ru.yandex.autotests.morda.pages.desktop.comtrfootball.DesktopComTrFootballMorda.desktopComTrBjk;
import static ru.yandex.autotests.morda.pages.desktop.comtrfootball.DesktopComTrFootballMorda.desktopComTrGs;
import static ru.yandex.autotests.morda.pages.desktop.comtrfootball.DesktopComTrFootballMorda.desktopFamilyComTrBjk;
import static ru.yandex.autotests.morda.pages.desktop.comtrfootball.DesktopComTrFootballMorda.desktopFamilyComTrGs;
import static ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda.desktopFamilyMain;
import static ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda.desktopMain;
import static ru.yandex.autotests.morda.pages.desktop.yaru.DesktopYaruMorda.desktopYaru;
import static ru.yandex.autotests.morda.pages.pda.com.PdaComMorda.pdaCom;
import static ru.yandex.autotests.morda.pages.pda.comtr.PdaComTrMorda.pdaComTr;
import static ru.yandex.autotests.morda.pages.pda.ru.PdaRuMorda.pdaRu;
import static ru.yandex.autotests.morda.pages.pda.yaru.PdaYaRuMorda.pdaYaRu;
import static ru.yandex.autotests.morda.pages.touch.com.TouchComMorda.touchCom;
import static ru.yandex.autotests.morda.pages.touch.comtr.TouchComTrMorda.touchComTr;
import static ru.yandex.autotests.morda.pages.touch.comtrwp.TouchComTrWpMorda.touchComTrWp;
import static ru.yandex.autotests.morda.pages.touch.ruwp.TouchRuWpMorda.touchRuWp;
import static ru.yandex.autotests.morda.steps.NavigationSteps.open;
import static ru.yandex.autotests.utils.morda.ParametrizationConverter.convert;
import static ru.yandex.autotests.utils.morda.region.Region.MOSCOW;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 28/02/15
 */
@Aqua.Test(title = "Clid is thrown to search")
@Features("Clid")
@Stories("Clid is thrown to search")
@RunWith(Parameterized.class)
public class ClidIsThrownToSearchTest {
    private static final MordaWebTestsProperties CONFIG = new MordaWebTestsProperties();

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        List<Morda<? extends PageWithSearchBlock<? extends BlockWithSearchForm>>> data = new ArrayList<>();

        String scheme = CONFIG.getMordaScheme();
        String environment = CONFIG.getMordaEnvironment();
        String userAgentTouchIphone = CONFIG.getMordaUserAgentTouchIphone();
        String userAgentTouchWp = CONFIG.getMordaUserAgentTouchWp();
        String userAgentPda = CONFIG.getMordaUserAgentPda();

        data.add(desktopMain(scheme, environment, MOSCOW));
        data.add(desktopFamilyMain(scheme, environment, MOSCOW));

        data.add(desktopYaru(scheme, environment));

        data.addAll(DesktopComMorda.getDefaultList(scheme, environment));

//        data.add(desktopFirefoxRu(scheme, environment, MOSCOW, RU));
//        data.add(desktopFirefoxUa(scheme, environment, MOSCOW, RU));
//        data.add(desktopFirefoxComTr(scheme, environment, MOSCOW));
        data.addAll(DesktopFirefoxMorda.getDefaultList(scheme, environment));

        data.add(desktopComTr(scheme, environment));
        data.add(desktopFamilyComTr(scheme, environment));

        data.add(desktopComTrBjk(scheme, environment));
        data.add(desktopComTrGs(scheme, environment));
        data.add(desktopFamilyComTrGs(scheme, environment));
        data.add(desktopFamilyComTrBjk(scheme, environment));

        data.addAll(TouchRuMorda.getDefaultList(scheme, environment, userAgentTouchIphone));
        data.add(touchComTr(scheme, environment, Region.ISTANBUL, userAgentTouchIphone));
        data.add(touchCom(scheme, environment, userAgentTouchIphone));
        data.add(touchRuWp(scheme, environment, userAgentTouchWp));
        data.add(touchComTrWp(scheme, environment, Region.ISTANBUL, userAgentTouchWp));

        data.add(pdaComTr(scheme, environment, userAgentPda));
        data.add(pdaCom(scheme, environment, userAgentPda));
        data.add(pdaRu(scheme, environment, userAgentPda));
        data.add(pdaYaRu(scheme, environment, userAgentPda));

        return convert(MordaType.filter(data, CONFIG.getMordaPagesToTest()));
    }

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;
    private WebDriver driver;
    private CommonMordaSteps user;
    private Morda<? extends PageWithSearchBlock<? extends BlockWithSearchForm>> morda;
    private PageWithSearchBlock<? extends BlockWithSearchForm> page;

    public ClidIsThrownToSearchTest(Morda<? extends PageWithSearchBlock<? extends BlockWithSearchForm>> morda) {
        this.morda = morda;
        this.mordaAllureBaseRule = this.morda.getRule();
        this.driver = mordaAllureBaseRule.getDriver();
        this.user = new CommonMordaSteps(driver);
        this.page = morda.getPage(driver);
    }

    @Before
    public void initialize() {
        morda.initialize(driver);
    }

    @Test
    public void clidIsThrownToSearch() {
        String clid = "123456";
        String request = "grumpy cat";
        URI clidURI = fromUri(morda.getUrl()).queryParam("clid", clid).build();

        open(driver, clidURI);

        user.shouldSeeElement(page.getSearchBlock());
        user.shouldSeeElement(page.getSearchBlock().getSearchInput());
        user.entersTextInInput(page.getSearchBlock().getSearchInput(), request);
        user.shouldSeeElement(page.getSearchBlock().getSearchButton());
        user.clicksOn(page.getSearchBlock().getSearchButton());

        user.shouldSeePage(containsString("clid=" + clid));
    }

}
