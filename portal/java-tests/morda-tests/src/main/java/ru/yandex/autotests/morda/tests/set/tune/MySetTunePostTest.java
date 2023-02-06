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
@Aqua.Test(title = "Check MY cookie POST")
@Features({"Portal Set", "Tune"})
@RunWith(Parameterized.class)
public class MySetTunePostTest extends BaseSetTuneTest {
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
            data.add(new Object[]{morda, "big_version", "1", "YywBAQA="});
            data.add(new Object[]{morda, "no_interest_ad", "1", "YyYBAQA="});
            data.add(new Object[]{morda, "no_main_banner", "1", "Yy4BAQA="});
            data.add(new Object[]{morda, "no_geo_ad", "1", "YzoBAQA="});
            data.add(new Object[]{morda, "no_app_by_links", "1", "YzsBAQA="});
            data.add(new Object[]{morda, "yes_interest_ad", "0", "YyYBAQA="});
            data.add(new Object[]{morda, "yes_main_banner", "0", "Yy4BAQA="});
            data.add(new Object[]{morda, "yes_geo_ad", "0", "YzoBAQA="});
            data.add(new Object[]{morda, "mobile_version", "0", "YywBAQA="});
            data.add(new Object[]{morda, "yes_app_by_links", "0", "YzsBAQA="});
        });

        return data;
    }

    public MySetTunePostTest(Morda<?> morda, String param, String value, String expectedMy) {
        super(morda, param, value);
        setTunePost();
        this.checker = (response -> user.shouldSeeMyCookie(expectedMy, response));
    }
}
