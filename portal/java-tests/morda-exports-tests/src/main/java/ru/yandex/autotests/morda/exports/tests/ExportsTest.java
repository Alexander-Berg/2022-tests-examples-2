package ru.yandex.autotests.morda.exports.tests;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.RuleChain;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.exports.AbstractMordaExport;
import ru.yandex.autotests.morda.exports.interfaces.Entry;
import ru.yandex.autotests.morda.exports.tests.checks.ExportCheck;
import ru.yandex.autotests.morda.exports.tests.checks.ExportChecks;
import ru.yandex.autotests.morda.exports.tests.checks.RegionTranslationsCheck;
import ru.yandex.autotests.morda.rules.allure.AllureFeatureRule;
import ru.yandex.autotests.morda.rules.allure.AllureLoggingRule;
import ru.yandex.autotests.morda.rules.allure.AllureStoryRule;
import ru.yandex.qatools.allure.annotations.Attachment;
import ru.yandex.qatools.allure.annotations.Features;

import java.net.URI;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.TimeUnit;

import static java.util.concurrent.Executors.newFixedThreadPool;
import static ru.yandex.autotests.morda.pages.main.DesktopMainMorda.desktopMain;

/**
 * User: asamar
 * Date: 13.08.2015.
 */
@Aqua.Test(title = "Exports test")
@RunWith(Parameterized.class)
@Features("MADM")
public class ExportsTest<T extends AbstractMordaExport<T, E>, E extends Entry> {
    public static final ExportsTestsProperties CONFIG = new ExportsTestsProperties();

    @Rule
    public RuleChain ruleChain;
    private AbstractMordaExport<T, E> export;
    private ExecutorService entryCheckPool;
    private ExportCheck<E> exportCheck;

    public ExportsTest(String exportName, AbstractMordaExport<T, E> export, ExportCheck<E> exportCheck) {
        this.export = export;
        this.exportCheck = exportCheck;
        this.entryCheckPool = newFixedThreadPool(20);
        this.ruleChain = RuleChain.outerRule(new AllureFeatureRule(exportName))
                .around(new AllureStoryRule(exportCheck.getStory()))
                .around(new AllureLoggingRule());
    }

    @Parameterized.Parameters(name = "{0}, {2}")
    public static Collection<Object[]> data() {
        List<Object[]> data = new ArrayList<>();

        List<ExportChecks> exportChecks = Arrays.asList(
                ExportChecks.getGeoPanoramsChecks(),
                ExportChecks.getMapsChecks(),
                ExportChecks.getGeoRoutesChecks(),
                ExportChecks.getSignTaxiV2Checks(),
                ExportChecks.getSignTravelV2Checks(),
                ExportChecks.getSignAutoV2Checks(),
                ExportChecks.getSignAutoruV2Checks(),
                ExportChecks.getSignBrowserV2Checks(),
                ExportChecks.getSignMarketV2Checks(),
                ExportChecks.getSignMasterV2Checks(),
                ExportChecks.getSignMusicV2Checks(),
                ExportChecks.getSignRabotaV2Checks(),
                ExportChecks.getSignRealtyV2Checks(),
                ExportChecks.getSignAutoruTouchV2Checks(),
                ExportChecks.getSignAviaV2Checks(),
                ExportChecks.getSignImagesV2Checks(),
                ExportChecks.getSignKinopoiskV2Checks(),
                ExportChecks.getSignKinopoiskOldV2Checks(),
                ExportChecks.getSignMoneyV2Checks(),
                ExportChecks.getSignRabotaTouchV2Checks(),
                ExportChecks.getSignRadioV2Checks(),
                ExportChecks.getSignRealtyTouchV2Checks(),
                ExportChecks.getSignSearchV2Checks(),
                ExportChecks.getSignTaxiTouchV2Checks(),
                ExportChecks.getSignTravelTouchV2Checks(),
                ExportChecks.getSignVideoV2Checks(),
                ExportChecks.getSignMarketTouchV2Checks()

        );

        URI mordaHost = desktopMain(CONFIG.getEnvironment()).getUrl();

        for (ExportChecks<?, ?> checks : CONFIG.filter(exportChecks)) {
            data.addAll(checks.getChecks(mordaHost, CONFIG.isExportPingLinks()));
        }

        return data;
    }

    @Test
    public void check() throws JsonProcessingException, InterruptedException {
        Map<Object, String> errors = new ConcurrentHashMap<>();

        if (exportCheck instanceof RegionTranslationsCheck) {
            RegionTranslationsCheck translationsCheck = (RegionTranslationsCheck) exportCheck;
            try {
                translationsCheck.accept(export);
            } catch (AssertionError e) {
                errors.put(translationsCheck.getStory(), e.getMessage());
            }
        } else {
            export.getData().stream()
                    .filter(e -> exportCheck.getCondition().test(e))
                    .forEach(r -> entryCheckPool.submit(() -> {
                        try {
                            exportCheck.accept(r);
                        } catch (AssertionError e) {
                            errors.put(r, e.getMessage());
                        }
                    }));

            entryCheckPool.shutdown();
            entryCheckPool.awaitTermination(100, TimeUnit.SECONDS);
        }

        if (!errors.isEmpty()) {
            attach(getEnrtyErrors(errors));
            throw new AssertionError(exportCheck.getStory() + " is failed");
        }
    }


    private String getEnrtyErrors(Map<Object, String> errors) {
        StringBuilder data = new StringBuilder();

        errors.forEach((k, v) -> {

            data.append("------------------------------ ENTRY ------------------------------\n");
            try {
                if (k instanceof Entry) {
                    Entry entry = (Entry) k;
                    data.append(new ObjectMapper().writerWithDefaultPrettyPrinter()
                            .writeValueAsString(entry.getJson()));
                }
            } catch (JsonProcessingException e1) {
                data.append("Error when trying to attach entry");
            }
            data.append("\n------------------------------ ERROR ------------------------------\n");
            data.append(v + "\n\n\n\n");
        });

        return data.toString();
    }

    @Attachment(value = "errors", type = "application/json")
    public static String attach(String entry) {
        System.out.println(entry);
        return entry;
    }
}
