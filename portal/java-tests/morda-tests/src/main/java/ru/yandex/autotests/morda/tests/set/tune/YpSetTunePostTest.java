package ru.yandex.autotests.morda.tests.set.tune;

import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.pages.Morda;
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
 * Date: 07.11.16
 */
@Aqua.Test(title = "Check YP cookie POST")
@Features({"Portal Set", "Tune"})
@RunWith(Parameterized.class)
public class YpSetTunePostTest extends BaseSetTuneTest {
    private static MordaTestsProperties CONFIG = new MordaTestsProperties();

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
            data.add(new Object[]{morda, "yes_mtd", "0", "mtd.1"});
            data.add(new Object[]{morda, "new_window", "0", "sp.tg:_self"});
        });

        return data;
    }

    public YpSetTunePostTest(Morda<?> morda, String param, String value, String ypSubstring) {
        super(morda, param, value);
        setTunePost();
        this.checker = (response -> user.ypShouldContains(ypSubstring, response));
    }
}
