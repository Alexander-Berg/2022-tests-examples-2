package ru.yandex.autotests.morda.tests.set.lang;

import com.jayway.restassured.response.Response;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.api.MordaClient;
import ru.yandex.autotests.morda.api.set.MordaSetClient;
import ru.yandex.autotests.morda.beans.cleanvars.MordaCleanvars;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.rules.allure.AllureLoggingRule;
import ru.yandex.autotests.morda.steps.set.SetSteps;
import ru.yandex.autotests.morda.tests.MordaTestsProperties;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.morda.api.set.SetError.BAD_LANG;
import static ru.yandex.autotests.morda.api.set.SetError.BAD_RETPATH;
import static ru.yandex.autotests.morda.api.set.SetError.BAD_SK;
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
 * Date: 18.10.16
 */
@Aqua.Test(title = "Potral set language with errors")
@Features({"Portal Set", "Lang"})
@RunWith(Parameterized.class)
public class SetLanguageWithErrorsTest {
    private static MordaTestsProperties CONFIG = new MordaTestsProperties();
    @Rule
    public AllureLoggingRule rule = new AllureLoggingRule();

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        List<Object[]> data = new ArrayList<>();

        String env = CONFIG.pages().getEnvironment();

        asList(MOSCOW, MINSK, ASTANA, KYIV)
                .forEach(region -> data.add(new Object[]{desktopMain(env).region(region)}));

        data.add(new Object[]{desktopCom(env)});
        data.add(new Object[]{desktopComTr(env)});

        return data;
    }

    private SetSteps userLanguage;
    private Morda<?> morda;
    private MordaSetClient set;
    private MordaCleanvars cleanvars;

    public SetLanguageWithErrorsTest(Morda<?> morda) {
        this.morda = morda;
        this.userLanguage = new SetSteps();
    }

    @Before
    public void init() {
        MordaClient mordaClient = new MordaClient();
        this.cleanvars = mordaClient.cleanvars(morda.getUrl()).read();
        this.set = mordaClient
                .set(morda.getUrl());
    }

    @Test
    public void setEmptyLang() {
        Response response = set
                .lang(cleanvars.getSk(), "", morda.getUrl().toString())
                .readAsResponse();

        userLanguage.shouldSeeError(response, BAD_LANG);
    }

    @Test
    public void setUnknownLang() {
        Response response = set.lang(cleanvars.getSk(), "gfds", morda.getUrl().toString())
                .readAsResponse();

        userLanguage.shouldSeeError(response, BAD_LANG);
    }

    @Test
    public void setLangWithBadRetpath() {
        Response response = set.lang(cleanvars.getSk(), UK, "https://mail.ru")
                .readAsResponse();

        userLanguage.shouldSeeError(response, BAD_RETPATH);
    }

    @Test
    public void setLangWithBadSk() {
        String sk = "y0d9ce139692fb126627d697010d1a7";
        Response response = set.lang(sk, UK, morda.getUrl().toString())
                .readAsResponse();

        userLanguage.shouldSeeError(response, BAD_SK);
    }
}
