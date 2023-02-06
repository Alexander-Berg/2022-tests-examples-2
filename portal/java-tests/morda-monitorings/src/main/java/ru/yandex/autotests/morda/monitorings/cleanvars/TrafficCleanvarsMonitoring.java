package ru.yandex.autotests.morda.monitorings.cleanvars;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.api.cleanvars.MordaCleanvarsBlock;
import ru.yandex.autotests.morda.beans.cleanvars.MordaCleanvars;
import ru.yandex.autotests.morda.beans.cleanvars.traffic.Traffic;
import ru.yandex.autotests.morda.monitorings.MonitoringsData;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.MordaType;
import ru.yandex.geobase.regions.GeobaseRegion;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.monitoring.golem.GolemEvent;
import ru.yandex.qatools.monitoring.golem.GolemObject;
import ru.yandex.qatools.monitoring.yasm.YasmSignal;

import java.util.*;

import static java.util.Arrays.asList;
import static org.hamcrest.CoreMatchers.notNullValue;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.junit.Assume.assumeFalse;
import static ru.yandex.autotests.morda.api.cleanvars.MordaCleanvarsBlock.TRAFFIC;
import static ru.yandex.autotests.morda.pages.MordaDomain.*;
import static ru.yandex.autotests.morda.pages.comtr.DesktopComTrFootballMorda.FootballClub.BJK;
import static ru.yandex.autotests.morda.pages.comtr.DesktopComTrFootballMorda.FootballClub.GS;
import static ru.yandex.autotests.morda.pages.comtr.DesktopComTrFootballMorda.desktopComTrFoot;
import static ru.yandex.autotests.morda.pages.comtr.DesktopComTrMorda.desktopComTr;
import static ru.yandex.autotests.morda.pages.comtr.PdaComTrMorda.pdaComTr;
import static ru.yandex.autotests.morda.pages.comtr.TouchComTrMorda.touchComTr;
import static ru.yandex.autotests.morda.pages.hw.DesktopHwBmwMorda.desktopHwBmw;
import static ru.yandex.autotests.morda.pages.hw.DesktopHwLgMorda.desktopHwLg;
import static ru.yandex.autotests.morda.pages.main.DesktopFirefoxMorda.desktopFirefox;
import static ru.yandex.autotests.morda.pages.main.DesktopMainMorda.desktopMain;
import static ru.yandex.autotests.morda.pages.main.PdaMainMorda.pdaMain;
import static ru.yandex.autotests.morda.pages.main.TouchMainMorda.touchMain;
import static ru.yandex.autotests.morda.pages.tv.TvSmartMorda.tvSmart;
import static ru.yandex.geobase.regions.Turkey.ISTANBUL_11508;
import static ru.yandex.qatools.monitoring.TestCaseResult.Status.BROKEN;
import static ru.yandex.qatools.monitoring.TestCaseResult.Status.SKIPPED;

/**
 * User: asamar
 * Date: 16.09.16
 */
@Aqua.Test(title = "Traffic cleanvars Monitoring")
@Features("Traffic")
@RunWith(Parameterized.class)
@GolemObject("portal_yandex_traffic")
public class TrafficCleanvarsMonitoring extends BaseCleanvarsMonitoring<Traffic> {
    private static final List<MordaType> SKIP_PING_LIST = asList(MordaType.PDA_COMTR, MordaType.PDA_MAIN);

    public TrafficCleanvarsMonitoring(Morda<?> morda) {
        super(morda);
    }

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Morda<?>> data() {
        List<Morda<?>> data = new ArrayList<>();

        String env = CONFIG.getEnvironment();

        for (GeobaseRegion region : MonitoringsData.TRAFFIC_REGIONS) {
            data.add(desktopMain(env).region(region));
            data.add(touchMain(env).region(region));
            data.add(pdaMain(env).region(region));
            data.add(desktopHwBmw(env).region(region));
            data.add(desktopHwLg(env).region(region));
            data.add(tvSmart(env).region(region));
            data.add(desktopFirefox(RU, env).region(ISTANBUL_11508));
            data.add(desktopFirefox(UA, env).region(ISTANBUL_11508));
        }

        data.add(desktopComTr(env).region(ISTANBUL_11508));
        data.add(desktopComTrFoot(BJK, env).region(ISTANBUL_11508));
        data.add(desktopComTrFoot(GS, env).region(ISTANBUL_11508));
        data.add(desktopFirefox(COM_TR, env).region(ISTANBUL_11508));
        data.add(touchComTr(env).region(ISTANBUL_11508));
        data.add(pdaComTr(env).region(ISTANBUL_11508));

        return data;
    }

    @Override
    public Traffic getBlock() {
        return cleanvars.getTraffic();
    }

    @Override
    public int getShow() {
        assertThat("Пропал балл блок пробок на Морде", getBlock().getRate(), notNullValue());
        return getBlock().getShow();
    }

    @Test
    @Override
    @GolemEvent("morda_exists")
    @YasmSignal(signal = "morda_traffic_exists_%s_tttt")
    public void exists() {
        super.exists();
    }

    @Test
    @GolemEvent("morda_ping")
    @YasmSignal(signal = "morda_traffic_ping_%s_tttt", statuses = {SKIPPED, BROKEN})
    public void pings() {
        assumeFalse("No urls in pda", SKIP_PING_LIST.contains(morda.getMordaType()));
        super.pings("morda_traffic_ping_%s_tttt");
    }

    @Override
    public Set<String> getUrlsToPing(MordaCleanvars cleanvars) {
        Set<String> urls = new HashSet<>();

        Traffic traffic = cleanvars.getTraffic();

        urls.add(traffic.getHref());
        urls.add(traffic.getPromoUrl());
//        urls.add(traffic.getMobile().getUrl());

        return urls;
    }

    @Override
    public MordaCleanvarsBlock getBlockName() {
        return TRAFFIC;
    }
}
