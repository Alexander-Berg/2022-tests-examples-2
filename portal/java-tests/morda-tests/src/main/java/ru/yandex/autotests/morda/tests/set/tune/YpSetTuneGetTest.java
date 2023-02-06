package ru.yandex.autotests.morda.tests.set.tune;

import org.junit.Rule;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.rules.allure.AllureLoggingRule;
import ru.yandex.autotests.morda.tests.MordaTestsProperties;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.morda.pages.com.DesktopComMorda.desktopCom;
import static ru.yandex.autotests.morda.pages.comtr.DesktopComTrMorda.desktopComTr;
import static ru.yandex.autotests.morda.pages.main.DesktopMainMorda.desktopMain;
import static ru.yandex.geobase.regions.Belarus.MINSK;
import static ru.yandex.geobase.regions.Kazakhstan.ASTANA;
import static ru.yandex.geobase.regions.Russia.MOSCOW;
import static ru.yandex.geobase.regions.Ukraine.KYIV;

/**
 * User: asamar
 * Date: 20.10.16
 */
@Aqua.Test(title = "Check YP cookie GET")
@Features({"Portal Set", "Tune"})
@RunWith(Parameterized.class)
public class YpSetTuneGetTest extends BaseSetTuneTest {
    private static MordaTestsProperties CONFIG = new MordaTestsProperties();
    @Rule
    public AllureLoggingRule rule = new AllureLoggingRule();

    @Parameterized.Parameters(name = "{1} = {2} {0}")
    public static Collection<Object[]> data() {
        List<Object[]> data = new ArrayList<>();

        String env = CONFIG.pages().getEnvironment();

        List<Morda<?>> mordas = new ArrayList<>();
        asList(MOSCOW, KYIV, MINSK, ASTANA)
                .forEach(region -> mordas.add(desktopMain(env).region(region)));
        mordas.add(desktopCom(env));
        mordas.add(desktopComTr(env));

        mordas.forEach(morda -> {
            data.add(new Object[]{morda, "mtd", "1", "mtd.1"});
            data.add(new Object[]{morda, "ygd", "1", "ygd.1"});
            data.add(new Object[]{morda, "self_window", "1", "sp.tg:_sel"});
            data.add(new Object[]{morda, "family", "1", "sp.family:2"});
        });

        return data;
    }

    public YpSetTuneGetTest(Morda<?> morda, String param, String value, String ypSubstring) {
        super(morda, param, value);
        setTuneGet();
        this.checker = response -> user.ypShouldContains(ypSubstring, response);
    }

}
