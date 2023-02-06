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
import ru.yandex.autotests.morda.pages.interfaces.blocks.BlockWithSetHomeLink;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithSetHomeBlock;
import ru.yandex.autotests.morda.tests.web.MordaWebTestsProperties;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.net.URI;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static javax.ws.rs.core.UriBuilder.fromUri;
import static ru.yandex.autotests.morda.pages.desktop.comtr.DesktopComTrMorda.desktopComTr;
import static ru.yandex.autotests.morda.pages.desktop.comtr.DesktopComTrMorda.desktopFamilyComTr;
import static ru.yandex.autotests.morda.pages.desktop.comtrfootball.DesktopComTrFootballMorda.desktopComTrBjk;
import static ru.yandex.autotests.morda.pages.desktop.comtrfootball.DesktopComTrFootballMorda.desktopComTrGs;
import static ru.yandex.autotests.morda.pages.desktop.comtrfootball.DesktopComTrFootballMorda.desktopFamilyComTrBjk;
import static ru.yandex.autotests.morda.pages.desktop.comtrfootball.DesktopComTrFootballMorda.desktopFamilyComTrGs;
import static ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda.desktopFamilyMain;
import static ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda.desktopMain;
import static ru.yandex.autotests.morda.steps.NavigationSteps.open;
import static ru.yandex.autotests.utils.morda.ParametrizationConverter.convert;
import static ru.yandex.autotests.utils.morda.region.Region.MOSCOW;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 28/02/15
 */
@Aqua.Test(title = "Clid hides set home link")
@Features("Clid")
@Stories("Clid hides set home link")
@RunWith(Parameterized.class)
public class ClidHidesSetHomeTest {
    private static final MordaWebTestsProperties CONFIG = new MordaWebTestsProperties();

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        List<Morda<? extends PageWithSetHomeBlock<? extends BlockWithSetHomeLink>>> data = new ArrayList<>();

        String scheme = CONFIG.getMordaScheme();
        String environment = CONFIG.getMordaEnvironment();

        data.add(desktopMain(scheme, environment, MOSCOW));
        data.add(desktopFamilyMain(scheme, environment, MOSCOW));

        data.add(desktopComTr(scheme, environment));
        data.add(desktopFamilyComTr(scheme, environment));

        data.add(desktopComTrBjk(scheme, environment));
        data.add(desktopComTrGs(scheme, environment));
        data.add(desktopFamilyComTrGs(scheme, environment));
        data.add(desktopFamilyComTrBjk(scheme, environment));

        return convert(MordaType.filter(data, CONFIG.getMordaPagesToTest()));
    }

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;
    private WebDriver driver;
    private CommonMordaSteps user;
    private Morda<? extends PageWithSetHomeBlock<? extends BlockWithSetHomeLink>> morda;
    private PageWithSetHomeBlock<? extends BlockWithSetHomeLink> page;

    public ClidHidesSetHomeTest(Morda<? extends PageWithSetHomeBlock<? extends BlockWithSetHomeLink>> morda) {
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
    public void setHomeIsHiddenWithGoodClid() {
        String clid = "1996099";
        URI clidURI = fromUri(morda.getUrl()).queryParam("clid", clid).build();

        open(driver, clidURI);

        user.shouldNotSeeElement(page.getSetHomeBlock());
    }

    @Test
    public void setHomeIsNotHiddenWithBadClid() {
        String clid = "123456";
        URI clidURI = fromUri(morda.getUrl()).queryParam("clid", clid).build();

        open(driver, clidURI);

        user.shouldSeeElement(page.getSetHomeBlock());
    }

}
