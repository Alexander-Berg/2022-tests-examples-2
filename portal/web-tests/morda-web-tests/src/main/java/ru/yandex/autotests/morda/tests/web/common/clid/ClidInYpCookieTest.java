package ru.yandex.autotests.morda.tests.web.common.clid;

import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.MordaType;
import ru.yandex.autotests.morda.pages.desktop.com.DesktopComMorda;
import ru.yandex.autotests.morda.pages.touch.ru.TouchRuMorda;
import ru.yandex.autotests.morda.rules.allure.AllureFeatureRule;
import ru.yandex.autotests.morda.tests.web.MordaWebTestsProperties;
import ru.yandex.autotests.morda.utils.client.MordaDefaultClient;
import ru.yandex.autotests.morda.utils.cookie.parsers.y.YpCookieValue;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static javax.ws.rs.core.UriBuilder.fromUri;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.notNullValue;
import static ru.yandex.autotests.morda.pages.desktop.comtr.DesktopComTrMorda.desktopComTr;
import static ru.yandex.autotests.morda.pages.desktop.comtr.DesktopComTrMorda.desktopFamilyComTr;
import static ru.yandex.autotests.morda.pages.desktop.comtrfootball.DesktopComTrFootballMorda.desktopComTrBjk;
import static ru.yandex.autotests.morda.pages.desktop.comtrfootball.DesktopComTrFootballMorda.desktopComTrGs;
import static ru.yandex.autotests.morda.pages.desktop.comtrfootball.DesktopComTrFootballMorda.desktopFamilyComTrBjk;
import static ru.yandex.autotests.morda.pages.desktop.comtrfootball.DesktopComTrFootballMorda.desktopFamilyComTrGs;
import static ru.yandex.autotests.morda.pages.desktop.firefox.DesktopFirefoxMorda.desktopFirefox;
import static ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda.desktopFamilyMain;
import static ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda.desktopMain;
import static ru.yandex.autotests.morda.pages.desktop.yaru.DesktopYaruMorda.desktopYaru;
import static ru.yandex.autotests.morda.pages.pda.com.PdaComMorda.pdaCom;
import static ru.yandex.autotests.morda.pages.pda.comtr.PdaComTrMorda.pdaComTr;
import static ru.yandex.autotests.morda.pages.pda.ru.PdaRuMorda.pdaRu;
import static ru.yandex.autotests.morda.pages.touch.com.TouchComMorda.touchCom;
import static ru.yandex.autotests.morda.pages.touch.comtr.TouchComTrMorda.touchComTr;
import static ru.yandex.autotests.morda.pages.touch.comtrwp.TouchComTrWpMorda.touchComTrWp;
import static ru.yandex.autotests.morda.pages.touch.ruwp.TouchRuWpMorda.touchRuWp;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeCookie;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.morda.utils.cookie.CookieUtilsFactory.cookieUtils;
import static ru.yandex.autotests.morda.utils.cookie.MordaCookieUtils.YP;
import static ru.yandex.autotests.morda.utils.cookie.parsers.y.YCookieParser.parseYpCookieToMap;
import static ru.yandex.autotests.utils.morda.ParametrizationConverter.convert;
import static ru.yandex.autotests.utils.morda.language.Language.RU;
import static ru.yandex.autotests.utils.morda.language.Language.TR;
import static ru.yandex.autotests.utils.morda.language.Language.UK;
import static ru.yandex.autotests.utils.morda.region.Region.ISTANBUL;
import static ru.yandex.autotests.utils.morda.region.Region.KIEV;
import static ru.yandex.autotests.utils.morda.region.Region.MOSCOW;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 28/02/15
 */
@Aqua.Test(title = "Clid in yp cookie")
@Features("Clid")
@Stories("Clid in yp cookie")
@RunWith(Parameterized.class)
public class ClidInYpCookieTest {
    private static final MordaWebTestsProperties CONFIG = new MordaWebTestsProperties();

    @Rule
    public AllureFeatureRule allureFeatureRule;
    private Client client;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        List<Morda<?>> data = new ArrayList<>();

        String scheme = CONFIG.getMordaScheme();
        String environment = CONFIG.getMordaEnvironment();
        String userAgentTouchIphone = CONFIG.getMordaUserAgentTouchIphone();
        String userAgentTouchWp = CONFIG.getMordaUserAgentTouchWp();
        String userAgentPda = CONFIG.getMordaUserAgentPda();

        data.add(desktopMain(scheme, environment, MOSCOW));
        data.add(desktopFamilyMain(scheme, environment, MOSCOW));

        data.add(desktopYaru(scheme, environment));

        data.addAll(DesktopComMorda.getDefaultList(scheme, environment));

        data.add(desktopFirefox(scheme, environment, MOSCOW, RU));
        data.add(desktopFirefox(scheme, environment, KIEV, UK));
        data.add(desktopFirefox(scheme, environment, ISTANBUL, TR));


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

        return convert(MordaType.filter(data, CONFIG.getMordaPagesToTest()));
    }

    private Morda<?> morda;

    public ClidInYpCookieTest(Morda<?> morda) {
        this.morda = morda;
        this.client = MordaDefaultClient.getDefaultClient();
        this.allureFeatureRule = new AllureFeatureRule(morda.getFeature());
    }

    @Test
    public void clidFoundInCookieYP() {
        String clid = "123456";

        get(client, morda.getUrl().toString());

        get(client,
                fromUri(morda.getUrl())
                        .queryParam("clid", clid)
                        .build()
                        .toString()
        );

        shouldSeeCookie(client, YP, morda.getCookieDomain()).run();

        shouldSeeClidInCookieYp(clid);
    }

    @Test
    public void clidWithHyphenFoundInCookieYP() {
        String clid = "123-456";

        get(client, morda.getUrl().toString());

        get(client,
                fromUri(morda.getUrl())
                        .queryParam("clid", clid)
                        .build()
                        .toString()
        );

        shouldSeeCookie(client, YP, morda.getCookieDomain()).run();

        shouldSeeClidInCookieYp(clid);
    }

    @Test
    public void clidCanBeOverriddenInCookieYP() {
        String clid1 = "123456";
        String clid2 = "654321";

        get(client, morda.getUrl().toString());

        get(client,
                fromUri(morda.getUrl())
                        .queryParam("clid", clid1)
                        .build()
                        .toString()
        );

        get(client,
                fromUri(morda.getUrl())
                        .queryParam("clid", clid2)
                        .build()
                        .toString()
        );

        shouldSeeCookie(client, YP, morda.getCookieDomain()).run();

        shouldSeeClidInCookieYp(clid2);
    }

    @Step("Should see clid in yp cookie")
    public void shouldSeeClidInCookieYp(String clid) {
        YpCookieValue clh = parseYpCookieToMap(
                cookieUtils(client).getCookieNamed(YP, morda.getCookieDomain()).getValue()).get("clh");

        shouldSeeElementMatchingTo(clh, notNullValue()).run();
        shouldSeeElementMatchingTo(clh.getValue(), equalTo(clid)).run();
    }

    @Step("Get \"{1}\"")
    public void get(Client client, String url) {
        client.target(url)
                .request()
                .header("No-Redirect", "1")
                .buildGet()
                .invoke()
                .close();
    }
}
