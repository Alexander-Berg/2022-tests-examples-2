package ru.yandex.autotests.morda.tests.set.any;

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
import ru.yandex.autotests.morda.rules.allure.AllureLoggingRule;
import ru.yandex.autotests.morda.steps.set.SetSteps;
import ru.yandex.autotests.morda.tests.MordaTestsProperties;
import ru.yandex.qatools.allure.annotations.Features;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.morda.pages.main.DesktopMainMorda.desktopMain;
import static ru.yandex.geobase.regions.Belarus.MINSK;
import static ru.yandex.geobase.regions.Kazakhstan.ASTANA;
import static ru.yandex.geobase.regions.Russia.MOSCOW;
import static ru.yandex.geobase.regions.Ukraine.KYIV;

/**
 * User: asamar
 * Date: 19.10.16
 */
@Aqua.Test(title = "Potral set any")
@Features({"Portal Set", "Any"})
@RunWith(Parameterized.class)
public class SetAnyTest {
    private static MordaTestsProperties CONFIG = new MordaTestsProperties();
    @Rule
    public AllureLoggingRule allureLoggingRule = new AllureLoggingRule();

    @Parameterized.Parameters(name = "{0}={1} {2}")
    public static Collection<Object[]> data() {
        List<Object[]> data = new ArrayList<>();

        String env = CONFIG.pages().getEnvironment();

        asList(MOSCOW, KYIV, MINSK, ASTANA).forEach(region -> {

            Morda<?> morda = desktopMain(env).region(region);

            asList("af", "afn", "beeb", "csc", "hkd", "hwb", "msb", "mtb", "mu",
                    "mv", "obp", "trf", "vd", "ybp", "ygp", "bdst", "ac", "dq")
                    .forEach(e -> data.add(new Object[]{e, "1", morda}));

            data.add(new Object[]{"apps", "mail-1", morda});
            data.add(new Object[]{"clh", "234-567", morda});
            data.add(new Object[]{"cr", "ua", morda});
            data.add(new Object[]{"hk", "m410316", morda});
            data.add(new Object[]{"nt", "culture", morda});
            data.add(new Object[]{"stst", "min", morda});
            data.add(new Object[]{"szm", "1:233x234:3432x23423", morda});
        });
        return data;
    }

    private String paramName;
    private String paramValue;
    private SetSteps user;
    private Morda<?> morda;
    private Response response;

    public SetAnyTest(String paramName, String paramValue, Morda<?> morda) {
        this.paramName = paramName;
        this.paramValue = paramValue;
        this.morda = morda;
        this.user = new SetSteps();
    }

    @Before
    public void init() throws IOException {
        MordaClient mordaClient = new MordaClient();
        MordaCleanvars cleanvars = mordaClient.cleanvars(morda.getUrl()).read();

        this.response = mordaClient
                .set(morda.getUrl())
                .any(cleanvars.getSk(), paramName, paramValue, morda.getUrl().toString())
                .readAsResponse();
    }

    @Test
    public void setAny() {
        user.ypShouldContains(response, paramName, paramValue);
    }

}
