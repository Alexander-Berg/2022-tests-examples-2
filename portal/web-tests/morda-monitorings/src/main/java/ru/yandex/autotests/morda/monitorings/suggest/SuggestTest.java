package ru.yandex.autotests.morda.monitorings.suggest;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.tika.mime.MimeTypes;
import org.junit.After;
import org.junit.Before;
import org.junit.ClassRule;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.monitorings.MonitoringProperties;
import ru.yandex.autotests.morda.monitorings.rules.MordaMonitoringsRule;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.desktop.com.DesktopComMorda;
import ru.yandex.autotests.morda.pages.desktop.comtr.DesktopComTrMorda;
import ru.yandex.autotests.morda.pages.desktop.firefox.DesktopFirefoxMorda;
import ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda;
import ru.yandex.autotests.morda.pages.desktop.smarttv.SmartTvMorda;
import ru.yandex.autotests.morda.pages.interfaces.blocks.BlockWithSearchForm;
import ru.yandex.autotests.morda.pages.interfaces.blocks.BlockWithSuggest;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithSearchBlock;
import ru.yandex.autotests.morda.pages.touch.com.TouchComMorda;
import ru.yandex.autotests.morda.pages.touch.comtr.TouchComTrMorda;
import ru.yandex.autotests.morda.pages.touch.embedsearch.EmbedSearchMorda;
import ru.yandex.autotests.morda.pages.touch.ru.TouchRuMorda;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.rules.proxy.actions.HarAction;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Attachment;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.monitoring.MonitoringNotifierRule;
import ru.yandex.qatools.monitoring.graphite.GraphiteMetric;
import ru.yandex.qatools.monitoring.graphite.GraphiteMetricPrefix;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static javax.ws.rs.core.UriBuilder.fromUri;
import static org.hamcrest.MatcherAssert.assertThat;
import static ru.yandex.autotests.morda.monitorings.matchers.SuggestMatcher.suggestIsOk;
import static ru.yandex.autotests.utils.morda.language.Language.UK;
import static ru.yandex.autotests.utils.morda.region.Region.KIEV;
import static ru.yandex.autotests.utils.morda.region.Region.MOSCOW;
import static ru.yandex.qatools.monitoring.MonitoringNotifierRule.notifierRule;

@Aqua.Test(title = "Suggest monitoring")
@Features("Suggest")
@RunWith(Parameterized.class)
@GraphiteMetricPrefix("servers.portal.eoff.monitorings.suggest")
public class SuggestTest {

    private static MonitoringProperties CONFIG = new MonitoringProperties();

    @Parameterized.Parameters(name = "Suggest in {0}")
    public static Collection<Morda<? extends PageWithSearchBlock<? extends BlockWithSearchForm>>> data() {

        List<Morda<? extends PageWithSearchBlock<? extends BlockWithSearchForm>>> mordas = new ArrayList<>();

        String scheme = CONFIG.getMordaScheme();
        String env = CONFIG.getMordaEnvironment();
        String touchUserAgent = CONFIG.getMordaUserAgentTouchIphone();
        String smartTvUserAgent = CONFIG.getSmartTvUserAgent();

        mordas.addAll(TouchRuMorda.getDefaultList(scheme, env, touchUserAgent));
        mordas.add(EmbedSearchMorda.embedSearchMorda(scheme, env));
        mordas.addAll(DesktopMainMorda.getDefaultList(scheme, env));
        mordas.add(DesktopComTrMorda.desktopComTr(scheme, env));
        mordas.addAll(DesktopComMorda.getDefaultList(scheme, env));
        mordas.add(DesktopFirefoxMorda.desktopFirefox(scheme, env, MOSCOW, UK));
        mordas.add(DesktopFirefoxMorda.desktopFirefox(scheme, env, KIEV, UK));
        mordas.add(TouchComMorda.touchCom(scheme, env, touchUserAgent));
        mordas.add(TouchComTrMorda.touchComTr(scheme, env, Region.ISTANBUL, touchUserAgent));
        mordas.add(SmartTvMorda.smartTvMorda(scheme, env, smartTvUserAgent, MOSCOW));

        return mordas;//.subList(0, 1);
    }

    private static final String INPUT_TEXT = "some ";

    @Rule
    @ClassRule
    public static MonitoringNotifierRule notifierRule = notifierRule();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;
    public MordaMonitoringsRule mordaMonitoringsRule;
    private Morda<? extends PageWithSearchBlock> morda;
    private PageWithSearchBlock<? extends BlockWithSearchForm> page;
    private WebDriver driver;
    private CommonMordaSteps userSteps;
    private String content;

    public SuggestTest(Morda<? extends PageWithSearchBlock<? extends BlockWithSearchForm>> morda) {
        this.morda = morda;
        this.mordaAllureBaseRule = morda.getRule()
                .withProxyAction(new HarAction("suggest-har"));
        this.driver = mordaAllureBaseRule.getDriver();
        this.mordaMonitoringsRule = new MordaMonitoringsRule(driver);
        this.mordaAllureBaseRule
                .withRule(mordaMonitoringsRule);
        this.userSteps = new CommonMordaSteps(driver);
        this.page = morda.getPage(driver);
    }

    @Before
    public void setUp() {
        morda.initialize(driver);
        userSteps.opensPage(
                fromUri(morda.getUrl())
                        .queryParam("yandex", "0")
                        .build()
                        .toString()
        );
        content = driver.getPageSource();
        userSteps.shouldSeeElement(page.getSearchBlock().getSearchInput());
    }

    @GraphiteMetric("exists")
    @Test
    public void suggestExists() throws InterruptedException {
        for (char c : INPUT_TEXT.toCharArray()) {
            userSteps.appendsTextInInput(page.getSearchBlock().getSearchInput(), String.valueOf(c));
            Thread.sleep(50);
        }

        BlockWithSuggest blockWithSuggest = (BlockWithSuggest) page.getSearchBlock();
        userSteps.shouldSeeElement(blockWithSuggest.getSuggest());

        shouldSeeSuggestRequests();
    }

    @After
    public void attachHar() throws JsonProcessingException {
        System.out.println(attachInfo());
    }

    @Attachment(value = "morda_info.txt", type = MimeTypes.PLAIN_TEXT)
    public String attachInfo() throws JsonProcessingException {
        return new ObjectMapper().writerWithDefaultPrettyPrinter().writeValueAsString(
                mordaAllureBaseRule.getProxyServer().getHar().getLog()) + "\n\n\n" + content;
    }

    @Step
    public void shouldSeeSuggestRequests() {
        assertThat(mordaAllureBaseRule.getProxyServer().getHar(), suggestIsOk());
    }
}
