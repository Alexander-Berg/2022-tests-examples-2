package ru.yandex.autotests.morda.tests.set.tune;

import com.jayway.restassured.response.Response;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.api.MordaClient;
import ru.yandex.autotests.morda.api.set.MordaSetClient;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.rules.allure.AllureLoggingRule;
import ru.yandex.autotests.morda.steps.set.SetSteps;
import ru.yandex.autotests.morda.tests.MordaTestsProperties;
import ru.yandex.qatools.allure.annotations.Features;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.morda.api.set.SetError.BAD_SK;
import static ru.yandex.autotests.morda.pages.com.DesktopComMorda.desktopCom;
import static ru.yandex.autotests.morda.pages.comtr.DesktopComTrMorda.desktopComTr;
import static ru.yandex.autotests.morda.pages.main.DesktopMainMorda.desktopMain;
import static ru.yandex.geobase.regions.Belarus.MINSK;
import static ru.yandex.geobase.regions.Kazakhstan.ASTANA;
import static ru.yandex.geobase.regions.Russia.MOSCOW;
import static ru.yandex.geobase.regions.Ukraine.KYIV;

/**
 * User: asamar
 * Date: 14.11.16
 */
@Aqua.Test(title = "Potral set tune with errors")
@Features({"Portal Set", "Tune"})
@RunWith(Parameterized.class)
public class SetTuneWithErrorsTest {

    private static MordaTestsProperties CONFIG = new MordaTestsProperties();
    @Rule
    public AllureLoggingRule rule = new AllureLoggingRule();

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        List<Object[]> data = new ArrayList<>();

        String env = CONFIG.pages().getEnvironment();

        asList(MOSCOW, KYIV, ASTANA, MINSK).forEach(e ->
                data.add(new Object[]{desktopMain(env).region(e)}));

        data.add(new Object[]{desktopCom(env)});
        data.add(new Object[]{desktopComTr(env)});

        return data;
    }

    private SetSteps user;
    private MordaSetClient set;
    private Morda<?> morda;

    public SetTuneWithErrorsTest(Morda<?> morda) {
        this.morda = morda;
        this.user = new SetSteps();
    }

    @Before
    public void init() throws IOException {
        MordaClient mordaClient = new MordaClient();
        mordaClient.cleanvars(morda, "sk").read();
        this.set = mordaClient
                .set(morda.getUrl());
    }

    @Test
     public void getWithBadSk() {
        String sk = "y96b0a98d9ba665f3588398de260b16c";
        String paramName = "no_app_by_links";
        String paramValue = "1";

        Response response = set.tuneGet(sk, paramName, paramValue, morda.getUrl().toString()).readAsResponse();
        user.shouldSeeError(response, BAD_SK);
    }

    @Test
    public void postWithBadSk() {
        String sk = "y96b0a98d9ba665f3588398de260b16c";
        String paramName = "yes_mtd";
        String paramValue = "0";

        Response response = set.tunePost(sk, paramName, paramValue, morda.getUrl().toString()).readAsResponse();
        user.shouldSeeError(response, BAD_SK);
    }
}
