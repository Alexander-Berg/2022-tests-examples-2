package ru.yandex.autotests.morda.tests.set.lang;

import com.jayway.restassured.response.Response;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.api.MordaClient;
import ru.yandex.autotests.morda.beans.cleanvars.MordaCleanvars;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.MordaLanguage;
import ru.yandex.autotests.morda.rules.allure.AllureLoggingRule;
import ru.yandex.autotests.morda.steps.set.SetSteps;
import ru.yandex.autotests.morda.tests.MordaTestsProperties;
import ru.yandex.geobase.regions.GeobaseRegion;
import ru.yandex.qatools.allure.annotations.Features;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.morda.pages.MordaLanguage.BE;
import static ru.yandex.autotests.morda.pages.MordaLanguage.EN;
import static ru.yandex.autotests.morda.pages.MordaLanguage.KK;
import static ru.yandex.autotests.morda.pages.MordaLanguage.RU;
import static ru.yandex.autotests.morda.pages.MordaLanguage.TT;
import static ru.yandex.autotests.morda.pages.MordaLanguage.UK;
import static ru.yandex.autotests.morda.pages.com.DesktopComMorda.desktopCom;
import static ru.yandex.autotests.morda.pages.comtr.DesktopComTrMorda.desktopComTr;
import static ru.yandex.autotests.morda.pages.main.DesktopMainMorda.desktopMain;
import static ru.yandex.geobase.regions.Belarus.MINSK;
import static ru.yandex.geobase.regions.Kazakhstan.ASTANA;
import static ru.yandex.geobase.regions.Russia.MOSCOW;
import static ru.yandex.geobase.regions.Ukraine.KYIV;

/**
 * User: asamar
 * Date: 17.10.16
 */
@Aqua.Test(title = "Potral set language")
@Features({"Portal Set", "Lang"})
@RunWith(Parameterized.class)
public class SetLanguageTest {
    private static MordaTestsProperties CONFIG = new MordaTestsProperties();
    @Rule
    public AllureLoggingRule allureLoggingRule = new AllureLoggingRule();

    @Parameterized.Parameters(name = "{0} {1}")
    public static Collection<Object[]> data() {
        List<Object[]> data = new ArrayList<>();

        String env = CONFIG.pages().getEnvironment();

        List<MordaLanguage> langs = asList(RU, UK, EN, KK, BE, TT);//,/*AZ*/ TR, HY, KA, RO, DE, ID, UZ);

        List<GeobaseRegion> regions = asList(MOSCOW, ASTANA, MINSK, KYIV);

        langs.forEach(lang -> {
                    regions.forEach(region ->
                                    data.add(new Object[]{lang, desktopMain(env).region(region)})
                    );
                    data.add(new Object[]{lang, desktopCom(env)});
                    data.add(new Object[]{lang, desktopComTr(env)});
                }
        );

        return data;
    }

    private MordaLanguage language;
    private SetSteps user;
    private Morda<?> morda;
    private Response response;

    public SetLanguageTest(MordaLanguage language, Morda<?> morda) {
        this.language = language;
        this.morda = morda;
        this.user = new SetSteps();
    }

    @Before
    public void init() throws IOException {
        MordaClient mordaClient = new MordaClient();
        MordaCleanvars cleanvars = mordaClient.cleanvars(morda.getUrl()).read();

        this.response = mordaClient
                .set(morda.getUrl())
                .lang(cleanvars.getSk(), language, morda.getUrl().toString())
                .readAsResponse();
    }

    @Test
    public void setLang() {
        user.shouldSeeLanguage(response, language);
    }

    //        org.apache.http.client.CookieStore cookieStore = new BasicCookieStore();
//
//        BasicClientCookie clientCookie = new BasicClientCookie("yandexuid", "4877238241477924781");
//        clientCookie.setDomain("yandex.ru");
//
//        cookieStore.addCookie(clientCookie);
//        HttpClient client = HttpClientBuilder.create().build();
//
//        HttpClientContext context = new HttpClientContext();
//        context.setCookieStore(cookieStore);
//
//        client.execute(
//                new HttpGet("https://www-rc.yandex.ru/portal/set/lang/?retpath=https%3A%2F%2Fwww-rc.yandex.ru&sk=y83da08fd9463065b31469bd8a10b39ed&intl=kk")
//                ,context
//        );
//
//        cookieStore.getCookies().stream().forEach(e -> System.out.println(e.getName() + "=" + e.getValue()));
}
