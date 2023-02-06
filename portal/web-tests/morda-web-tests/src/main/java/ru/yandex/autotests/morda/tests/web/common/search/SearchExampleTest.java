package ru.yandex.autotests.morda.tests.web.common.search;

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
import ru.yandex.autotests.morda.tests.web.MordaWebTestsProperties;
import ru.yandex.autotests.morda.utils.matchers.UrlMatcher;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static org.hamcrest.Matchers.anyOf;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.morda.utils.matchers.UrlMatcher.ParamMatcher.urlParam;
import static ru.yandex.autotests.morda.utils.matchers.UrlMatcher.urlMatcher;
import static ru.yandex.autotests.utils.morda.ParametrizationConverter.convert;
import static ru.yandex.autotests.utils.morda.url.UrlManager.encode;
import static ru.yandex.autotests.utils.morda.url.UrlManager.encodeRequest;

/**
 * User: asamar
 * Date: 11.12.2015.
 */
@Aqua.Test(title = "Пример запроса поиска")
@Features("Search")
@Stories("Example")
@RunWith(Parameterized.class)
public class SearchExampleTest {
    private static final MordaWebTestsProperties CONFIG = new MordaWebTestsProperties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;
    private WebDriver driver;
    private CommonMordaSteps user;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        List<Morda<DesktopMainPage>> data = new ArrayList<>();
        String scheme = CONFIG.getMordaScheme();
        String environment = CONFIG.getMordaEnvironment();

        data.addAll(DesktopMainMorda.getDefaultList(scheme, environment));

        return convert(MordaType.filter(data, CONFIG.getMordaPagesToTest()));
    }

    private Morda<DesktopMainPage> morda;
    private DesktopMainPage page;
    private UrlMatcher serpUrlMatcher;

    public SearchExampleTest(Morda<DesktopMainPage> morda) {
        this.morda = morda;
        this.mordaAllureBaseRule = this.morda.getRule();
        this.driver = mordaAllureBaseRule.getDriver();
        this.user = new CommonMordaSteps(driver);
        this.page = morda.getPage(driver);
    }

    @Before
    public void init() {
        morda.initialize(driver);
        serpUrlMatcher = urlMatcher()
                .scheme(morda.getSerpUrl().getScheme())
                .host(morda.getSerpUrl().getHost())
                .path(morda.getSerpUrl().getPath() + "/")
                .urlParams(
                        urlParam("lr", page.getSearchBlock().getLr().getAttribute("value")),
                        urlParam("nl","1"),
                        urlParam("text", anyOf(
                                equalTo(encodeRequest(
                                        page.getSearchBlock().searchForm.searchSample.getSample().getText())
                                ),
                                equalTo(encode(
                                        page.getSearchBlock().searchForm.searchSample.getSample().getText())
                                )
                        ))
                )
                .build();
    }

    @Test
    public void searchExampleClick() throws InterruptedException {
        user.shouldSeeElement(page.getSearchBlock().searchForm.searchSample);
        user.clicksOn(page.getSearchBlock().searchForm.searchSample.getSample());
        Thread.sleep(1000);
        user.shouldSeePage(serpUrlMatcher);
    }
}
