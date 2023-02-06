package ru.yandex.autotests.morda.tests.clid.morda;

import com.jayway.restassured.response.Response;
import org.apache.log4j.Logger;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.api.MordaClient;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.MordaType;
import ru.yandex.autotests.morda.pages.com.DesktopComMorda;
import ru.yandex.autotests.morda.pages.com.PdaComMorda;
import ru.yandex.autotests.morda.pages.com.TouchComMorda;
import ru.yandex.autotests.morda.pages.comtr.DesktopComTrFootballMorda;
import ru.yandex.autotests.morda.pages.comtr.DesktopComTrMorda;
import ru.yandex.autotests.morda.pages.comtr.DesktopFamilyComTrMorda;
import ru.yandex.autotests.morda.pages.comtr.PdaComTrMorda;
import ru.yandex.autotests.morda.pages.comtr.TouchComTrMorda;
import ru.yandex.autotests.morda.pages.comtr.TouchComTrWpMorda;
import ru.yandex.autotests.morda.pages.main.DesktopFamilyMainMorda;
import ru.yandex.autotests.morda.pages.main.DesktopFirefoxMorda;
import ru.yandex.autotests.morda.pages.main.DesktopMainMorda;
import ru.yandex.autotests.morda.pages.main.MainMorda;
import ru.yandex.autotests.morda.pages.main.PdaMainMorda;
import ru.yandex.autotests.morda.pages.main.TouchMainMorda;
import ru.yandex.autotests.morda.pages.main.TouchMainWpMorda;
import ru.yandex.autotests.morda.pages.yaru.DesktopYaruMorda;
import ru.yandex.autotests.morda.restassured.requests.RestAssuredGetRequest;
import ru.yandex.autotests.morda.rules.allure.AllureLoggingRule;
import ru.yandex.autotests.morda.steps.set.SetSteps;
import ru.yandex.autotests.morda.tests.MordaTestTags;
import ru.yandex.autotests.morda.tests.MordaTestsProperties;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.Map;

import static ru.yandex.autotests.morda.pages.MordaType.DESKTOP_MAIN;
import static ru.yandex.autotests.morda.pages.MordaType.PDA_MAIN;
import static ru.yandex.autotests.morda.pages.MordaType.TOUCH_MAIN;
import static ru.yandex.autotests.morda.pages.MordaType.TOUCH_MAIN_WP;
import static ru.yandex.autotests.morda.tests.MordaTestTags.CLID;

/**
 * User: asamar
 * Date: 19.01.17
 */
@Aqua.Test(title = "Clid in yp cookie")
@RunWith(Parameterized.class)
@Features({MordaTestTags.MORDA, CLID})
public class ClidInYpCookieTest {
    private static Logger LOGGER = Logger.getLogger(ClidInYpCookieTest.class);
    private static final MordaTestsProperties CONFIG = new MordaTestsProperties();

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Morda<?>> data() {
        List<Morda<?>> data = new ArrayList<>();

        data.addAll(PdaComMorda.getDefaultList(CONFIG.pages().getEnvironment()));
        data.addAll(DesktopYaruMorda.getDefaultList(CONFIG.pages().getEnvironment()));
        data.addAll(DesktopMainMorda.getDefaultList(CONFIG.pages().getEnvironment()));
        data.addAll(DesktopFamilyMainMorda.getDefaultList(CONFIG.pages().getEnvironment()));
        data.addAll(DesktopComMorda.getDefaultList(CONFIG.pages().getEnvironment()));
        data.addAll(DesktopFirefoxMorda.getDefaultList(CONFIG.pages().getEnvironment()));
        data.addAll(DesktopComTrMorda.getDefaultList(CONFIG.pages().getEnvironment()));
        data.addAll(DesktopFamilyComTrMorda.getDefaultList(CONFIG.pages().getEnvironment()));
        data.addAll(DesktopComTrFootballMorda.getDefaultList(CONFIG.pages().getEnvironment()));
        data.addAll(TouchMainMorda.getDefaultList(CONFIG.pages().getEnvironment()));
        data.addAll(TouchComTrMorda.getDefaultList(CONFIG.pages().getEnvironment()));
        data.addAll(TouchComMorda.getDefaultList(CONFIG.pages().getEnvironment()));
        data.addAll(TouchMainWpMorda.getDefaultList(CONFIG.pages().getEnvironment()));
        data.addAll(TouchComTrWpMorda.getDefaultList(CONFIG.pages().getEnvironment()));
        data.addAll(PdaComTrMorda.getDefaultList(CONFIG.pages().getEnvironment()));
        data.addAll(PdaMainMorda.getDefaultList(CONFIG.pages().getEnvironment()));

        return data;
    }

    @Rule
    public AllureLoggingRule allureLoggingRule = new AllureLoggingRule();
    private Morda<?> morda;
    private MordaClient mordaClient;
    private SetSteps user;
    private Response response;

    private static final String CLH = "clh";
    private static final String SOME_CLID = "123456";
    private static final String ANOTHER_CLID = "654321";
    private static final String CLID_WITH_HYPHEN = "123-456";

    public ClidInYpCookieTest(Morda<?> morda) {
        this.morda = morda;
        this.mordaClient = new MordaClient();
        this.user = new SetSteps();
    }

    @Before
    public void init() {
        this.response = mordaClient.morda(morda).invoke();
    }

    @Test
    public void clidFoundInCookieYP() {
        Response response = getRequest(SOME_CLID).readAsResponse();
        user.ypDetailedShouldContains(CLH, SOME_CLID, response, morda.getCookieDomain());
    }

    @Test
    public void clidWithHyphenFoundInCookieYP() {
        Response response = getRequest(CLID_WITH_HYPHEN).readAsResponse();
        user.ypDetailedShouldContains(CLH, CLID_WITH_HYPHEN, response, morda.getCookieDomain());
    }

    @Test
    public void clidCanBeOverriddenInCookieYP() throws InterruptedException {
        getRequest(SOME_CLID).readAsResponse();
        Response response = getRequest(ANOTHER_CLID).readAsResponse();

        user.ypDetailedShouldContains(CLH, ANOTHER_CLID, response, morda.getCookieDomain());
    }

    private RestAssuredGetRequest getRequest(String clid) {
        MordaType mt = morda.getMordaType();
        MainMorda<?> mainMorda;

        RestAssuredGetRequest request = mordaClient.morda(morda).queryParam(CLID, clid);
        if (morda.getMordaType() == MordaType.PDA_COM) {
            request.cookie("S", clid);
        }
        if (mt == DESKTOP_MAIN || mt == TOUCH_MAIN || mt == PDA_MAIN || mt == TOUCH_MAIN_WP) {
            String yp = response.getCookies().entrySet().stream()
                    .filter(e -> "yp".equals(e.getKey()))
                    .map(Map.Entry::getValue)
                    .findFirst()
                    .orElseThrow(() -> new RuntimeException("yp cookie is missing"));

            String newYpValue = yp.replaceAll("(?<=\\.ygu\\.)\\d", "0");

            mainMorda = (MainMorda<?>) morda;
            request.cookie("yandex_gid", String.valueOf(mainMorda.getRegion().getRegionId()));
            request.cookie("yp", newYpValue);
        }
        return request;
    }
}
