package ru.yandex.autotests.morda.tests.consistency;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.log4j.Logger;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.logging.LogEntry;
import org.openqa.selenium.logging.LogType;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.desktop.com.DesktopComMorda;
import ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda;
import ru.yandex.autotests.morda.pages.desktop.spok.DesktopSpokMorda;
import ru.yandex.autotests.morda.pages.touch.spok.TouchSpokMorda;
import ru.yandex.autotests.morda.tests.web.MordaWebTestsProperties;
import ru.yandex.autotests.morda.utils.matchers.StaticDownloadedMatcher;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.logging.Level;
import java.util.stream.Collectors;

import static java.lang.Thread.sleep;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.hasSize;
import static ru.yandex.autotests.morda.pages.MordaType.D_HWLG;
import static ru.yandex.autotests.morda.pages.desktop.comtr.DesktopComTrMorda.desktopComTr;
import static ru.yandex.autotests.morda.pages.desktop.comtrall.DesktopComTrAllMorda.desktopComTrAll;
import static ru.yandex.autotests.morda.pages.desktop.comtrfootball.DesktopComTrFootballMorda.desktopComTrBjk;
import static ru.yandex.autotests.morda.pages.desktop.comtrfootball.DesktopComTrFootballMorda.desktopComTrGs;
import static ru.yandex.autotests.morda.pages.desktop.hwbmw.DesktopHwBmwMorda.desktopHwBmw;
import static ru.yandex.autotests.morda.pages.desktop.hwlg.DesktopHwLgMorda.desktopHwLg;
import static ru.yandex.autotests.morda.pages.desktop.hwlgV2.DesktopHwLgV2Morda.desktopHwLgV2;
import static ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda.desktopMain;
import static ru.yandex.autotests.morda.pages.desktop.mainall.DesktopMainAllMorda.desktopMainAll;
import static ru.yandex.autotests.morda.pages.desktop.op.DesktopOpMorda.desktopOp;
import static ru.yandex.autotests.morda.pages.desktop.yaru.DesktopYaruMorda.desktopYaru;
import static ru.yandex.autotests.morda.pages.pda.com.PdaComMorda.pdaCom;
import static ru.yandex.autotests.morda.pages.pda.comtr.PdaComTrMorda.pdaComTr;
import static ru.yandex.autotests.morda.pages.pda.comtrall.PdaComTrAllMorda.pdaComTrAll;
import static ru.yandex.autotests.morda.pages.pda.ru.PdaRuMorda.pdaRu;
import static ru.yandex.autotests.morda.pages.pda.ruall.PdaRuAllMorda.pdaRuAll;
import static ru.yandex.autotests.morda.pages.pda.yaru.PdaYaRuMorda.pdaYaRu;
import static ru.yandex.autotests.morda.pages.touch.com.TouchComMorda.touchCom;
import static ru.yandex.autotests.morda.pages.touch.comtr.TouchComTrMorda.touchComTr;
import static ru.yandex.autotests.morda.pages.touch.comtrall.TouchComTrAllMorda.touchComTrAll;
import static ru.yandex.autotests.morda.pages.touch.comtrwp.TouchComTrWpMorda.touchComTrWp;
import static ru.yandex.autotests.morda.pages.touch.ru.TouchRuMorda.touchRu;
import static ru.yandex.autotests.morda.pages.touch.ruall.TouchRuAllMorda.touchRuAll;
import static ru.yandex.autotests.morda.pages.touch.ruwp.TouchRuWpMorda.touchRuWp;
import static ru.yandex.autotests.morda.pages.touch.yaru.TouchYaRuMorda.touchYaRu;
import static ru.yandex.autotests.mordacommonsteps.rules.proxy.actions.HarAction.addHar;
import static ru.yandex.autotests.utils.morda.language.Language.RU;
import static ru.yandex.autotests.utils.morda.region.Region.MOSCOW;

/**
 * User: alex89
 * Date: 18.03.13
 */

@Aqua.Test(title = "Проверка отсутствия js-ошибок")
@RunWith(Parameterized.class)
@Features("Consistency")
public class MordaConsistencyTest {
    private static final Logger LOG = Logger.getLogger(MordaConsistencyTest.class);
    private static final MordaWebTestsProperties CONFIG = new MordaWebTestsProperties();
    public static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        List<Morda<?>> data = new ArrayList<>();

