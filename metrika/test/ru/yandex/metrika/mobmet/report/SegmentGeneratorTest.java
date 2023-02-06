package ru.yandex.metrika.mobmet.report;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.collect.ImmutableList;
import org.apache.commons.lang3.tuple.Pair;
import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.ExpectedException;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.metrika.api.WrongParameterException;
import ru.yandex.metrika.mobmet.report.generator.SegmentGenerator;
import ru.yandex.metrika.mobmet.report.model.frontend.FrontendParams;
import ru.yandex.metrika.mobmet.report.model.frontend.MobmetFrontendParamsParser;
import ru.yandex.metrika.util.io.IOUtils;
import ru.yandex.metrika.util.io.UncheckedIOException;
import ru.yandex.metrika.util.json.ObjectMappersFactory;

import static org.junit.Assert.assertEquals;

@RunWith(Parameterized.class)
public class SegmentGeneratorTest {

    public final static ObjectMapper mapper = ObjectMappersFactory.getDefaultMapper();

    private final static List<String> TEST_PATHS = Arrays.asList(
            "invariants/invert",
            "invariants/connect/invert",
            "invariants/connect/invert_partial",

            "user/install/install_dates",
            "user/install/install_geo",
            "user/install/install_campaign",
            "user/install/install_publisher",
            "user/install/install_tracker_params",
            "user/install/install_app_version",
            "user/install/install_dates_composition",
            "user/install/install_dates_two_items_composition",
            "user/install/connect",
            "user/install/connect_complex",

            "user/reengagement/reengagement_dates",
            "user/reengagement/reengagement_geo",
            "user/reengagement/reengagement_campaign",
            "user/reengagement/reengagement_publisher",
            "user/reengagement/reengagement_tracker_params",
            "user/reengagement/reengagement_app_version",
            "user/reengagement/reengagement_dates_composition",
            "user/reengagement/reengagement_dates_two_items_composition",
            "user/reengagement/connect",
            "user/reengagement/connect_complex",

            "user/open/open_dates",
            "user/open/open_campaign",
            "user/open/open_publisher",
            "user/open/open_tracker_params",
            "user/open/open_dates_composition",
            "user/open/connect",
            "user/open/connect_complex",

            "user/push/push_control",
            "user/push/push_delivered",
            "user/push/push_missed",
            "user/push/push_opened",
            "user/push/push_sent",
            "user/push/push_sent_many",

            "user/push_v2/push_control",
            "user/push_v2/push_delivered",
            "user/push_v2/push_missed",
            "user/push_v2/push_opened",
            "user/push_v2/push_sent",
            "user/push_v2/push_sent_many",

            "user/user_client_events/and",
            "user/user_client_events/and_invert",
            "user/user_client_events/or",
            "user/user_client_events/or_invert",
            "user/user_client_events/many",
            "user/user_client_events/only_path",
            "user/user_client_events/number_comparision",
            "user/user_client_events/interval",

            "user/demography/user_age",
            "user/demography/user_gender",

            "user/current/user_geo",
            "user/current/user_app_version",
            "user/current/user_build_number",
            "user/current/user_app_id",
            "user/current/user_client_kit_version",
            "user/current/user_os",
            "user/current/user_device_brand",
            "user/current/user_device_model",
            "user/current/user_device_type",
            "user/current/user_resolution",
            "user/current/user_locale",
            "user/current/user_root",
            "user/current/connect",

            "user/metrics/days_since_install",
            "user/metrics/days_since_last_visit",
            "user/metrics/sessions_count",
            "user/metrics/push_notification_opened",
            "user/metrics/crashes_count",
            "user/metrics/sessions_count_interval",

            "user/nda/user_device",
            "user/nda/user_device_id",
            "user/nda/user_google_aid",
            "user/nda/user_ios_ifa",
            "user/nda/user_limit_ad_tracking",

            "user/start/start_dates",
            "user/start/start_dates_composition",

            "user/profile/profile_id",
            "user/profile/bool_attribute",
            "user/profile/name_attribute",
            "user/profile/notifications_attribute",
            "user/profile/number_attribute",
            "user/profile/string_attribute",
            "user/profile/counter_attribute",
            "user/profile/connect",

            "user/revenue/revenue_currency",
            "user/revenue/revenue_dates",
            "user/revenue/revenue_geo",
            "user/revenue/revenue_order_id",
            "user/revenue/revenue_payload",
            "user/revenue/revenue_product_id",
            "user/revenue/revenue_verified",
            "user/revenue/revenue_total_sum",

            "common/common_app_id",
            "common/common_app_version",
            "common/common_build_number",
            "common/common_client_events",
            "common/common_client_events_invert",
            "common/common_client_events_and",
            "common/common_client_events_and_invert",
            "common/common_client_events_or",
            "common/common_client_events_or_invert",
            "common/common_client_events_many",
            "common/common_client_kit_version",
            "common/common_connection_type",
            "common/common_device_brand",
            "common/common_device_model",
            "common/common_geo",
            "common/common_locale",
            "common/common_network_type",
            "common/common_operator",
            "common/common_os",
            "common/common_resolution",
            "common/common_root",
            "common/common_session_duration"
    );

    @Rule
    public ExpectedException expectedException = ExpectedException.none();

    @Parameterized.Parameter
    public String name;
    @Parameterized.Parameter(1)
    public ReportType target;
    @Parameterized.Parameter(2)
    public String segment;
    @Parameterized.Parameter(3)
    public String expectedFilter;

    @Test
    public void testFilters() {
        FrontendParams parsedSegment = new MobmetFrontendParamsParser().parse(segment);

        SegmentGenerator generator = new SegmentGeneratorsFactory(SegmentGeneratorMocks.emptyPushMetaService())
                .build()
                .get(target);

        if ("is not supported".equals(expectedFilter)) {
            expectedException.expect(WrongParameterException.class);
        }

        String actualFilter = generator.generate(parsedSegment.toInternal());
        assertEquals(expectedFilter, actualFilter);
    }

    @Parameterized.Parameters(name = "Params: {0}, report type: {1}")
    public static Collection<Object[]> init() {
        ImmutableList.Builder<Object[]> builder = ImmutableList.builder();
        TEST_PATHS.forEach(path -> {
            try {
                String params = IOUtils.resourceAsString(SegmentGeneratorTest.class, "params/" + path + "/params.json");
                String expected = IOUtils.resourceAsString(SegmentGeneratorTest.class, "params/" + path + "/expected.json");

                List<Pair<ReportType, String>> expectedByTarget = parseExpected(expected);

                Map<ReportType, String> segments = new HashMap<>();
                Arrays.stream(ReportType.values()).forEach(reportType -> segments.put(reportType, ""));
                expectedByTarget.forEach(expectedForTarget -> segments.put(expectedForTarget.getLeft(), expectedForTarget.getRight()));

                segments.forEach((reportType, segment) -> builder.add(params(path, reportType, params, segment)));
            } catch (Exception ex) {
                throw new IllegalStateException("Can't handle " + path, ex);
            }
        });
        return builder.build();
    }

    private static Object[] params(Object... params) {
        return params;
    }

    private static List<Pair<ReportType, String>> parseExpected(String file) {
        try {
            JsonNode root = mapper.readTree(file);
            List<Pair<ReportType, String>> result = new ArrayList<>();
            root.fields().forEachRemaining(entry ->
                    result.add(Pair.of(ReportType.of(entry.getKey()), entry.getValue().asText())));
            return result;
        } catch (IOException ex) {
            throw new UncheckedIOException(ex);
        }
    }
}
