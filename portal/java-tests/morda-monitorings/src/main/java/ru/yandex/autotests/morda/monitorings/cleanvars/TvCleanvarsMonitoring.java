package ru.yandex.autotests.morda.monitorings.cleanvars;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.api.cleanvars.MordaCleanvarsBlock;
import ru.yandex.autotests.morda.beans.cleanvars.MordaCleanvars;
import ru.yandex.autotests.morda.beans.cleanvars.tv.Tv;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.geobase.regions.GeobaseRegion;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.monitoring.golem.GolemEvent;
import ru.yandex.qatools.monitoring.golem.GolemObject;
import ru.yandex.qatools.monitoring.yasm.YasmSignal;

import java.util.*;

import static org.junit.Assume.assumeTrue;
import static ru.yandex.autotests.morda.api.cleanvars.MordaCleanvarsBlock.TV;
import static ru.yandex.autotests.morda.monitorings.MonitoringsData.TV_REGIONS;
import static ru.yandex.autotests.morda.pages.hw.DesktopHwLgMorda.desktopHwLg;
import static ru.yandex.autotests.morda.pages.main.DesktopMainMorda.desktopMain;
import static ru.yandex.autotests.morda.pages.main.PdaMainMorda.pdaMain;
import static ru.yandex.autotests.morda.pages.main.TouchMainMorda.touchMain;
import static ru.yandex.autotests.morda.pages.tv.TvSmartMorda.tvSmart;
import static ru.yandex.qatools.monitoring.TestCaseResult.Status.BROKEN;
import static ru.yandex.qatools.monitoring.TestCaseResult.Status.SKIPPED;

/**
 * User: asamar
 * Date: 19.09.16
 */
@Aqua.Test(title = "Tv cleanvars Monitoring")
@Features("Tv")
@RunWith(Parameterized.class)
@GolemObject("portal_yandex_tv")
public class TvCleanvarsMonitoring extends BaseCleanvarsMonitoring<Tv> {
    public TvCleanvarsMonitoring(Morda<?> morda) {
        super(morda);
    }

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Morda<?>> data() {
        List<Morda<?>> data = new ArrayList<>();

        String env = CONFIG.getEnvironment();

        for (GeobaseRegion region : TV_REGIONS) {
            data.add(desktopMain(env).region(region));
            data.add(touchMain(env).region(region));
            data.add(pdaMain(env).region(region));
            data.add(tvSmart(env).region(region));
            data.add(desktopHwLg(env).region(region));
        }

        return data;
    }

    @Override
    public MordaCleanvarsBlock getBlockName() {
        return TV;
    }

    @Override
    public Tv getBlock() {
        return cleanvars.getTv();
    }

    @Override
    public int getShow() {
        return getBlock().getShow();
    }

    @Test
    @Override
    @GolemEvent("morda_exists")
    @YasmSignal(signal = "morda_tv_exists_%s_tttt")
    public void exists() {
        super.exists();
    }

    @Test
    @GolemEvent("morda_ping")
    @YasmSignal(signal = "morda_tv_ping_%s_tttt", statuses = {SKIPPED, BROKEN})
    public void pings() {
        super.pings("morda_tv_ping_%s_tttt");
    }

    @Override
    public Set<String> getUrlsToPing(MordaCleanvars cleanvars) {
        Tv tv = cleanvars.getTv();
        assumeTrue("Нет блока ТВ на Морде", tv != null && tv.getShow() == 1);

        Set<String> links = new HashSet<>();

        links.add(tv.getHref());

        tv.getAnnounces()
                .forEach(e -> links.add(e.getUrl()));
        tv.getProgramms()
                .forEach(e -> {
                    links.add(e.getHref());
                    links.add(e.getChHref());
                });

        tv.getTabs().forEach(e -> {
            links.add(e.getHref());
            e.getProgramms().forEach(p -> {
                links.add(p.getHref());
                links.add(p.getChHref());
            });
        });

        return links;
    }
}
