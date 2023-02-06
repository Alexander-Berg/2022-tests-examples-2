package ru.yandex.autotests.morda.monitorings.cleanvars;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.api.cleanvars.MordaCleanvarsBlock;
import ru.yandex.autotests.morda.beans.cleanvars.MordaCleanvars;
import ru.yandex.autotests.morda.beans.cleanvars.servicesblock.ServicesBlock;
import ru.yandex.autotests.morda.monitorings.MonitoringsData;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.geobase.regions.GeobaseRegion;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.monitoring.golem.GolemEvent;
import ru.yandex.qatools.monitoring.golem.GolemObject;
import ru.yandex.qatools.monitoring.yasm.YasmSignal;

import java.util.*;

import static ru.yandex.autotests.morda.api.cleanvars.MordaCleanvarsBlock.SERVICES;
import static ru.yandex.autotests.morda.pages.main.DesktopMainMorda.desktopMain;
import static ru.yandex.autotests.morda.pages.main.TouchMainMorda.touchMain;
import static ru.yandex.autotests.morda.pages.tv.TvSmartMorda.tvSmart;
import static ru.yandex.geobase.regions.Russia.MOSCOW;
import static ru.yandex.qatools.monitoring.TestCaseResult.Status.BROKEN;
import static ru.yandex.qatools.monitoring.TestCaseResult.Status.SKIPPED;

/**
 * User: asamar
 * Date: 16.09.16
 */
@Aqua.Test(title = "Services cleanvars Monitoring")
@Features("Services")
@RunWith(Parameterized.class)
@GolemObject("portal_yandex_services")
public class ServicesCleanvarsMonitoring extends BaseCleanvarsMonitoring<ServicesBlock> {

    public ServicesCleanvarsMonitoring(Morda<?> morda) {
        super(morda);
    }

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Morda<?>> data() {
        List<Morda<?>> data = new ArrayList<>();

        String env = CONFIG.getEnvironment();

        for (GeobaseRegion region : MonitoringsData.SERVICES_REGIONS) {
            data.add(desktopMain(env).region(region));
            data.add(tvSmart(env).region(region));
            if (region.getKubrDomain().equals(".ru")) {
                data.add(touchMain(env).region(MOSCOW));
            }
        }
        return data;
    }

    @Override
    public ServicesBlock getBlock() {
        return cleanvars.getServices();
    }

    @Override
    public int getShow() {
        return getBlock().getShow();
    }

    @Test
    @Override
    @GolemEvent("morda_exists")
    @YasmSignal(signal = "morda_services_exists_%s_tttt")
    public void exists() {
        super.exists();
    }

    @Test
    @GolemEvent("morda_ping")
    @YasmSignal(signal = "morda_services_ping_%s_tttt", statuses = {SKIPPED, BROKEN})
    public void pings() {
        super.pings("morda_services_ping_%s_tttt");
    }

    @Override
    public Set<String> getUrlsToPing(MordaCleanvars cleanvars) {
        Set<String> urls = new HashSet<>();

        ServicesBlock services = getBlock();

        services.getHash().get2().forEach(
                e -> {
                    urls.add(e.getUrl());
                    urls.add(e.getUrltext());
                }
        );

        return urls;
    }

    @Override
    public MordaCleanvarsBlock getBlockName() {
        return SERVICES;
    }
}
