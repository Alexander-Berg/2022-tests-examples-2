package ru.yandex.autotests.morda.tests.set.any;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.api.MordaClient;
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
import static ru.yandex.autotests.morda.pages.main.DesktopMainMorda.desktopMain;
import static ru.yandex.geobase.regions.Belarus.MINSK;
import static ru.yandex.geobase.regions.Kazakhstan.ASTANA;
import static ru.yandex.geobase.regions.Russia.MOSCOW;
import static ru.yandex.geobase.regions.Ukraine.KYIV;

/**
 * User: asamar
 * Date: 27.10.16
 */
@Aqua.Test(title = "Potral set any with errors")
@Features({"Portal Set", "Any"})
@RunWith(Parameterized.class)
public class SetAnyWithErrorsTest {
    private static MordaTestsProperties CONFIG = new MordaTestsProperties();
    @Rule
    public AllureLoggingRule allureLoggingRule = new AllureLoggingRule();

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Morda<?>> data() {
        List<Morda<?>> data = new ArrayList<>();

        String env = CONFIG.pages().getEnvironment();

        asList(MOSCOW, KYIV, MINSK, ASTANA).forEach(region -> data.add(desktopMain(env).region(region)));

        return data;
    }

    private SetSteps user;
    private Morda<?> morda;
    private com.jayway.restassured.response.Response response;
    private static final String SK = "y3a26dced020a80c37c97fd71ed072dd";

    public SetAnyWithErrorsTest(Morda<?> morda) {
        this.user = new SetSteps();
        this.morda = morda;
    }

    @Before
    public void init() throws IOException {
        MordaClient mordaClient = new MordaClient();
        mordaClient.cleanvars(morda.getUrl()).read();
        this.response = mordaClient
                .set(morda.getUrl())
                .any(SK, "af", "1", morda.getUrl().toString())
                .readAsResponse();
    }

    @Test
    public void setAnyWithSk() {
        user.shouldSeeError(response, BAD_SK);
    }
}
