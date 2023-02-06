package ru.yandex.autotests.morda.monitorings.cleanvars;

import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.api.cleanvars.MordaCleanvarsBlock;
import ru.yandex.autotests.morda.beans.cleanvars.MordaCleanvars;
import ru.yandex.autotests.morda.beans.cleanvars.bridges.Bridges;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.geobase.regions.Russia;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.monitoring.golem.GolemObject;

import java.util.*;

import static ru.yandex.autotests.morda.api.cleanvars.MordaCleanvarsBlock.BRIDGES;
import static ru.yandex.autotests.morda.pages.main.TouchMainMorda.touchMain;

/**
 * User: asamar
 * Date: 16.09.16
 */
@Aqua.Test(title = "Bridges cleanvars monitoring")
@Features("Bridges")
@RunWith(Parameterized.class)
@GolemObject("portal_yandex_bridges")
public class BridgesCleanvarsMonitoring extends BaseCleanvarsMonitoring<Bridges> {
    public BridgesCleanvarsMonitoring(Morda<?> morda) {
        super(morda);
    }

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Morda<?>> data() {
        List<Morda<?>> data = new ArrayList<>();

        data.add(
                touchMain(CONFIG.getEnvironment())
                        .region(Russia.SAINT_PETERSBURG));

        return data;
    }

    @Override
    public Bridges getBlock() {
        return cleanvars.getBridges();
    }

    @Override
    public int getShow() {
        return getBlock().getShow();
    }

    @Override
    public Set<String> getUrlsToPing(MordaCleanvars cleanvars) {
        return new HashSet<>();
    }

    @Override
    public MordaCleanvarsBlock getBlockName() {
        return BRIDGES;
    }
}
