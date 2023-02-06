package ru.yandex.autotests.morda.monitorings.cleanvars;

import org.apache.commons.lang3.StringUtils;
import org.apache.log4j.Logger;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.api.cleanvars.MordaCleanvarsBlock;
import ru.yandex.autotests.morda.beans.cleanvars.MordaCleanvars;
import ru.yandex.autotests.morda.beans.cleanvars.edadeal.Edadeal;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.MordaLanguage;
import ru.yandex.autotests.morda.restassured.requests.RestAssuredGetRequest;
import ru.yandex.autotests.morda.steps.attach.AttachmentUtils;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.monitoring.golem.GolemEvent;
import ru.yandex.qatools.monitoring.golem.GolemObject;
import ru.yandex.qatools.monitoring.yasm.YasmSignal;

import java.util.*;

import static java.util.stream.Collectors.joining;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.empty;
import static ru.yandex.autotests.morda.api.MordaRequestActions.prepareRequest;
import static ru.yandex.autotests.morda.monitorings.MonitoringsData.EDADEAL_REGIONS;
import static ru.yandex.autotests.morda.pages.main.TouchMainMorda.touchMain;
import static ru.yandex.qatools.monitoring.TestCaseResult.Status.BROKEN;
import static ru.yandex.qatools.monitoring.TestCaseResult.Status.SKIPPED;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 31/12/16
 */
@Aqua.Test(title = "Edadeal cleanvars monitoring")
@Features("Edadeal")
@RunWith(Parameterized.class)
@GolemObject("portal_yandex_edadeal")
public class EdadealCleanvarsMonitoring extends BaseCleanvarsMonitoring<Edadeal> {
    private static final Logger LOGGER = Logger.getLogger(EdadealCleanvarsMonitoring.class);

    public EdadealCleanvarsMonitoring(Morda<?> morda) {
        super(morda);
    }

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Morda<?>> data() {
        List<Morda<?>> data = new ArrayList<>();

        String env = CONFIG.getEnvironment();

        EDADEAL_REGIONS.forEach(region -> {
            data.add(touchMain(env).region(region).language(MordaLanguage.RU)
                    .cookie("yandexuid", "5244339571483364144"));
        });

        return data;
    }

    @Override
    public Edadeal getBlock() {
        return cleanvars.getEdadeal();
    }

    @Override
    public int getShow() {
        return getBlock().getShow();
    }

    @Override
    public MordaCleanvarsBlock getBlockName() {
        return MordaCleanvarsBlock.EDADEAL;
    }

    @Override
    public Set<String> getUrlsToPing(MordaCleanvars cleanvars) {
        Set<String> urls = new HashSet<>();
        Edadeal edadeal = cleanvars.getEdadeal();

        edadeal.getRetailers().forEach(e -> {
            urls.add(e.getShareURL());
        });

        return urls;
    }

    public Set<String> getShareUrls(MordaCleanvars cleanvars) {
        Set<String> urls = new HashSet<>();
        Edadeal edadeal = cleanvars.getEdadeal();

        edadeal.getRetailers().forEach(e -> {
            urls.add(e.getShareURL());
        });

        return urls;
    }

    @Test
    @Override
    @GolemEvent("morda_exists")
    @YasmSignal(signal = "morda_edadeal_exists_%s_tttt")
    public void exists() {
        super.exists();
    }

    @Test
    @GolemEvent("morda_ping")
    @YasmSignal(signal = "morda_edadeal_ping_%s_tttt", statuses = {SKIPPED, BROKEN})
    public void pings() {
        super.pings("morda_edadeal_ping_%s_tttt");
    }

    @Test
    @GolemEvent("morda_items")
    @YasmSignal(signal = "morda_edadeal_items_%s_tttt", statuses = {SKIPPED, BROKEN})
    public void items() {
        Set<String> urls = getShareUrls(cleanvars);

        List<String> failed = new ArrayList<>();
        List<String> passed = new ArrayList<>();

        for (String url : urls) {
            try {
                String response = prepareRequest(new RestAssuredGetRequest(url), morda)
                        .readAsResponse()
                        .asString();
                int count = StringUtils.countMatches(response, "\"p-shop__item-content\"");
                if (count > 0) {
                    passed.add(url);
                } else {
                    failed.add(url);
                }
            } catch (Exception e) {
                failed.add(url);
                LOGGER.error(e);
            }
        }

        notifierRule.yasm().addToSignal("morda_edadeal_items_passed_tttt", passed.size());
        notifierRule.yasm().addToSignal("morda_edadeal_items_failed_tttt", failed.size());

        if (failed.size() != 0) {
            AttachmentUtils.attachText("bad_shops.info", failed.stream()
                    .collect(joining("\n")));
        }

        assertThat("Some shops without actions", failed, empty());
    }
}
