package ru.yandex.autotests.morda.exports.tests;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.RuleChain;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.exports.MordaExportEntry;
import ru.yandex.autotests.morda.exports.tests.checks.ExportCheck;
import ru.yandex.autotests.morda.exports.tests.checks.ExportChecks;
import ru.yandex.autotests.morda.rules.allure.AllureFeatureRule;
import ru.yandex.autotests.morda.rules.allure.AllureStoryRule;
import ru.yandex.qatools.allure.annotations.Attachment;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.List;
import java.util.function.Supplier;

/**
 * User: asamar
 * Date: 13.08.2015.
 */
@Aqua.Test(title = "Exports test")
@RunWith(Parameterized.class)
public class ExportsTest {
    public static final ExportsTestsProperties CONFIG = new ExportsTestsProperties();
    @Rule
    public RuleChain ruleChain;
    private Supplier<Void> supplier;
    private Object entry;

    public <T> ExportsTest(String exportName, T entry, ExportCheck<T> exportCheck) {
        this.entry = entry;
        this.ruleChain = RuleChain.outerRule(new AllureFeatureRule(exportName))
                .around(new AllureStoryRule(exportCheck.getStory()));
        this.supplier = () -> {
            exportCheck.accept(entry);
            return null;
        };
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
                ExportChecks.getSignRealtyV2Checks()
        );

        for (ExportChecks<?, ?> checks : CONFIG.filter(exportChecks)) {
            data.addAll(checks.getChecks(CONFIG.getMordaHost(), CONFIG.isExportPingLinks()));
        }
        return data;
    }

    @Attachment(value = "Entry", type = "application/json")
    public static String attachEntry(MordaExportEntry entry) throws JsonProcessingException {
        return new ObjectMapper().writerWithDefaultPrettyPrinter()
                .writeValueAsString(entry.getJson());
    }

    @Before
    public void attach() throws JsonProcessingException {
        if (entry instanceof MordaExportEntry) {
            attachEntry((MordaExportEntry) entry);
        }
    }

    @Test
    public void check() {
        supplier.get();
    }
}
