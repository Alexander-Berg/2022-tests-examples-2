package ru.yandex.metrika.mobmet.climetr;

import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import org.junit.Before;
import org.junit.Test;

import ru.yandex.metrika.api.constructor.presets.PresetService;
import ru.yandex.metrika.api.constructor.presets.PresetSource;
import ru.yandex.metrika.api.constructor.presets.PresetsTreeNodeService;
import ru.yandex.metrika.mobmet.climetr.meta.config.ClimetrWidgetsConfig;
import ru.yandex.metrika.mobmet.climetr.meta.config.ClimetrWidgetsConfigFactory;
import ru.yandex.metrika.mobmet.climetr.meta.config.Dashboard;
import ru.yandex.metrika.mobmet.climetr.meta.config.DashboardWidget;
import ru.yandex.metrika.mobmet.climetr.meta.config.ReportNode;
import ru.yandex.metrika.segments.apps.schema.MobmetTableSchema;
import ru.yandex.metrika.segments.core.schema.TableMeta;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * По хорошему эти проверки должны выполнятся и при запуске демона. Но пресеты почему то
 * живут прямо в ядре, при этом мы их локализуем в сервисе {@link PresetService#afterPropertiesSet()}.
 * В итоге у нас как бы много наборов пресетов для каждого языка и каждый такой одинаковый набор не
 * хочется проверять. Ещё пресеты зачем то используются в ConstructorService. А мета виджетов нет.
 * Хотя кажется, что пресеты ничем особенным не отличаются от виджетов, но судьбы у них почему то разные.
 */
public class ClimetrConfigTest {

    private List<PresetSource> presets;
    private ClimetrWidgetsConfig config;
    private List<String> tableIds;

    @Before
    public void setUp() {
        PresetsTreeNodeService treeNodeService = PresetsTreeNodeService.appTreeNodeService();
        presets = treeNodeService.presetsSources();
        config = new ClimetrWidgetsConfigFactory().create();

        MobmetTableSchema tableSchema = new MobmetTableSchema();
        tableIds = tableSchema.values().stream()
                .map(TableMeta::toID)
                .collect(Collectors.toList());
    }

    @Test
    public void testDashboardConsistency() {
        testDashboardConsistencyCommon(config.getDashboard());
    }

    @Test
    public void testAgencyDashboardConsistency() {
        testDashboardConsistencyCommon(config.getAgencyDashboard());
    }

    private void testDashboardConsistencyCommon(Dashboard dashboard) {
        dashboard.getWidgets().forEach(widget -> {
            PresetSource preset = findPreset(widget.getPreset(), presets);
            if (widget.getDimension() != null) {
                assertThat(preset.getDimensions()).contains(widget.getDimension());
            }
            assertThat(widget.getMetric()).isNotNull();
            assertThat(preset.getMetrics()).contains(widget.getMetric());
        });

        List<Integer> ids = dashboard.getWidgets().stream().map(DashboardWidget::getId).collect(Collectors.toList());
        List<Integer> idsWithoutDuplicates = ids.stream().distinct().collect(Collectors.toList());

        assertThat(ids).hasSize(idsWithoutDuplicates.size());
    }

    @Test
    public void testReportConsistency() {
        testReportConsistencyCommon(config.getReports());
    }

    @Test
    public void testAgencyReportConsistency() {
        testReportConsistencyCommon(config.getAgencyReports());
    }

    private void testReportConsistencyCommon(ReportNode reportNode) {
        if (reportNode.getPreset() == null) {
            assertThat(reportNode.getItems()).isNotEmpty();
            reportNode.getItems().forEach(this::testReportConsistencyCommon);
            return;
        }
        assertThat(reportNode.getItems()).isNull();
        assertThat(findPreset(reportNode.getPreset(), presets)).isNotNull();
    }

    @Test
    public void testPresetConsistency() {
        presets.forEach(preset -> {
            assertThat(preset.getSort()).isNotNull();
            assertThat(Stream.concat(preset.getMetrics().stream(), preset.getDimensions().stream()))
                    .contains(metricToCanonical(preset.getSort()));
            assertThat(tableIds).contains(preset.getTable());
        });
    }

    private static String metricToCanonical(String metric) {
        return metric.startsWith("-") ? metric.substring(1) : metric;
    }

    private static PresetSource findPreset(String name, List<PresetSource> presets) {
        List<PresetSource> matched = presets.stream()
                .filter(preset -> name.equals(preset.getName()))
                .collect(Collectors.toList());
        assertThat(matched).hasSize(1);
        return matched.get(0);
    }
}
