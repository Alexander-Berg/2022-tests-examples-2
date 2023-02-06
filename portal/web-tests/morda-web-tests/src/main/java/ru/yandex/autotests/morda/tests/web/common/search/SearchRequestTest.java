package ru.yandex.autotests.morda.tests.web.common.search;

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
import ru.yandex.autotests.morda.tests.web.MordaWebTestsProperties;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static org.hamcrest.Matchers.anyOf;
import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.morda.pages.desktop.yaru.DesktopYaruMorda.desktopYaru;
import static ru.yandex.autotests.morda.pages.touch.comtr.TouchComTrMorda.touchComTr;
import static ru.yandex.autotests.morda.utils.matchers.AllOfDetailedMatcher.allOfDetailed;
import static ru.yandex.autotests.utils.morda.ParametrizationConverter.convert;
import static ru.yandex.autotests.utils.morda.url.UrlManager.encode;
import static ru.yandex.autotests.utils.morda.url.UrlManager.encodeRequest;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 28/02/15
 */
@Aqua.Test(title = "Search request")
@Features("Search")
@Stories("Search request")
@RunWith(Parameterized.class)
public class SearchRequestTest {
    private static final MordaWebTestsProperties CONFIG = new MordaWebTestsProperties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;
    private WebDriver driver;
    private CommonMordaSteps user;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        List<Morda<? extends PageWithSearchBlock<? extends BlockWithSearchForm>>> data = new ArrayList<>();

        String scheme = CONFIG.getMordaScheme();
        String environment = CONFIG.getMordaEnvironment();
        String userAgentTouchIphone = CONFIG.getMordaUserAgentTouchIphone();
        String userAgentTouchWp = CONFIG.getMordaUserAgentTouchWp();
        String userAgentPda = CONFIG.getMordaUserAgentPda();

        data.addAll(DesktopMainMorda.getDefaultList(scheme, environment));
        data.add(desktopYaru(scheme, environment));
        data.add(touchComTr(CONFIG.getMordaScheme(), CONFIG.getMordaEnvironment(), Region.IZMIR,
                CONFIG.getMordaUserAgentTouchIphone()));
        data.addAll(DesktopComMorda.getDefaultList(scheme, environment));
        data.addAll(Com404Morda.getDefaultList(scheme, environment));
//        data.add(desktopFirefoxRu(scheme, environment, Region.MOSCOW, Language.RU));
//        data.add(desktopFirefoxUa(scheme, environment, Region.KIEV, Language.UK));
//        data.add(desktopFirefoxComTr(scheme, environment, Region.IZMIR));
        data.addAll(DesktopFirefoxMorda.getDefaultList(scheme, environment));

        return convert(MordaType.filter(data, CONFIG.getMordaPagesToTest()));
    }

    private Morda<? extends PageWithSearchBlock<? extends BlockWithSearchForm>> morda;
    private PageWithSearchBlock<? extends BlockWithSearchForm> page;

    public SearchRequestTest(Morda<? extends PageWithSearchBlock<? extends BlockWithSearchForm>> morda) {
        this.morda = morda;
        this.mordaAllureBaseRule = this.morda.getRule();
        this.driver = mordaAllureBaseRule.getDriver();
        this.user = new CommonMordaSteps(driver);
        this.page = morda.getPage(driver);
    }

    @Test
    public void searchRequest() throws InterruptedException {
        String request = "grumpy cat";
        user.opensPage(morda.getUrl().toString());
        user.shouldSeeElement(page.getSearchBlock());
        user.shouldSeeElement(page.getSearchBlock().getSearchInput());
        user.entersTextInInput(page.getSearchBlock().getSearchInput(), request);
        user.shouldSeeElement(page.getSearchBlock().getSearchButton());
        user.clicksOn(page.getSearchBlock().getSearchButton());
        user.shouldSeePage(allOfDetailed(
                startsWith(morda.getSerpUrl().toString()),
                anyOf(
                        containsString(encodeRequest(request)),
                        containsString(encode(request))
                )
        ));

    }
}
