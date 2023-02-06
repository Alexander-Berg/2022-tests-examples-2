package ru.yandex.autotests.morda.monitorings.cleanvars;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.api.cleanvars.MordaCleanvarsBlock;
import ru.yandex.autotests.morda.beans.cleanvars.MordaCleanvars;
import ru.yandex.autotests.morda.beans.cleanvars.afisha.Afisha;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.MordaLanguage;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.monitoring.golem.GolemEvent;
import ru.yandex.qatools.monitoring.golem.GolemObject;
import ru.yandex.qatools.monitoring.yasm.YasmSignal;

import java.util.*;

import static org.hamcrest.Matchers.*;
import static org.junit.Assert.assertThat;
import static org.junit.Assume.assumeThat;
import static ru.yandex.autotests.morda.api.cleanvars.MordaCleanvarsBlock.AFISHA;
import static ru.yandex.autotests.morda.monitorings.MonitoringsData.AFISHA_REGIONS;
import static ru.yandex.autotests.morda.pages.main.DesktopMainMorda.desktopMain;
import static ru.yandex.autotests.morda.pages.main.PdaMainMorda.pdaMain;
import static ru.yandex.autotests.morda.pages.main.TouchMainMorda.touchMain;
import static ru.yandex.qatools.monitoring.TestCaseResult.Status.BROKEN;
import static ru.yandex.qatools.monitoring.TestCaseResult.Status.SKIPPED;

/**
 * User: asamar
 * Date: 15.09.16
 */
@Aqua.Test(title = "Afisha cleanvars monitoring")
@Features("Afisha")
@RunWith(Parameterized.class)
@GolemObject("portal_yandex_afisha")
public class AfishaCleanvarsMonitoring extends BaseCleanvarsMonitoring<Afisha> {

    public AfishaCleanvarsMonitoring(Morda<?> morda) {
        super(morda);
    }

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Morda<?>> data() {
        List<Morda<?>> data = new ArrayList<>();

        String env = CONFIG.getEnvironment();

        AFISHA_REGIONS.forEach(region -> {
            data.add(desktopMain(env).region(region).language(MordaLanguage.RU));
            data.add(touchMain(env).region(region).language(MordaLanguage.RU));
            data.add(pdaMain(env).region(region).language(MordaLanguage.RU));
        });

        return data;
    }

    @Override
    public Afisha getBlock() {
        return cleanvars.getAfisha();
    }

    @Override
    public int getShow() {
        return this.getBlock().getShow();
    }

    @Override
    public MordaCleanvarsBlock getBlockName() {
        return AFISHA;
    }

    @Override
    public Set<String> getUrlsToPing(MordaCleanvars cleanvars) {
        Set<String> urls = new HashSet<>();

        urls.add(cleanvars.getAfisha().getHref());
        urls.add(cleanvars.getAfisha().getSearchUrl());

        cleanvars.getAfisha().getEvents()
                .forEach(e -> urls.add(e.getRawHref()));

        if (cleanvars.getAfisha().getPremiere() != null) {
            urls.add(cleanvars.getAfisha().getPremiere().getHref());
        }
        return urls;
    }

    @Test
    @Override
    @GolemEvent("morda_exists")
    @YasmSignal(signal = "morda_afisha_exists_%s_tttt")
    public void exists() {
        super.exists();
    }

    @Test
    @GolemEvent("morda_ping")
    @YasmSignal(signal = "morda_afisha_ping_%s_tttt", statuses = {SKIPPED, BROKEN})
    public void pings() {
        super.pings("morda_afisha_ping_%s_tttt");
    }

    @Test
    @GolemEvent("morda_events_count")
    @YasmSignal(signal = "morda_afisha_events_count_%s_tttt")
    public void eventsCount() {
        assumeThat(getShow(), equalTo(1));

        assertThat("Too few events", getBlock().getEvents(), hasSize(greaterThan(1)));
    }

}
