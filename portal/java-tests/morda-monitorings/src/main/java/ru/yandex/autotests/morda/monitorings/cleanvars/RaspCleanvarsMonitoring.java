package ru.yandex.autotests.morda.monitorings.cleanvars;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.api.cleanvars.MordaCleanvarsBlock;
import ru.yandex.autotests.morda.beans.cleanvars.MordaCleanvars;
import ru.yandex.autotests.morda.beans.cleanvars.rasp.Rasp;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.MordaLanguage;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.monitoring.golem.GolemEvent;
import ru.yandex.qatools.monitoring.golem.GolemObject;
import ru.yandex.qatools.monitoring.yasm.YasmSignal;

import java.util.*;

import static org.hamcrest.Matchers.greaterThan;
import static org.junit.Assert.assertThat;
import static ru.yandex.autotests.morda.api.cleanvars.MordaCleanvarsBlock.RASP;
import static ru.yandex.autotests.morda.monitorings.MonitoringsData.RASP_REGIONS;
import static ru.yandex.autotests.morda.pages.main.PdaMainMorda.pdaMain;
import static ru.yandex.autotests.morda.pages.main.TouchMainMorda.touchMain;
import static ru.yandex.qatools.monitoring.TestCaseResult.Status.BROKEN;
import static ru.yandex.qatools.monitoring.TestCaseResult.Status.SKIPPED;

/**
 * User: asamar
 * Date: 15.09.16
 */
@Aqua.Test(title = "Rasp cleanvars monitoring")
@Features("Rasp")
@RunWith(Parameterized.class)
@GolemObject("portal_yandex_rasp")
public class RaspCleanvarsMonitoring extends BaseCleanvarsMonitoring<Rasp> {

    public RaspCleanvarsMonitoring(Morda<?> morda) {
        super(morda);
    }

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Morda<?>> data() {
        List<Morda<?>> data = new ArrayList<>();

        String env = CONFIG.getEnvironment();

        RASP_REGIONS.forEach(region -> {
            data.add(touchMain(env).region(region).language(MordaLanguage.RU));
            data.add(pdaMain(env).region(region).language(MordaLanguage.RU));
        });

        return data;
    }

    @Override
    public Rasp getBlock() {
        return cleanvars.getRasp();
    }

    @Override
    public int getShow() {
        return this.getBlock().getShow();
    }

    @Override
    public MordaCleanvarsBlock getBlockName() {
        return RASP;
    }

    @Override
    public Set<String> getUrlsToPing(MordaCleanvars cleanvars) {
        Rasp rasp = getBlock();
        Set<String> urls = new HashSet<>();

        rasp.getList().forEach(e -> urls.add(e.getUrl()));

        return urls;
    }

    @Test
    @Override
    @GolemEvent("morda_exists")
    @YasmSignal(signal = "morda_rasp_exists_%s_tttt")
    public void exists() {
        super.exists();
        assertThat("No rasp items found", getBlock().getList().size(), greaterThan(0));
    }

    @Test
    @GolemEvent("morda_ping")
    @YasmSignal(signal = "morda_rasp_ping_%s_tttt", statuses = {SKIPPED, BROKEN})
    public void pings() {
        super.pings("morda_rasp_ping_%s_tttt");
    }

}
