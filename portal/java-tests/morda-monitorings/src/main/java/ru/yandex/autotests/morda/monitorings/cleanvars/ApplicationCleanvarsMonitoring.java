package ru.yandex.autotests.morda.monitorings.cleanvars;

import org.apache.log4j.Logger;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.api.cleanvars.MordaCleanvarsBlock;
import ru.yandex.autotests.morda.beans.cleanvars.MordaCleanvars;
import ru.yandex.autotests.morda.beans.cleanvars.application.Application;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.main.TouchMainMorda;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.monitoring.golem.GolemEvent;
import ru.yandex.qatools.monitoring.golem.GolemObject;
import ru.yandex.qatools.monitoring.yasm.YasmSignal;

import java.util.*;

import static ru.yandex.autotests.morda.api.cleanvars.MordaCleanvarsBlock.APPLICATION;
import static ru.yandex.qatools.monitoring.TestCaseResult.Status.BROKEN;
import static ru.yandex.qatools.monitoring.TestCaseResult.Status.SKIPPED;

/**
 * User: asamar
 * Date: 15.09.16
 */
@Aqua.Test(title = "Application cleanvars monitorings")
@Features("Applications")
@RunWith(Parameterized.class)
@GolemObject("portal_yandex_application")
public class ApplicationCleanvarsMonitoring extends BaseCleanvarsMonitoring<Application> {
    private static final Logger LOGGER = Logger.getLogger(ApplicationCleanvarsMonitoring.class);

    public ApplicationCleanvarsMonitoring(Morda<?> morda) {
        super(morda);
    }

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Morda<?>> data() {
        List<Morda<?>> data = new ArrayList<>();

        data.addAll(TouchMainMorda.getDefaultList(CONFIG.getEnvironment()));

        return data;
    }

    @Override
    public Application getBlock() {
        return cleanvars.getApplication();
    }

    @Override
    public int getShow() {
        return this.getBlock().getShow();
    }

    @Override
    public MordaCleanvarsBlock getBlockName() {
        return APPLICATION;
    }

    @Test
    @Override
    @GolemEvent("morda_exists")
    @YasmSignal(signal = "morda_applications_exists_%s_tttt")
    public void exists() {
        super.exists();
    }

    @Test
    @GolemEvent("morda_ping")
    @YasmSignal(signal = "morda_applications_ping_%s_tttt", statuses = {SKIPPED, BROKEN})
    public void pings() {
        super.pings("morda_applications_ping_%s_tttt");
    }

    @Override
    public Set<String> getUrlsToPing(MordaCleanvars cleanvars) {
        Set<String> urls = new HashSet<>();

        Application application = cleanvars.getApplication();

        application.getList().forEach(e -> {
            urls.add(e.getIcon());
            urls.add(e.getIconSvg());
            urls.add(e.getUrl());
        });

        return urls;
    }


}
