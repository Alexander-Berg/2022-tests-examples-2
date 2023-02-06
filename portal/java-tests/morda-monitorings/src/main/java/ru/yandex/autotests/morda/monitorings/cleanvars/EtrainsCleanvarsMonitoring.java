package ru.yandex.autotests.morda.monitorings.cleanvars;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.api.cleanvars.MordaCleanvarsBlock;
import ru.yandex.autotests.morda.beans.cleanvars.MordaCleanvars;
import ru.yandex.autotests.morda.beans.cleanvars.etrains.Etrains;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.monitoring.golem.GolemEvent;
import ru.yandex.qatools.monitoring.golem.GolemObject;
import ru.yandex.qatools.monitoring.graphite.GraphiteMetricPrefix;
import ru.yandex.qatools.monitoring.yasm.YasmSignal;

import java.util.ArrayList;
import java.util.Collection;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import static java.util.Arrays.asList;
import static org.hamcrest.Matchers.greaterThan;
import static org.junit.Assert.assertThat;
import static ru.yandex.autotests.morda.api.cleanvars.MordaCleanvarsBlock.ETRAINS;
import static ru.yandex.autotests.morda.pages.main.DesktopMainMorda.desktopMain;
import static ru.yandex.geobase.regions.Belarus.ORSHA;
import static ru.yandex.geobase.regions.Kazakhstan.TEMIRTAU;
import static ru.yandex.geobase.regions.Russia.DUBNA;
import static ru.yandex.geobase.regions.Russia.VYBORG;
import static ru.yandex.geobase.regions.Ukraine.BROVARY;
import static ru.yandex.qatools.monitoring.TestCaseResult.Status.BROKEN;
import static ru.yandex.qatools.monitoring.TestCaseResult.Status.SKIPPED;

/**
 * User: asamar
 * Date: 02.11.16
 */
@Aqua.Test(title = "Etrains cleanvars monitoring")
@Features("Etrains")
@RunWith(Parameterized.class)
@GolemObject("portal_yandex_etrains")
public class EtrainsCleanvarsMonitoring extends BaseCleanvarsMonitoring<Etrains> {

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Morda<?>> data() {
        List<Morda<?>> data = new ArrayList<>();

        asList(DUBNA, VYBORG, BROVARY, ORSHA, TEMIRTAU)
                .forEach(region -> data.add(
                                desktopMain(CONFIG.getEnvironment()).region(region))
                );

        return data;
    }


    public EtrainsCleanvarsMonitoring(Morda<?> morda) {
        super(morda);
    }

    @Override
    public MordaCleanvarsBlock getBlockName() {
        return ETRAINS;
    }

    @Override
    public Etrains getBlock() {
        return cleanvars.getEtrains();
    }

    @Override
    public int getShow() {
        return getBlock().getShow();
    }

    @Test
    @Override
    @GolemEvent("morda_exists")
    @YasmSignal(signal = "morda_etrains_exists_%s_tttt")
    public void exists() {
        super.exists();
    }

    @Test
    @GolemEvent("morda_ping")
    @YasmSignal(signal = "morda_etrains_ping_%s_tttt", statuses = {SKIPPED, BROKEN})
    public void pings() {
        super.pings("morda_etrains_ping_%s_tttt");
    }


    @Override
    public Set<String> getUrlsToPing(MordaCleanvars cleanvars) {
        Set<String> urls = new HashSet<>();

        Etrains etrains = cleanvars.getEtrains();

        urls.add(etrains.getHref());
        urls.add(etrains.getHrefBack());
        urls.add(etrains.getRaspHost());
        urls.add(etrains.getRaspHostBigRu());

        etrains.getFctd().forEach(e -> urls.add(e.getUrl()));
        etrains.getFctm().forEach(e -> urls.add(e.getUrl()));
        etrains.getTctd().forEach(e -> urls.add(e.getUrl()));
        etrains.getTctm().forEach(e -> urls.add(e.getUrl()));

        return urls;
    }
}
