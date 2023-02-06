package ru.yandex.autotests.morda.monitorings.cleanvars;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.api.cleanvars.MordaCleanvarsBlock;
import ru.yandex.autotests.morda.beans.cleanvars.MordaCleanvars;
import ru.yandex.autotests.morda.beans.cleanvars.teaser.Teaser;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.MordaLanguage;
import ru.yandex.autotests.morda.pages.main.DesktopFamilyMainMorda;
import ru.yandex.autotests.morda.pages.main.DesktopMainMorda;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.monitoring.golem.GolemEvent;
import ru.yandex.qatools.monitoring.yasm.YasmSignal;

import java.util.*;
import java.util.stream.Stream;

import static ru.yandex.autotests.morda.api.cleanvars.MordaCleanvarsBlock.TEASER;
import static ru.yandex.autotests.morda.pages.MordaType.TOUCH_MAIN;
import static ru.yandex.autotests.morda.pages.main.DesktopFamilyMainMorda.desktopFamilyMain;
import static ru.yandex.autotests.morda.pages.main.DesktopMainMorda.desktopMain;
import static ru.yandex.autotests.morda.pages.main.TouchMainMorda.touchMain;
import static ru.yandex.geobase.regions.Belarus.MINSK;
import static ru.yandex.geobase.regions.Belarus.VITEBSK;
import static ru.yandex.geobase.regions.Kazakhstan.ALMATY;
import static ru.yandex.geobase.regions.Kazakhstan.ASTANA;
import static ru.yandex.geobase.regions.Russia.*;
import static ru.yandex.geobase.regions.Ukraine.KYIV;
import static ru.yandex.geobase.regions.Ukraine.LVIV;
import static ru.yandex.qatools.monitoring.TestCaseResult.Status.BROKEN;
import static ru.yandex.qatools.monitoring.TestCaseResult.Status.SKIPPED;

/**
 * User: asamar
 * Date: 27.09.16
 */
@Aqua.Test(title = "Teaser cleanvars monitoring")
@Features("Teaser")
@RunWith(Parameterized.class)
public class TeaserCleanvarsMonitoring extends BaseCleanvarsMonitoring<Teaser> {
    public TeaserCleanvarsMonitoring(Morda<?> morda) {
        super(morda);
    }

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Morda<?>> data() {
        List<Morda<?>> data = new ArrayList<>();

        data.addAll(DesktopMainMorda.getDefaultList(CONFIG.getEnvironment()));
        data.addAll(DesktopFamilyMainMorda.getDefaultList(CONFIG.getEnvironment()));

        Stream.of(SAINT_PETERSBURG, YEKATERINBURG, VORONEZH, NIZHNY_NOVGOROD, ROSTOV_NA_DONU, KRASNODAR, CHELYABINSK, SAMARA,
                NOVOSIBIRSK, VOLGOGRAD, UFA, PERM, SARATOV, PETROPAVLOVSK, ASTANA, VITEBSK, LVIV)
                .forEach(region -> {
                    data.add(desktopMain(CONFIG.getEnvironment()).region(region));
                    data.add(desktopFamilyMain(CONFIG.getEnvironment()).region(region));
                });

        Stream.of(MINSK, VITEBSK, ASTANA, ALMATY, LVIV, KYIV).forEach(region ->
                data.add(touchMain(CONFIG.getEnvironment()).region(region).language(MordaLanguage.RU))
        );

        return data;
    }

    @Override
    public Teaser getBlock() {
        return cleanvars.getTeaser();
    }

    @Override
    public int getShow() {
        return getBlock().getShow();
    }


    @Override
    public MordaCleanvarsBlock getBlockName() {
        return TEASER;
    }


    @Test
    @Override
    @GolemEvent("morda_exists")
    @YasmSignal(signal = "morda_teaser_exists_%s_tttt")
    public void exists() {
        super.exists();
    }

    @Test
    @GolemEvent("morda_ping")
    @YasmSignal(signal = "morda_teaser_ping_%s_tttt", statuses = {SKIPPED, BROKEN})
    public void pings() {
        super.pings("morda_teaser_ping_%s_tttt");
    }


    @Override
    public Set<String> getUrlsToPing(MordaCleanvars cleanvars) {
        Set<String> urls = new HashSet<>();
        Teaser teaser = cleanvars.getTeaser();

        if (morda.getMordaType() != TOUCH_MAIN) {
            urls.add(teaser.getValue().getUrl().replaceAll("\\*", "%2A"));
        } else {
            urls.add(teaser.getValue().getUrl1().replaceAll("\\*", "%2A"));
            String url2 = teaser.getValue().getUrl2();
            if (url2 != null && !"".equals(url2)) urls.add(url2.replaceAll("\\*", "%2A"));
        }

        urls.add(teaser.getValue().getImg().getUrl().replaceAll("\\*", "%2A"));

        return urls;
    }
}
