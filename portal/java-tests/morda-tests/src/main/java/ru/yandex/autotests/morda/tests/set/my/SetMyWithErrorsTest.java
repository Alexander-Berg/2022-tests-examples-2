package ru.yandex.autotests.morda.tests.set.my;

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

import java.io.IOException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.morda.api.set.SetError.BAD_BLOCK;
import static ru.yandex.autotests.morda.api.set.SetError.BAD_SK;
import static ru.yandex.autotests.morda.api.set.SetError.NO_BLOCK;
import static ru.yandex.autotests.morda.pages.com.DesktopComMorda.desktopCom;
import static ru.yandex.autotests.morda.pages.comtr.DesktopComTrMorda.desktopComTr;
import static ru.yandex.autotests.morda.pages.main.DesktopMainMorda.desktopMain;
import static ru.yandex.geobase.regions.Belarus.MINSK;
import static ru.yandex.geobase.regions.Kazakhstan.ASTANA;
import static ru.yandex.geobase.regions.Russia.MOSCOW;
import static ru.yandex.geobase.regions.Ukraine.KYIV;

/**
 * User: asamar
 * Date: 28.10.16
 */
@Aqua.Test(title = "Potral set my with errors")
@Features({"Portal Set", "My"})
@RunWith(Parameterized.class)
public class SetMyWithErrorsTest {

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
    private MordaCleanvars cleanvars;
    private MordaSetClient set;
    private Morda<?> morda;

    public SetMyWithErrorsTest(Morda<?> morda) {
        this.morda = morda;
        this.user = new SetSteps();
    }

    @Before
    public void init() throws IOException {
        MordaClient mordaClient = new MordaClient();
        this.cleanvars = mordaClient.cleanvars(morda.getUrl()).read();

        this.set = mordaClient
                .set(morda.getUrl());
    }

    @Test
    public void emptyBlock() {
        String param = "2";
        String block = "";

        Response response = set.my(cleanvars.getSk(), param, block, morda.getUrl().toString()).readAsResponse();
        user.shouldSeeError(response, NO_BLOCK);
    }

    @Test
    public void noBlock() {
        String param = "3";

        Response response = set.my(cleanvars.getSk(), param, morda.getUrl().toString()).readAsResponse();
        user.shouldSeeError(response, NO_BLOCK);
    }

    @Test
    public void unknownBlock() {
        String param = "qqq";
        String block = "aaa";

        Response response = set.my(cleanvars.getSk(), param, block, morda.getUrl().toString()).readAsResponse();
        user.shouldSeeError(response, BAD_BLOCK);
    }

    @Test
    public void badSk() {
        String param = "2";
        String block = "39";
        String sk = "y3a26dced020a80c37c97fd71ed072dd";

        Response response = set.my(sk, param, block, morda.getUrl().toString()).readAsResponse();
        user.shouldSeeError(response, BAD_SK);
    }

}
