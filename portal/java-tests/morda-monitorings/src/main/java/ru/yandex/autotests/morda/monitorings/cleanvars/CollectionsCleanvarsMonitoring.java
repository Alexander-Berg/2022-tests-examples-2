package ru.yandex.autotests.morda.monitorings.cleanvars;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.api.cleanvars.MordaCleanvarsBlock;
import ru.yandex.autotests.morda.beans.cleanvars.MordaCleanvars;
import ru.yandex.autotests.morda.beans.cleanvars.collections.Collections;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.MordaLanguage;
import ru.yandex.geobase.regions.Russia;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.monitoring.golem.GolemEvent;
import ru.yandex.qatools.monitoring.golem.GolemObject;
import ru.yandex.qatools.monitoring.yasm.YasmSignal;

import java.util.*;

import static ru.yandex.autotests.morda.monitorings.MonitoringsData.COLLECTIONS_REGIONS;
import static ru.yandex.autotests.morda.pages.main.TouchMainMorda.touchMain;
import static ru.yandex.qatools.monitoring.TestCaseResult.Status.BROKEN;
import static ru.yandex.qatools.monitoring.TestCaseResult.Status.SKIPPED;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 31/12/16
 */
@Aqua.Test(title = "Collections monitoring")
@Features("Collections")
@RunWith(Parameterized.class)
@GolemObject("portal_yandex_collections")
public class CollectionsCleanvarsMonitoring extends BaseCleanvarsMonitoring<Collections> {
    public CollectionsCleanvarsMonitoring(Morda<?> morda) {
        super(morda);
    }

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Morda<?>> data() {
        List<Morda<?>> data = new ArrayList<>();

        String env = CONFIG.getEnvironment();

        COLLECTIONS_REGIONS.forEach(region -> {
            data.add(touchMain(env).region(Russia.MOSCOW).language(MordaLanguage.RU));
        });

        return data;
    }

    @Override
    public Collections getBlock() {
        return cleanvars.getCollections();
    }

    @Override
    public int getShow() {
        return getBlock().getShow();
    }

    @Override
    public MordaCleanvarsBlock getBlockName() {
        return MordaCleanvarsBlock.COLLECTIONS;
    }

    @Override
    public Set<String> getUrlsToPing(MordaCleanvars cleanvars) {
        Set<String> urls = new HashSet<>();
        Collections collections = cleanvars.getCollections();

        collections.getList().forEach(e -> urls.add(e.getLink()));

        return urls;
    }

    @Test
    @Override
    @GolemEvent("morda_exists")
    @YasmSignal(signal = "morda_collections_exists_%s_tttt")
    public void exists() {
        super.exists();
    }

    @Test
    @GolemEvent("morda_ping")
    @YasmSignal(signal = "morda_collections_ping_%s_tttt", statuses = {SKIPPED, BROKEN})
    public void pings() {
        super.pings("morda_collections_ping_%s_tttt");
    }

}
