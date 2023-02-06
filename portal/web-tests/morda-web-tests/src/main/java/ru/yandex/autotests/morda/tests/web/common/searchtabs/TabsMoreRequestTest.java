package ru.yandex.autotests.morda.tests.web.common.searchtabs;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda;
import ru.yandex.autotests.morda.pages.desktop.main.blocks.SearchBlock;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithSearchBlock;
import ru.yandex.autotests.morda.tests.web.MordaWebTestsProperties;
import ru.yandex.autotests.morda.utils.matchers.UrlMatcher;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.beans.servicestabs.ServicesTab;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.Optional;

import static java.util.Arrays.asList;
import static java.util.stream.Collectors.toList;
import static org.hamcrest.Matchers.anyOf;
import static org.hamcrest.Matchers.equalTo;
import static org.junit.Assert.fail;
import static ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda.desktopMain;
import static ru.yandex.autotests.morda.utils.matchers.UrlMatcher.ParamMatcher.urlParam;
import static ru.yandex.autotests.morda.utils.matchers.UrlMatcher.urlMatcher;
import static ru.yandex.autotests.mordabackend.MordaClient.getJsonEnabledClient;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.utils.morda.url.UrlManager.encode;
import static ru.yandex.autotests.utils.morda.url.UrlManager.encodeRequest;

/**
 * User: asamar
 * Date: 16.12.2015.
 */
@Aqua.Test(title = "Пробрасывание запросов в табах \"ещё\"")
@RunWith(Parameterized.class)
@Features("Search Tabs")
@Stories("Tabs more")
public class TabsMoreRequestTest {
    private static final MordaWebTestsProperties CONFIG = new MordaWebTestsProperties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;

    @Parameterized.Parameters(name = "{0},{2}")
    public static Collection<Object[]> data() {

        String scheme = CONFIG.getMordaScheme();
        String environment = CONFIG.getMordaEnvironment();

        List<Object[]> data = new ArrayList<>();

        asList(
                desktopMain(scheme, environment, Region.MOSCOW),
                desktopMain(scheme, environment, Region.KIEV)
        ).forEach(morda -> {

            Cleanvars cleanvars = new MordaClient(morda.getUrl())
                    .cleanvarsActions(getJsonEnabledClient())
                    .get();

            List<ServicesTab> tabs = cleanvars.getServicesTabs().getMore().stream()
                    .filter(it -> it.getSearch() != null)
                    .filter(e -> !e.getId().equals("music"))
                    .collect(toList());

            tabs.forEach(tab ->
                            data.add(new Object[]{morda, tab, tab.getId()})
            );
        });
        return data;
    }

    private ServicesTab tab;
    private WebDriver driver;
    private CommonMordaSteps user;
    private DesktopMainMorda morda;
    private PageWithSearchBlock<? extends SearchBlock> page;
    private String request;
    private UrlMatcher tabUrlMatcher;

    public TabsMoreRequestTest(DesktopMainMorda morda, ServicesTab tab, String id) {
        this.morda = morda;
        this.tab = tab;
        this.mordaAllureBaseRule = morda.getRule();
        this.driver = mordaAllureBaseRule.getDriver();
        this.user = new CommonMordaSteps(driver);
        this.page = morda.getPage(driver);
    }

    @Before
    public void init() {
        morda.initialize(driver);
        request = "grumpy cat";

        String url = tab.getSearch().startsWith("http") ?
                tab.getSearch() :
                morda.getScheme() + ":" + tab.getSearch();

        url = url.replaceAll("\\??request=$", "");

        if (tab.getId().equals("pogoda")) {
            tabUrlMatcher = urlMatcher(url)
                    .urlParams(
                            urlParam("request", anyOf(
                                    equalTo(encodeRequest(request)),
                                    equalTo(encode(request))
                            ))
                    )
                    .build();
        } else {
            tabUrlMatcher = urlMatcher(url)
                    .urlParams(
                            urlParam("text", anyOf(
                                    equalTo(encodeRequest(request)),
                                    equalTo(encode(request))
                            ))
                    )
                    .build();
        }
    }

    @Test
    public void tabRequestTest() throws Exception {
        user.clicksOn(page.getSearchBlock().more);
        Optional<HtmlElement> searchTab = page.getSearchBlock().moreTabs.stream()
                .filter(it -> tab.getId().equals(it.getAttribute("data-id")))
                .findFirst();
        if (!searchTab.isPresent()) {
            fail("Табика с id=" + tab.getId() + " нет в верстке");
        }

        user.entersTextInInput(page.getSearchBlock().getSearchInput(), request);
        user.shouldSeeElementMatchingTo(searchTab.get(), hasAttribute(HREF, tabUrlMatcher));
    }
}
