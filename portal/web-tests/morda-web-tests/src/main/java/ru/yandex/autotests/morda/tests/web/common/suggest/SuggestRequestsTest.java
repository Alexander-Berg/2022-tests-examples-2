package ru.yandex.autotests.morda.tests.web.common.suggest;

import net.lightbody.bmp.core.har.Har;
import net.lightbody.bmp.core.har.HarEntry;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.interfaces.blocks.BlockWithSuggest;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithSearchBlock;
import ru.yandex.autotests.morda.tests.web.MordaWebTestsProperties;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static ru.yandex.autotests.mordacommonsteps.rules.proxy.actions.HarAction.addHar;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 28/02/15
 */
@Aqua.Test(title = "Suggest requests")
@Features("Suggest")
@Stories("Suggest requests")
@RunWith(Parameterized.class)
public class SuggestRequestsTest {
    private static final MordaWebTestsProperties CONFIG = new MordaWebTestsProperties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;
    private WebDriver driver;
    private CommonMordaSteps user;
    private SuggestSteps userSuggest;

    @Parameterized.Parameters(name = "{0}, {1}")
    public static Collection<Object[]> data() {
        List<Object[]> data = new ArrayList<>();
        String ruRequest = "запрос";
        String enRequest = "request";
        String comTrRequest = "isteği";
        String twoWordsRequest = "fat cat";

//        for (String request : asList(ruRequest)){//, enRequest, comTrRequest, twoWordsRequest)) {
//            data.add(new Object[]{desktopMain(CONFIG.getMordaScheme(), CONFIG.getMordaEnvironment(), 10), request});
//            data.add(new Object[]{desktopFamilyMain(CONFIG.getMordaScheme(), CONFIG.getMordaEnvironment(), 10),
//                    request});
//            data.add(new Object[]{desktopYaru(CONFIG.getMordaScheme(), CONFIG.getMordaEnvironment()), request});
//            data.add(new Object[]{touchRu(CONFIG.getMordaScheme(), CONFIG.getMordaEnvironment(),
//                    CONFIG.getMordaUserAgentTouchIphone()), request});
//            data.add(new Object[]{desktopCom(CONFIG.getMordaScheme(), CONFIG.getMordaEnvironment()), request});
//            data.add(new Object[]{desktopFirefoxRu(CONFIG.getMordaScheme(), CONFIG.getMordaEnvironment()), request});
//            data.add(new Object[]{desktopFirefoxUa(CONFIG.getMordaScheme(), CONFIG.getMordaEnvironment()), request});
//        }

//        for (String request : asList(enRequest, comTrRequest, twoWordsRequest)) {
//            data.add(new Object[]{desktopComTr(CONFIG.getMordaScheme(), CONFIG.getMordaEnvironment()), request});
//            data.add(new Object[]{desktopFamilyComTr(CONFIG.getMordaScheme(), CONFIG.getMordaEnvironment()), request});
//            data.add(new Object[]{touchComTr(CONFIG.getMordaScheme(), CONFIG.getMordaEnvironment(), Region.IZMIR,
//                    CONFIG.getMordaUserAgentTouchIphone()), request});
//            data.add(new Object[]{desktopFirefoxComTr(CONFIG.getMordaScheme(), CONFIG.getMordaEnvironment()), request});
//        }

        return data;
    }

    private Morda<? extends PageWithSearchBlock<? extends BlockWithSuggest>> morda;
    private PageWithSearchBlock<? extends BlockWithSuggest> page;
    private String request;

    public SuggestRequestsTest(Morda<? extends PageWithSearchBlock<? extends BlockWithSuggest>> morda, String request) {
        this.morda = morda;
        this.request = request;
        this.mordaAllureBaseRule = this.morda.getRule().withProxyAction(addHar("suggest"));
        this.driver = mordaAllureBaseRule.getDriver();
        this.user = new CommonMordaSteps(driver);
        this.userSuggest = new SuggestSteps(driver);
        this.page = morda.getPage(driver);
    }

    @Before
    public void initialize() {
        morda.initialize(driver);
    }

    @Test
    public void suggestAppearsAndCloses() throws InterruptedException {
        user.opensPage(morda.getUrl().toString());
        user.shouldSeeElement(page.getSearchBlock());
        user.shouldSeeElement(page.getSearchBlock().getSearchInput());
        userSuggest.appendsTextInInputSlowly(page.getSearchBlock().getSearchInput(), request);
        Har har = mordaAllureBaseRule.getProxyServer().getHar();
        for (HarEntry entry : har.getLog().getEntries()) {
            if (entry.getRequest().getUrl().contains("suggest")) {
                System.out.println(entry.getRequest().getUrl());
                System.out.println(entry.getResponse().getContent().getText());
            }
        }
    }

}