        String scheme = CONFIG.getMordaScheme();
        String environment = CONFIG.getMordaEnvironment();
        String userAgentTouchIphone = CONFIG.getMordaUserAgentTouchIphone();
        String userAgentTouchWp = CONFIG.getMordaUserAgentTouchWp();
        String userAgentPda = CONFIG.getMordaUserAgentPda();

        data.addAll(DesktopMainMorda.getDefaultList(scheme, environment));
        data.add(desktopMainAll(scheme, environment, MOSCOW));

//        data.add(desktopFamilyMain(scheme, environment, MOSCOW));
//        data.add(desktopFamilyMainAll(scheme, environment, MOSCOW));

        data.add(desktopYaru(scheme, environment));
        data.add(desktopOp("http", environment));

        data.addAll(DesktopComMorda.getDefaultList(scheme, environment));

//        data.add(desktopFirefox(scheme, environment, MOSCOW, RU));
//        data.add(desktopFirefox(scheme, environment, KIEV, RU));
//        data.add(desktopFirefox(scheme, environment, ISTANBUL, TR));
//        data.addAll(DesktopFirefoxMorda.getDefaultList(scheme, environment));

        data.add(desktopComTr(scheme, environment));
        data.add(desktopComTrAll(scheme, environment));
//        data.add(desktopFamilyComTr(scheme, environment));
//        data.add(desktopFamilyComTrAll(scheme, environment));

        data.add(desktopComTrBjk(scheme, environment));
        data.add(desktopComTrGs(scheme, environment));
//        data.add(desktopFamilyComTrGs(scheme, environment));
//        data.add(desktopFamilyComTrBjk(scheme, environment));

        data.add(desktopHwLg(scheme, environment));
        data.add(desktopHwLgV2("http", environment));
        data.add(desktopHwBmw(scheme, environment));

        data.add(touchRu(scheme, environment, userAgentTouchIphone, MOSCOW, RU));
        data.add(touchRuAll(scheme, environment, userAgentTouchIphone));
        data.add(touchComTr(scheme, environment, Region.ISTANBUL, userAgentTouchIphone));
        data.add(touchComTrAll(scheme, environment, Region.ISTANBUL, userAgentTouchIphone));
        data.add(touchCom(scheme, environment, userAgentTouchIphone));
        data.add(touchRuWp(scheme, environment, userAgentTouchWp));
        data.add(touchComTrWp(scheme, environment, Region.ISTANBUL, userAgentTouchWp));
        data.add(touchYaRu(scheme, environment, userAgentTouchIphone));

        data.add(pdaRu(scheme, environment, userAgentPda));
        data.add(pdaRuAll(scheme, environment, userAgentPda));
        data.add(pdaComTr(scheme, environment, userAgentPda));
        data.add(pdaComTrAll(scheme, environment, userAgentPda));
        data.add(pdaCom(scheme, environment, userAgentPda));
        data.add(pdaYaRu(scheme, environment, userAgentPda));

        data.addAll(DesktopSpokMorda.getDefaultList(environment));
        data.addAll(TouchSpokMorda.getDefaultList(environment, userAgentTouchIphone));

        return ParametrizationConverter.convert(data);
    }

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;
    private WebDriver driver;
    private Morda<?> morda;

    public MordaConsistencyTest(Morda<?> morda) {
        this.morda = morda;
        this.mordaAllureBaseRule = this.morda.getRule()
                .withProxyAction(addHar("js-errors"));
        this.driver = mordaAllureBaseRule.getDriver();
    }

    @Before
    public void setUp() throws InterruptedException {
        morda.initialize(driver);
        if (morda.getMordaType().equals(D_HWLG)) {
            sleep(5000);
        }
    }

    @Test
    public void noJSErrors() throws IOException {
        List<LogEntry> severeLogs = driver.manage().logs().get(LogType.BROWSER).getAll().stream()
                .filter(e -> !e.getMessage().contains("NS_ERROR_ILLEGAL_VALUE")
                        && !e.getMessage().contains("NS_ERROR_FAILURE")
                        && e.getLevel().equals(Level.SEVERE))
                .collect(Collectors.toList());

        assertThat("Detected " + severeLogs.size() + " js-errors: " + severeLogs, severeLogs, hasSize(0));
    }

    @Test
    public void staticIsOk() {
        assertThat(morda.toString(), mordaAllureBaseRule.getProxyServer().getHar(),
                StaticDownloadedMatcher.staticDownloaded());
    }
}

