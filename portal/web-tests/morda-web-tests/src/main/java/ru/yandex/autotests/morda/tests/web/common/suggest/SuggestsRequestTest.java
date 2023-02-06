package ru.yandex.autotests.morda.tests.web.common.suggest;

import net.lightbody.bmp.core.har.HarEntry;
import net.lightbody.bmp.core.har.HarLog;
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
import ru.yandex.autotests.morda.pages.desktop.com404.Com404Morda;
import ru.yandex.autotests.morda.pages.desktop.firefox.DesktopFirefoxMorda;
import ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda;
import ru.yandex.autotests.morda.pages.interfaces.blocks.BlockWithSearchForm;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithSearchBlock;
import ru.yandex.autotests.morda.pages.touch.ru.TouchRuMorda;
import ru.yandex.autotests.morda.tests.web.MordaWebTestsProperties;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.function.Predicate;

import static org.hamcrest.MatcherAssert.assertThat;
import static ru.yandex.autotests.morda.pages.MordaType.T_RU;
import static ru.yandex.autotests.morda.pages.desktop.comtr.DesktopComTrMorda.desktopComTr;
import static ru.yandex.autotests.morda.pages.desktop.comtrfootball.DesktopComTrFootballMorda.desktopComTrBjk;
import static ru.yandex.autotests.morda.pages.desktop.comtrfootball.DesktopComTrFootballMorda.desktopComTrGs;
import static ru.yandex.autotests.morda.pages.desktop.comtrfootball.DesktopComTrFootballMorda.desktopFamilyComTrBjk;
import static ru.yandex.autotests.morda.pages.desktop.comtrfootball.DesktopComTrFootballMorda.desktopFamilyComTrGs;
import static ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda.desktopFamilyMain;
import static ru.yandex.autotests.morda.pages.desktop.yaru.DesktopYaruMorda.desktopYaru;
import static ru.yandex.autotests.morda.pages.touch.comtr.TouchComTrMorda.touchComTr;
import static ru.yandex.autotests.morda.pages.touch.comtrwp.TouchComTrWpMorda.touchComTrWp;
import static ru.yandex.autotests.morda.pages.touch.ruwp.TouchRuWpMorda.touchRuWp;
import static ru.yandex.autotests.morda.tests.web.utils.UrlValidator.getUrlMatcher;
import static ru.yandex.autotests.morda.utils.matchers.HarRequestMatcher.request;
import static ru.yandex.autotests.mordacommonsteps.rules.proxy.actions.HarAction.addHar;
import static ru.yandex.autotests.utils.morda.region.Region.MOSCOW;

/**
 * User: asamar
 * Date: 24.08.2015.
 */
@Aqua.Test(title = "Suggests request")
@Features("Suggest")
@Stories("Suggests request")
@RunWith(Parameterized.class)
public class SuggestsRequestTest {

    private static final MordaWebTestsProperties CONFIG = new MordaWebTestsProperties();

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        List<Morda<? extends PageWithSearchBlock<? extends BlockWithSearchForm>>> data = new ArrayList<>();

        String scheme = CONFIG.getMordaScheme();
        String environment = CONFIG.getMordaEnvironment();
        String userAgentTouchIphone = CONFIG.getMordaUserAgentTouchIphone();
        String userAgentTouchWp = CONFIG.getMordaUserAgentTouchWp();
        String userAgentPda = CONFIG.getMordaUserAgentPda();

        data.addAll(TouchRuMorda.getDefaultList(scheme, environment, userAgentTouchIphone));
        data.addAll(Com404Morda.getDefaultList(scheme, environment));
        data.addAll(DesktopMainMorda.getDefaultList(scheme, environment));
        data.add(desktopFamilyMain(scheme, environment, MOSCOW));
        data.add(desktopYaru(scheme, environment));
        data.addAll(DesktopComMorda.getDefaultList(scheme, environment));
        data.addAll(DesktopFirefoxMorda.getDefaultList(scheme, environment));
        data.add(desktopFamilyComTrBjk(scheme, environment));
        data.add(desktopComTr(scheme, environment));
        data.add(desktopComTrBjk(scheme, environment));
        data.add(desktopComTrGs(scheme, environment));
        data.add(desktopFamilyComTrGs(scheme, environment));
        data.add(desktopFamilyComTrBjk(scheme, environment));

        data.add(touchComTr(scheme, environment, Region.ISTANBUL, userAgentTouchIphone));
        data.add(touchRuWp(scheme, environment, userAgentTouchWp));
        data.add(touchComTrWp(scheme, environment, Region.ISTANBUL, userAgentTouchWp));


        return ParametrizationConverter.convert(MordaType.filter(data, CONFIG.getMordaPagesToTest()));
    }

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;


    private WebDriver driver;
    private CommonMordaSteps user;
    private Morda<? extends PageWithSearchBlock<? extends BlockWithSearchForm>> morda;

    public SuggestsRequestTest(Morda<? extends PageWithSearchBlock<? extends BlockWithSearchForm>> morda) {

        this.mordaAllureBaseRule = morda.getRule().withProxyAction(addHar("har"));
        this.driver = mordaAllureBaseRule.getDriver();
        this.user = new CommonMordaSteps(driver);
        this.morda = morda;
    }

    @Before
    public void setUp() {
        this.morda.initialize(driver);
    }

    @Test
    public void suggestAppears() throws InterruptedException {
        Predicate<HarEntry> predicate = entry -> entry.getRequest().getUrl().contains("suggest-ya.cgi");
        if (morda.getMordaType() == T_RU) {
            predicate = entry -> entry.getRequest().getUrl().contains("suggest-endings");
        }
        BlockWithSearchForm searchForm = morda.getPage(driver).getSearchBlock();
        user.appendsTextInInput(searchForm.getSearchInput(), "");
        mordaAllureBaseRule.getProxyServer().getHar().setLog(new HarLog());
        user.appendsTextInInput(searchForm.getSearchInput(), "a");
        assertThat(mordaAllureBaseRule.getProxyServer().getHar(),
                request(predicate, getUrlMatcher(morda)));
    }
}
