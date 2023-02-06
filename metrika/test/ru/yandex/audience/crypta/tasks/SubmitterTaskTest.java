package ru.yandex.audience.crypta.tasks;

import java.util.Map;

import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import org.assertj.core.api.SoftAssertions;
import org.junit.Before;
import org.junit.Test;

import ru.yandex.audience.SegmentContentType;
import ru.yandex.audience.SegmentType;
import ru.yandex.audience.geo.GeoSegmentType;
import ru.yandex.audience.util.AudiencePropertiesService;

import static org.mockito.Matchers.any;
import static org.mockito.Mockito.doNothing;
import static org.mockito.Mockito.doReturn;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.spy;
import static ru.yandex.audience.SegmentStatus.confirmed;
import static ru.yandex.audience.SegmentStatus.few_data;
import static ru.yandex.audience.SegmentStatus.processed_fully;
import static ru.yandex.audience.SegmentStatus.processing_failed;
import static ru.yandex.audience.SegmentStatus.updated;

public class SubmitterTaskTest {

    public static final String SELECT_QUERY_COMMON = """
            SELECT segment_id, status, notified FROM segments
            WHERE
                segment_type = :type AND
                deleted = 0 AND
                (
                    last_submit_time IS NULL OR last_submit_time = 0 OR
                    (received_time IS NOT NULL AND received_time != 0 AND received_time > last_submit_time)
                ) AND
                (
                    status IN (:submitStatuses) OR
                    (
                        status IN (:resendStatuses) AND
                        (
                            (
                                status IN (:autoResendStatuses) AND
                                resend_on = 1 AND
                                NOW() > received_time + INTERVAL :resendSeconds SECOND
                            ) OR
                            (notified > 0 AND resend_on = 1) OR
                            notified > 1
                        )
                    )
               )""";

    public static final String SELECT_QUERY_NONUPLOADING = SELECT_QUERY_COMMON;
    public static final String SELECT_QUERY_GEOSEGMENT = SELECT_QUERY_COMMON + " AND geo_segment_type = :geoType";

    public static final long DEFAULT_RESEND_PERIOD = 86400L;
    private SubmitterTask submitterTask;
    private AudiencePropertiesService audiencePropertiesService;
    private long resendPeriodSeconds;

    @Before
    public void setUp() throws Exception {
        submitterTask = spy(SubmitterTask.class);
        audiencePropertiesService = mock(AudiencePropertiesService.class);
        doReturn(false).when(audiencePropertiesService).submitOnlyNew(any());
        submitterTask.setAudiencePropertiesService(audiencePropertiesService);
        doNothing().when(submitterTask).executeSubmit(any(), any(), any());
    }

    @Test
    public void generatesCorrectQueryAndParamsForUploadingSegmentsFetching() throws Exception {
        SubmitterTask.QueryParam queryParam = submitterTask.queryParamBuilder(SegmentType.uploading).asQueryParam();

        Map<String, Object> expectedParams = ImmutableMap.<String, Object>builder()
                .putAll(getCommonParams())
                .put("type", SegmentType.uploading.dbName())
                .put("resendSeconds", DEFAULT_RESEND_PERIOD)
                .put("clientIdContentType", SegmentContentType.client_id.name())
                .build();

        String expectedQuery = SELECT_QUERY_COMMON + " AND content_type != :clientIdContentType AND (valid_unique_quantity > 0 OR uploading_source_id is null OR uploading_source_id != 100)";

        assertQueryParam(expectedParams, expectedQuery, queryParam);
    }

    @Test
    public void generatesCorrectQueryAndParamsForClientIdUploadingSegmentsFetching() throws Exception {
        SubmitterTask.QueryParam queryParam = submitterTask.clientIdQueryParamBuilder().asQueryParam();

        Map<String, Object> expectedParams = ImmutableMap.<String, Object>builder()
                .putAll(getCommonParams())
                .put("type", SegmentType.uploading.dbName())
                .put("resendSeconds", DEFAULT_RESEND_PERIOD)
                .put("clientIdContentType", SegmentContentType.client_id.name())
                .build();

        String expectedQuery = SELECT_QUERY_COMMON + " AND content_type = :clientIdContentType";

        assertQueryParam(expectedParams, expectedQuery, queryParam);
    }

    @Test
    public void generatesCorrectQueryAndParamsForMetrikaSegmentsFetching() throws Exception {
        SubmitterTask.QueryParam queryParam = submitterTask.queryParamBuilder(SegmentType.metrika).asQueryParam();

        Map<String, Object> expectedParams = ImmutableMap.<String, Object>builder()
                .putAll(getCommonParams())
                .put("type", SegmentType.metrika.dbName())
                .put("resendSeconds", DEFAULT_RESEND_PERIOD)
                .build();

        assertQueryParam(expectedParams, SELECT_QUERY_NONUPLOADING, queryParam);
    }

    @Test
    public void generatesCorrectQueryAndParamsForAppmetricaSegmentsFetching() throws Exception {
        SubmitterTask.QueryParam queryParam = submitterTask.queryParamBuilder(SegmentType.appmetrica).asQueryParam();

        Map<String, Object> expectedParams = ImmutableMap.<String, Object>builder()
                .putAll(getCommonParams())
                .put("type", SegmentType.appmetrica.dbName())
                .put("resendSeconds", DEFAULT_RESEND_PERIOD)
                .build();

        assertQueryParam(expectedParams, SELECT_QUERY_NONUPLOADING, queryParam);
    }

    @Test
    public void generatesCorrectQueryAndParamsForPixelSegmentsFetching() throws Exception {
        SubmitterTask.QueryParam queryParam = submitterTask.queryParamBuilder(SegmentType.pixel).asQueryParam();

        Map<String, Object> expectedParams = ImmutableMap.<String, Object>builder()
                .putAll(getCommonParams())
                .put("type", SegmentType.pixel.dbName())
                .put("resendSeconds", DEFAULT_RESEND_PERIOD)
                .build();

        assertQueryParam(expectedParams, SELECT_QUERY_NONUPLOADING, queryParam);
    }

    @Test
    public void generatesCorrectQueryAndParamsForConditionGeoSegmentsFetching() throws Exception {
        SubmitterTask.QueryParam queryParam = submitterTask.geoQueryParamBuilder(GeoSegmentType.condition,
                DEFAULT_RESEND_PERIOD).asQueryParam();

        Map<String, Object> expectedParams = ImmutableMap.<String, Object>builder()
                .putAll(getCommonParams())
                .put("type", SegmentType.geo.dbName())
                .put("resendSeconds", DEFAULT_RESEND_PERIOD)
                .put("geoType", GeoSegmentType.condition.name())
                .build();

        assertQueryParam(expectedParams, SELECT_QUERY_GEOSEGMENT, queryParam);
    }

    @Test
    public void generatesCorrectQueryAndParamsForLastGeoSegmentsFetching() throws Exception {
        SubmitterTask.QueryParam queryParam = submitterTask.geoQueryParamBuilder(GeoSegmentType.last,
                DEFAULT_RESEND_PERIOD).asQueryParam();

        Map<String, Object> expectedParams = ImmutableMap.<String, Object>builder()
                .putAll(getCommonParams())
                .put("type", SegmentType.geo.dbName())
                .put("resendSeconds", DEFAULT_RESEND_PERIOD)
                .put("geoType", GeoSegmentType.last.name())
                .build();

        assertQueryParam(expectedParams, SELECT_QUERY_GEOSEGMENT, queryParam);
    }

    @Test
    public void generatesCorrectQueryAndParamsForRegularGeoSegmentsFetching() throws Exception {
        resendPeriodSeconds = 30L;
        SubmitterTask.QueryParam queryParam = submitterTask.geoQueryParamBuilder(GeoSegmentType.regular, resendPeriodSeconds).asQueryParam();

        Map<String, Object> expectedParams = ImmutableMap.<String, Object>builder()
                .putAll(getCommonParams())
                .put("type", SegmentType.geo.dbName())
                .put("resendSeconds", resendPeriodSeconds)
                .put("geoType", GeoSegmentType.regular.name())
                .build();

        assertQueryParam(expectedParams, SELECT_QUERY_GEOSEGMENT, queryParam);
    }

    private void assertQueryParam(Map<String, Object> expectedParams, String expectedQuery, SubmitterTask.QueryParam queryParam) {
        SoftAssertions softly = new SoftAssertions();
        softly.assertThat(queryParam.getParams()).isEqualTo(expectedParams);
        softly.assertThat(queryParam.getQuery()).isEqualToIgnoringWhitespace(expectedQuery);
        softly.assertAll();
    }


    private Map<String, Object> getCommonParams() {
        return ImmutableMap.<String, Object>builder()
                .put("submitStatuses", ImmutableList.of(confirmed.name(), updated.name()))
                .put("resendStatuses", ImmutableList.of(processed_fully.name(), processing_failed.name(), few_data.name()))
                .put("autoResendStatuses", ImmutableList.of(processed_fully.name()))
                .build();
    }
}
