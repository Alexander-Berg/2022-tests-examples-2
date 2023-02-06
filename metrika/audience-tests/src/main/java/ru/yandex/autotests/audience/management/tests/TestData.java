package ru.yandex.autotests.audience.management.tests;

import java.io.IOException;
import java.io.InputStream;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.stream.Stream;

import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import org.apache.commons.io.IOUtils;
import org.apache.commons.lang3.StringUtils;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.apache.commons.lang3.tuple.Pair;

import ru.yandex.audience.AppMetricaSegment;
import ru.yandex.audience.AppMetricaSegmentType;
import ru.yandex.audience.BaseSegment;
import ru.yandex.audience.LookalikeSegment;
import ru.yandex.audience.MetrikaSegment;
import ru.yandex.audience.MetrikaSegmentType;
import ru.yandex.audience.SegmentContentType;
import ru.yandex.audience.SegmentType;
import ru.yandex.audience.dmp.DmpSegment;
import ru.yandex.audience.geo.CircleGeoSegment;
import ru.yandex.audience.geo.GeoPoint;
import ru.yandex.audience.geo.GeoPolygon;
import ru.yandex.audience.geo.GeoSegmentType;
import ru.yandex.audience.geo.PolygonGeoSegment;
import ru.yandex.audience.pixel.Pixel;
import ru.yandex.audience.pixel.PixelSegment;
import ru.yandex.audience.pixel.PixelTimesQuantityOperation;
import ru.yandex.audience.segmentab.ExperimentAB;
import ru.yandex.audience.segmentab.SegmentAB;
import ru.yandex.audience.uploading.UploadingSegment;
import ru.yandex.autotests.audience.data.users.User;
import ru.yandex.autotests.audience.data.wrappers.DelegateWrapper;
import ru.yandex.autotests.audience.data.wrappers.SegmentRequestDmpWrapper;
import ru.yandex.autotests.audience.data.wrappers.SegmentRequestUploadingWrapper;
import ru.yandex.autotests.audience.parameters.ModificationType;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.autotests.irt.testutils.RandomUtils;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.metrika.api.management.client.grants.Grant;
import ru.yandex.metrika.audience.pubapi.ClientIdSegmentRequestUploading;
import ru.yandex.metrika.audience.pubapi.Delegate;
import ru.yandex.metrika.audience.pubapi.DelegateType;
import ru.yandex.metrika.audience.pubapi.PixelControllerInnerPixelRequest;
import ru.yandex.metrika.audience.pubapi.SegmentRequestAppMetrika;
import ru.yandex.metrika.audience.pubapi.SegmentRequestDmp;
import ru.yandex.metrika.audience.pubapi.SegmentRequestGeoCircle;
import ru.yandex.metrika.audience.pubapi.SegmentRequestGeoPolygon;
import ru.yandex.metrika.audience.pubapi.SegmentRequestLookalike;
import ru.yandex.metrika.audience.pubapi.SegmentRequestMetrika;
import ru.yandex.metrika.audience.pubapi.SegmentRequestPixel;
import ru.yandex.metrika.audience.pubapi.SegmentRequestUploading;

import static com.google.common.base.Throwables.propagate;
import static java.lang.Boolean.TRUE;
import static java.lang.String.format;
import static java.util.Collections.shuffle;
import static java.util.stream.Collectors.toList;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static org.apache.commons.lang3.RandomUtils.nextDouble;
import static org.apache.commons.lang3.RandomUtils.nextLong;
import static ru.yandex.audience.SegmentContentType.CRYPTA_ID;
import static ru.yandex.audience.SegmentContentType.PUID;
import static ru.yandex.audience.SegmentContentType.YUID;
import static ru.yandex.audience.SegmentType.APPMETRICA;
import static ru.yandex.audience.SegmentType.GEO;
import static ru.yandex.audience.SegmentType.LOOKALIKE;
import static ru.yandex.audience.SegmentType.METRIKA;
import static ru.yandex.audience.SegmentType.PIXEL;
import static ru.yandex.audience.SegmentType.UPLOADING;
import static ru.yandex.autotests.audience.data.users.User.APPMETRICA_APLICATION_ID;
import static ru.yandex.autotests.audience.data.users.User.APPMETRICA_SEGMENT_ID;
import static ru.yandex.autotests.audience.data.users.User.METRIKA_COUNTER_ID;
import static ru.yandex.autotests.audience.data.users.User.METRIKA_GOAL_ID;
import static ru.yandex.autotests.audience.data.users.User.METRIKA_SEGMENT_ID;
import static ru.yandex.autotests.audience.data.users.Users.SUPER_USER;
import static ru.yandex.autotests.audience.data.users.Users.USER_DELEGATOR;
import static ru.yandex.autotests.audience.data.users.Users.USER_GRANTEE;
import static ru.yandex.autotests.audience.data.users.Users.USER_WITH_PERM_EDIT;
import static ru.yandex.autotests.audience.data.wrappers.WrapperBase.wrap;
import static ru.yandex.autotests.audience.errors.ManagementError.INCORRECT_SEGMENT_NAME_LENGTH;
import static ru.yandex.autotests.audience.errors.ManagementError.NOT_NULL;

/**
 * Created by konkov on 28.03.2017.
 */
public final class TestData {
    public static final int NAME_LEN = 6;
    public static final int SEGMENT_NAME_MAX_LENGTH = 250;
    public static final int PIXEL_NAME_LENGTH = 256;

    public static final Long GEO_MIN_RADIUS = 500L;
    public static final Long GEO_MAX_RADIUS = 10000L;
    public static final Long GEO_MAX_PERIOD_LENGTH = 90L;
    public static final int GEO_CONDITION_MAX_POINTS = 100;
    public static final int GEO_OTHER_MAX_POINTS = 1000;
    public static final Double GEO_LATITUDE_LIMIT = 85.05112878D;

    public static final int GEO_MAX_POLYGONS = 10;

    public static final String BOUNDARY_LENGTH_SEGMENT_NAME = RandomUtils.getString(SEGMENT_NAME_MAX_LENGTH);
    public static final String TOO_LONG_SEGMENT_NAME_LENGTH = RandomUtils.getString(SEGMENT_NAME_MAX_LENGTH + 1);

    public static final String PIXEL_TOO_LONG_NAME = RandomUtils.getString(PIXEL_NAME_LENGTH + 1);
    public static final String PIXEL_BOUNDARY_LENGTH_NAME = RandomUtils.getString(PIXEL_NAME_LENGTH);

    public static final String APPMETRICA_SEGMENT_NAME_PREFIX = "сегмент AppMetrica ";
    public static final String METRIKA_SEGMENT_NAME_PREFIX = "сегмент Метрики ";
    public static final String UPLOADING_SEGMENT_NAME_PREFIX = "сегмент из файла ";
    public static final String CLIENTID_UPLOADING_SEGMENT_NAME_PREFIX = "сегмент с ClientId Метрики из файла ";
    public static final String GEO_SEGMENT_NAME_PREFIX = "сегмент «геолокация» ";
    public static final String PIXEL_SEGMENT_NAME_PREFIX = "сегмент «pixel» ";
    public static final String PIXEL_NAME_PREFIX = "пиксель ";
    public static final String LOOKALIKE_SEGMENT_NAME_PREFIX = "сегмент «lookalike» ";
    public static final String DMP_SEGMENT_PREFIX = "сегмент «dmp» ";

    public static final Long SEGMENT_ID_FOR_LOOKALIKE = 839182L;
    public static final Long LOOKALIKE_PRECISION_MIN_VALUE = 1L;
    public static final Long LOOKALIKE_PRECISION_MAX_VALUE = 5L;
    public static final Long LOOKALIKE_GEO_LAST_SEGMENT_ID = 1220430L;
    public static final Long LOOKALIKE_DMP_SEGMENT_ID = 1584240L;
    public static final Long LOOKALIKE_FEW_DATA_SEGMENT_ID = 1220442L;
    public static final Long LOOKALIKE_NO_ACCESS_SEGMENT_ID = 839191L;
    public static final Long LOOKALIKE_INACTIVE_SEGMENT_ID = 1220457L;

    public static final Long YUID_SEGMENT_FOR_LOOKALIKE = 5051032L;
    public static final Long YUID_SEGMENT_BY_UPLOADER_2 = 3235867L;
    public static final Long YUID_SEGMENT_FOR_MODIFY_DATA = 5051044L;
    public static final List<Long> YUID_SEGMENTS_FOR_MODIFICATION = ImmutableList.of(3235852L, 3235858L, 3235861L);

    public static final Long PIXEL_MIN_PERIOD_LENGTH = 1L;
    public static final Long PIXEL_MAX_PERIOD_LENGTH = 90L;
    public static final Long PIXEL_MIN_TIMES_QUANTITY = 1L;
    public static final Long PIXEL_MAX_TIMES_QUANTITY = 1000L;

    public static final Long NOT_ACCESSIBLE_METRIKA_COUNTER = 36940940L;
    public static final List<Long> NOT_ACCESSIBLE_GOAL = ImmutableList.of(31306333L);

    public static final Long DMP_ID = 4L;
    public static final Long DELETED_DMP_SEGMENT_ID = 3085L;
    public static final Long EXISTING_DMP_SEGMENT_ID = 381522L;
    public static final Long NO_ACCESS_DMP_ID = 11L;
    public static final Long NO_ACCESS_DMP_SEGMENT_ID = 23001L;
    public static final Long TOO_SMALL_SIZE_DMP_SEGMENT_ID = 912L;

    public static final Long SEGMENT_WITH_EXTENDED_STAT = 839185L;

    public static final Long SEGMENT_FOR_REPROCESS = 1571184L;
    public static final Long SEGMENT_FOR_REPROCESS_QUOTA = 1571181L;

    public static final Long UPLOADING_SEGMENT_DELETED = 19645725L;

    public static final String EXPERIMENT_NAME_PREFIX = "эксперимент ";
    public static final String SEGMENT_NAME_PREFIX = "сегмент ";
    public static final int EXPERIMENT_NAME_LENGTH = 64;
    public static final String EXPERIMENT_TOO_LONG_NAME = RandomUtils.getString(EXPERIMENT_NAME_LENGTH + 1);
    public static final int SEGMENT_NAME_LENGTH = 128;
    public static final String SEGMENT_TOO_LONG_NAME = RandomUtils.getString(SEGMENT_NAME_LENGTH + 1);

    private static final Map<Pair<SegmentContentType, Boolean>, String> UPLOADING_CONTENT =
            ImmutableMap.<Pair<SegmentContentType, Boolean>, String>builder()
                    .put(ImmutablePair.of(SegmentContentType.EMAIL, false), "data/plain/email")
                    .put(ImmutablePair.of(SegmentContentType.IDFA_GAID, false), "data/plain/idfa_gaid")
                    .put(ImmutablePair.of(SegmentContentType.PHONE, false), "data/plain/phone")
                    .put(ImmutablePair.of(SegmentContentType.YUID, false), "data/plain/yuid")
                    .put(ImmutablePair.of(SegmentContentType.MAC, false), "data/plain/mac")
                    .put(ImmutablePair.of(SegmentContentType.CLIENT_ID, false), "data/plain/clientid")
                    .put(ImmutablePair.of(SegmentContentType.CRM, false), "data/plain/crm")
                    .put(ImmutablePair.of(CRYPTA_ID, false), "data/plain/crypta_id")
                    .put(ImmutablePair.of(PUID, false), "data/plain/puid")

                    .put(ImmutablePair.of(SegmentContentType.EMAIL, true), "data/hashed/email")
                    .put(ImmutablePair.of(SegmentContentType.IDFA_GAID, true), "data/hashed/idfa_gaid")
                    .put(ImmutablePair.of(SegmentContentType.PHONE, true), "data/hashed/phone")
                    .put(ImmutablePair.of(SegmentContentType.MAC, true), "data/hashed/mac")
                    .put(ImmutablePair.of(SegmentContentType.CRM, true), "data/hashed/crm")
                    .build();

    private static final Map<Pair<SegmentContentType, Boolean>, String> UPLOADING_CONTENT_CRYPTA_SENDER =
            ImmutableMap.<Pair<SegmentContentType, Boolean>, String>builder()
                    .put(ImmutablePair.of(SegmentContentType.EMAIL, false), "data/plain/email")
                    .put(ImmutablePair.of(SegmentContentType.IDFA_GAID, false), "data/plain/idfa_gaid_long")
                    .put(ImmutablePair.of(SegmentContentType.PHONE, false), "data/plain/phone")
                    .put(ImmutablePair.of(SegmentContentType.YUID, false), "data/plain/yuid")
                    .put(ImmutablePair.of(SegmentContentType.MAC, false), "data/plain/mac_long")
                    .put(ImmutablePair.of(SegmentContentType.CLIENT_ID, false), "data/plain/clientid_long")
                    .put(ImmutablePair.of(SegmentContentType.CRM, false), "data/plain/crm")
                    .put(ImmutablePair.of(CRYPTA_ID, false), "data/plain/crypta_id")
                    .put(ImmutablePair.of(PUID, false), "data/plain/puid")

                    .put(ImmutablePair.of(SegmentContentType.EMAIL, true), "data/hashed/email")
                    .put(ImmutablePair.of(SegmentContentType.IDFA_GAID, true), "data/hashed/idfa_gaid")
                    .put(ImmutablePair.of(SegmentContentType.PHONE, true), "data/hashed/phone")
                    .put(ImmutablePair.of(SegmentContentType.MAC, true), "data/hashed/mac_long")
                    .put(ImmutablePair.of(SegmentContentType.CRM, true), "data/hashed/crm")
                    .build();

    public static final Map<SegmentType, Long> SEGMENTS = ImmutableMap.<SegmentType, Long>builder()
            .put(UPLOADING, 839182L)
            .put(METRIKA, 839185L)
            .put(APPMETRICA, 839188L)
            .put(GEO, 839191L)
            .put(PIXEL, 850588L)
            .put(LOOKALIKE, 874228L)
            .build();

    public static final Map<SegmentType, Long> SEGMENTS_CRYPTA_SENDER = ImmutableMap.<SegmentType, Long>builder()
            .put(UPLOADING, 2371193L)
            .put(METRIKA, 2371198L)
            .put(APPMETRICA, 2371200L)
            .put(LOOKALIKE, 2371283L)
            .build();


    public static final String PIXEL_SEGMENT_OWNER = "etagi72";
    public static final String DEFAULT_DELIMITER = "\n";

    public static Long PIXEL_ID = 31377L;
    public static Long PIXEL_ID_CRYPTA_SENDER = 2555L;

    public static final Map<String, Long> DMP_SEGMENTS_IDS = ImmutableMap.<String, Long>builder()
            .put("CreateDmpSegmentsTest_1", 381144L)
            .put("CreateDmpSegmentsTest_2", 377250L)
            .put("CreateOneDmpSegmentNegativeTest", 381149L)
            .put("CreateOneDmpSegmentTest", 377255L)
            .put("DeleteDmpSegmentTest", 377247L)
            .put("EditDmpSegmentNegativeTest", 377246L)
            .put("EditDmpSegmentTest", 381153L)
            .put("RestoreDmpSegmentTest", 381152L)
            .build();

    public static String getName(String prefix) {
        return prefix + RandomUtils.getString(NAME_LEN);
    }

    public static SegmentRequestAppMetrika getAppMetricaSegment(AppMetricaSegmentType type, User user) {
        SegmentRequestAppMetrika segment = new SegmentRequestAppMetrika()
                .withAppMetricaSegmentType(type);

        switch (type) {
            case API_KEY:
                segment.setAppMetricaSegmentId(user.get(APPMETRICA_APLICATION_ID));
                break;
            case SEGMENT_ID:
                segment.setAppMetricaSegmentId(user.get(APPMETRICA_SEGMENT_ID));
                break;
        }

        segment.setName(getName(APPMETRICA_SEGMENT_NAME_PREFIX +
                format("%s: %s ", segment.getAppMetricaSegmentType(), segment.getAppMetricaSegmentId())));

        return segment;
    }

    public static SegmentRequestMetrika getMetrikaSegment(MetrikaSegmentType type, User user) {
        SegmentRequestMetrika segment = new SegmentRequestMetrika()
                .withMetrikaSegmentType(type);

        switch (type) {
            case COUNTER_ID:
                segment.setMetrikaSegmentId(user.get(METRIKA_COUNTER_ID));
                break;
            case GOAL_ID:
                segment.setMetrikaSegmentId(user.get(METRIKA_GOAL_ID));
                break;
            case SEGMENT_ID:
                segment.setMetrikaSegmentId(user.get(METRIKA_SEGMENT_ID));
                break;
        }

        segment.setName(getName(METRIKA_SEGMENT_NAME_PREFIX +
                format("%s: %s ", segment.getMetrikaSegmentType(), segment.getMetrikaSegmentId())));

        return segment;
    }

    public static SegmentRequestUploading getUploadingSegment(SegmentContentType type, boolean isHashed) {
        return new SegmentRequestUploading()
                .withContentType(type)
                .withHashed(isHashed)
                .withName(getName(UPLOADING_SEGMENT_NAME_PREFIX +
                        format("%s%s ", isHashed ? "хэшированный " : StringUtils.EMPTY, type)));
    }

    public static ClientIdSegmentRequestUploading getClientIdSegmentRequestUploading() {
        return new ClientIdSegmentRequestUploading()
                .withCounterId(51258889L)
                .withName(getName(CLIENTID_UPLOADING_SEGMENT_NAME_PREFIX));
    }

    public static ClientIdSegmentRequestUploading getClientIdSegmentRequestUploadingCryptaSender() {
        return new ClientIdSegmentRequestUploading()
                .withCounterId(24226447L)
                .withName(getName(CLIENTID_UPLOADING_SEGMENT_NAME_PREFIX));
    }

    public static InputStream getContent(SegmentRequestUploadingWrapper request) {
        return getContent(request.get().getContentType(), request.get().getHashed(), DEFAULT_DELIMITER);
    }

    public static SegmentRequestUploading getYuidUploadingSegment() {
        return getUploadingSegment(YUID, false);
    }

    public static SegmentRequestUploading getCryptaIdUploadingSegment() {
        return getUploadingSegment(CRYPTA_ID, false);
    }

    public static SegmentRequestUploading getPuidUploadingSegment() {
        return getUploadingSegment(PUID, false);
    }

    public static InputStream getClientIdContent() {
        return getClientIdContent(DEFAULT_DELIMITER);
    }

    public static InputStream getClientIdContent(String delimiter) {
        return getContent(SegmentContentType.CLIENT_ID, false, delimiter);
    }

    public static InputStream getClientIdContentCryptaSender(String delimiter) {
        return getContentCryptaSender(SegmentContentType.CLIENT_ID, false, delimiter);
    }

    public static InputStream getClientIdContentForAddition() {
        return getContent(getFakeClientIds(2L));
    }

    public static InputStream getContent(SegmentContentType type, boolean isHashed) {
        return getContent(type, isHashed, DEFAULT_DELIMITER);
    }

    public static InputStream getContent(SegmentContentType type, boolean isHashed, String delimiter) {
        return getContent(UPLOADING_CONTENT.get(ImmutablePair.of(type, isHashed)), delimiter);
    }

    public static InputStream getContentCryptaSender(SegmentContentType type, boolean isHashed, String delimiter) {
        return getContent(UPLOADING_CONTENT_CRYPTA_SENDER.get(ImmutablePair.of(type, isHashed)), delimiter);
    }

    public static InputStream getEmptyContent() {
        return getContent("data/plain/empty_file", DEFAULT_DELIMITER);
    }

    public static InputStream getCrmContentWithoutEmail() {
        return getContent("data/plain/crm_wo_email", DEFAULT_DELIMITER);
    }

    public static InputStream getCrmContentWithoutPhone() {
        return getContent("data/plain/crm_wo_phone", DEFAULT_DELIMITER);
    }

    public static InputStream getCrmContentNoParse() {
        return getContent("data/plain/crm_no_parse", DEFAULT_DELIMITER);
    }

    public static InputStream getContent(String resourceName, String delimiter) {
        try {
            return IOUtils.toInputStream(String.join(delimiter,
                    IOUtils.readLines(TestData.class.getClassLoader().getResourceAsStream(resourceName))));

        } catch (IOException e) {
            throw propagate(e);
        }
    }

    public static InputStream getContent(List<String> yuids) {
        return IOUtils.toInputStream(String.join(DEFAULT_DELIMITER, yuids));
    }

    public static InputStream getYuidContent() {
        return getContent(YUID, false, DEFAULT_DELIMITER);
    }

    public static InputStream getPuidContent() {
        return getContent(PUID, false, DEFAULT_DELIMITER);
    }

    public static InputStream getCryptaIdContent() {
        return getContent(CRYPTA_ID, false, DEFAULT_DELIMITER);
    }

    public static SegmentRequestGeoCircle getGeoCircleSegment(GeoSegmentType type) {
        return new SegmentRequestGeoCircle()
                .withGeoSegmentType(type)
                .withRadius(500L)
                .withPeriodLength(GeoSegmentType.CONDITION == type ? 1L : null)
                .withTimesQuantity(GeoSegmentType.CONDITION == type ? 1L : null)
                .withPoints(ImmutableList.of(
                        new GeoPoint()
                                .withDescription("Фиджи")
                                .withLatitude(-17.8375)
                                .withLongitude(179.4397)))
                .withName(getName(GEO_SEGMENT_NAME_PREFIX +
                        format("%s ", type)));
    }

    public static SegmentRequestGeoCircle getGeoCircleSegmentCryptaSender(GeoSegmentType type) {
        return new SegmentRequestGeoCircle()
                .withGeoSegmentType(type)
                .withRadius(1000L)
                .withPeriodLength(GeoSegmentType.CONDITION == type ? 1L : null)
                .withTimesQuantity(GeoSegmentType.CONDITION == type ? 1L : null)
                .withPoints(ImmutableList.of(
                        new GeoPoint()
                                .withDescription("Москва")
                                .withLatitude(55.755869)
                                .withLongitude(37.620828)))
                .withName(getName(GEO_SEGMENT_NAME_PREFIX + format("%s ", type)));
    }

    public static SegmentRequestGeoPolygon getGeoPolygonSegment(GeoSegmentType type) {
        return new SegmentRequestGeoPolygon()
                .withGeoSegmentType(type)
                .withPeriodLength(GeoSegmentType.CONDITION == type ? 1L : null)
                .withTimesQuantity(GeoSegmentType.CONDITION == type ? 1L : null)
                .withPolygons(ImmutableList.of(getGeoPolygon()))
                .withName(getName(GEO_SEGMENT_NAME_PREFIX + format("%s ", type)));
    }

    public static SegmentRequestGeoPolygon getGeoPolygonSegmentCryptaSender(GeoSegmentType type) {
        return new SegmentRequestGeoPolygon()
                .withGeoSegmentType(type)
                .withPeriodLength(GeoSegmentType.CONDITION == type ? 1L : null)
                .withTimesQuantity(GeoSegmentType.CONDITION == type ? 1L : null)
                .withPolygons(ImmutableList.of(getGeoPolygonCryptaSender()))
                .withName(getName(GEO_SEGMENT_NAME_PREFIX + format("%s ", type)));
    }

    public static SegmentRequestPixel getPixelSegment() {
        return getPixelSegment(PIXEL_ID);
    }

    public static SegmentRequestPixel getPixelSegment(Long pixelId) {
        return new SegmentRequestPixel()
                .withPixelId(pixelId)
                .withPeriodLength(10L)
                .withTimesQuantity(5L)
                .withTimesQuantityOperation(PixelTimesQuantityOperation.GT)
                .withUtmCampaign(RandomUtils.getString(NAME_LEN))
                .withUtmContent(RandomUtils.getString(NAME_LEN))
                .withUtmMedium(RandomUtils.getString(NAME_LEN))
                .withUtmSource(RandomUtils.getString(NAME_LEN))
                .withUtmTerm(RandomUtils.getString(NAME_LEN))
                .withName(getName(PIXEL_SEGMENT_NAME_PREFIX));
    }

    public static SegmentRequestPixel getPixelSegmentCryptaSender(Long pixelId) {
        return new SegmentRequestPixel()
                .withPixelId(pixelId)
                .withPeriodLength(90L)
                .withTimesQuantity(1L)
                .withTimesQuantityOperation(PixelTimesQuantityOperation.GT)
                .withName(getName(PIXEL_SEGMENT_NAME_PREFIX));
    }

    public static SegmentRequestLookalike getLookalikeSegment() {
        return getLookalikeSegment(SEGMENT_ID_FOR_LOOKALIKE);
    }

    public static SegmentRequestLookalike getLookalikeSegment(String name) {
        return getLookalikeSegment().withName(name);
    }

    public static SegmentRequestLookalike getLookalikeSegment(Long lookalikeLink) {
        return getLookalikeSegment(lookalikeLink, getPrecisionValue());
    }

    public static SegmentRequestLookalike getLookalikeSegment(Long lookalikeLink, Long lookalikeValue) {
        return getLookalikeSegment(lookalikeLink, lookalikeValue, TRUE, TRUE);
    }

    public static SegmentRequestLookalike getLookalikeSegment(Boolean geoDistribution, Boolean deviceDistribution) {
        return getLookalikeSegment()
                .withMaintainGeoDistribution(geoDistribution)
                .withMaintainDeviceDistribution(deviceDistribution);
    }

    public static SegmentRequestLookalike getLookalikeSegment(Long lookalikeLink, Long lookalikeValue,
                                                              Boolean geoDistribution, Boolean deviceDistribution) {
        return new SegmentRequestLookalike()
                .withLookalikeLink(lookalikeLink)
                .withLookalikeValue(lookalikeValue)
                .withMaintainGeoDistribution(geoDistribution)
                .withMaintainDeviceDistribution(deviceDistribution)
                .withName(getName(LOOKALIKE_SEGMENT_NAME_PREFIX + format("от %s ", lookalikeLink)));
    }

    public static SegmentRequestDmp getDmpSegment(Long dmpSegmentId) {
        return getDmpSegment(DMP_ID, dmpSegmentId);
    }

    public static SegmentRequestDmp getDmpSegment() {
        return getDmpSegment(DMP_SEGMENTS_IDS.get("CreateOneDmpSegmentTest"));
    }

    public static List<SegmentRequestDmp> getDmpSegments(List<Long> dmpSegmentIds) {
        return dmpSegmentIds.stream().map(TestData::getDmpSegment).collect(toList());
    }

    public static SegmentRequestDmp getDmpSegment(Long dmpId, Long dmpSegmentId) {
        return new SegmentRequestDmp()
                .withDmpId(dmpId)
                .withDmpSegmentId(dmpSegmentId);
    }

    public static MetrikaSegment getExpectedSegment(SegmentRequestMetrika original) {
        return new MetrikaSegment()
                .withName(original.getName())
                .withMetrikaSegmentType(original.getMetrikaSegmentType())
                .withMetrikaSegmentId(original.getMetrikaSegmentId());
    }

    public static AppMetricaSegment getExpectedSegment(SegmentRequestAppMetrika original) {
        return new AppMetricaSegment()
                .withName(original.getName())
                .withAppMetricaSegmentType(original.getAppMetricaSegmentType())
                .withAppMetricaSegmentId(original.getAppMetricaSegmentId());
    }

    public static UploadingSegment getExpectedSegment(SegmentRequestUploading original) {
        return new UploadingSegment()
                .withId(original.getId())
                .withName(original.getName())
                .withContentType(original.getContentType())
                .withHashed(original.getHashed());
    }

    public static UploadingSegment getExpectedSegment(ClientIdSegmentRequestUploading original) {
        return new UploadingSegment()
                .withName(original.getName())
                .withCounterId(original.getCounterId());
    }

    public static CircleGeoSegment getExpectedSegment(SegmentRequestGeoCircle original) {
        return new CircleGeoSegment()
                .withName(original.getName())
                .withGeoSegmentType(original.getGeoSegmentType())
                .withPoints(original.getPoints())
                .withPeriodLength(original.getPeriodLength())
                .withRadius(original.getRadius())
                .withTimesQuantity(original.getTimesQuantity());
    }

    public static PolygonGeoSegment getExpectedSegment(SegmentRequestGeoPolygon original) {
        return new PolygonGeoSegment()
                .withName(original.getName())
                .withGeoSegmentType(original.getGeoSegmentType())
                .withPolygons(original.getPolygons())
                .withPeriodLength(original.getPeriodLength())
                .withTimesQuantity(original.getTimesQuantity());
    }

    public static PixelSegment getExpectedSegment(SegmentRequestPixel original) {
        return new PixelSegment()
                .withName(original.getName())
                .withPixelId(original.getPixelId())
                .withPeriodLength(original.getPeriodLength())
                .withTimesQuantity(original.getTimesQuantity())
                .withTimesQuantityOperation(original.getTimesQuantityOperation())
                .withUtmCampaign(original.getUtmCampaign())
                .withUtmContent(original.getUtmContent())
                .withUtmMedium(original.getUtmMedium())
                .withUtmSource(original.getUtmSource())
                .withUtmTerm(original.getUtmTerm());
    }

    public static LookalikeSegment getExpectedSegment(SegmentRequestLookalike original) {
        return new LookalikeSegment()
                .withName(original.getName())
                .withLookalikeLink(original.getLookalikeLink())
                .withLookalikeValue(original.getLookalikeValue())
                .withMaintainGeoDistribution(
                        original.getMaintainGeoDistribution() == null ? TRUE : original.getMaintainGeoDistribution())
                .withMaintainDeviceDistribution(
                        original.getMaintainDeviceDistribution() == null ? TRUE :
                                original.getMaintainDeviceDistribution());
    }

    public static DmpSegment getExpectedSegment(SegmentRequestDmp original) {
        return new DmpSegment()
                .withDmpId(original.getDmpId())
                .withDmpSegmentId(original.getDmpSegmentId());
    }

    public static List<DmpSegment> getExpectedSegments(List<SegmentRequestDmp> original) {
        return original.stream().map(TestData::getExpectedSegment).collect(toList());
    }

    public static AppMetricaSegment getSegmentToChange(AppMetricaSegment createdSegment,
                                                       String newName,
                                                       AppMetricaSegmentType newType,
                                                       Long newSegmentId) {
        return new AppMetricaSegment()
                .withName(newName)
                .withAppMetricaSegmentType(newType)
                .withAppMetricaSegmentId(newSegmentId);
    }

    public static MetrikaSegment getSegmentToChange(MetrikaSegment createdSegment,
                                                    String newName,
                                                    MetrikaSegmentType newType,
                                                    Long newSegmentId) {
        return wrap(createdSegment).getClone()
                .withName(newName)
                .withMetrikaSegmentType(newType)
                .withMetrikaSegmentId(newSegmentId);
    }

    public static UploadingSegment getSegmentToChange(UploadingSegment createdSegment,
                                                      String newName,
                                                      SegmentContentType newType,
                                                      boolean newHashed) {
        return wrap(createdSegment).getClone()
                .withName(newName)
                .withContentType(newType)
                .withHashed(newHashed);
    }

    public static CircleGeoSegment getSegmentToChange(CircleGeoSegment createdSegment,
                                                      String newName,
                                                      GeoSegmentType newType,
                                                      Long newRadius,
                                                      Long newPeriodLength,
                                                      Long newTimesQuantity) {
        return wrap(createdSegment).getClone()
                .withName(newName)
                .withGeoSegmentType(newType)
                .withRadius(newRadius)
                .withPeriodLength(newPeriodLength)
                .withTimesQuantity(newTimesQuantity);
    }

    public static PixelSegment getSegmentToChange(PixelSegment createdSegment,
                                                  String newName,
                                                  Long newPixelId) {
        return wrap(createdSegment).getClone()
                .withName(newName)
                .withPixelId(newPixelId)
                .withPeriodLength(11L)
                .withTimesQuantity(6L)
                .withTimesQuantityOperation(PixelTimesQuantityOperation.LT)
                .withUtmCampaign(RandomUtils.getString(NAME_LEN))
                .withUtmContent(RandomUtils.getString(NAME_LEN))
                .withUtmMedium(RandomUtils.getString(NAME_LEN))
                .withUtmSource(RandomUtils.getString(NAME_LEN))
                .withUtmTerm(RandomUtils.getString(NAME_LEN));

    }

    public static <T extends BaseSegment> T getSegmentToChange(T createdSegment, String newName) {
        return (T) wrap(createdSegment).getClone().withName(newName);
    }

    public static String getPixelName() {
        return getName(PIXEL_NAME_PREFIX);
    }

    public static String getExperimentName() {
        return getName(EXPERIMENT_NAME_PREFIX);
    }

    public static String getSegmentName() {
        return getName(SEGMENT_NAME_PREFIX);
    }

    public static Long getPrecisionValue() {
        return nextLong(LOOKALIKE_PRECISION_MIN_VALUE, LOOKALIKE_PRECISION_MAX_VALUE + 1);
    }

    public static Object[] getEmptySegmentNameParams() {
        return toArray(
                "пустой name",
                StringUtils.EMPTY,
                INCORRECT_SEGMENT_NAME_LENGTH
        );
    }

    public static Object[] getTooLongSegmentNameParams() {
        return toArray(
                "слишком длинный name",
                TOO_LONG_SEGMENT_NAME_LENGTH,
                INCORRECT_SEGMENT_NAME_LENGTH
        );
    }

    public static Object[] getNullSegmentNameParams() {
        return toArray(
                "отсутствует поле name",
                null,
                NOT_NULL
        );
    }

    public static Object[] createLookalikeParam(SegmentType type, SegmentRequestLookalike segmentRequest,
                                                UserSteps user,
                                                String uLogin) {
        return createLookalikeParam(type, segmentRequest, user, uLogin, "");
    }

    public static Object[] createLookalikeParam(SegmentType type, SegmentRequestLookalike segmentRequest,
                                                UserSteps user,
                                                String uLogin, String notes) {
        return toArray(
                type,
                segmentRequest,
                user,
                uLogin,
                notes);
    }

    public static Object[] createLookalikeNegativeParam(String description, SegmentRequestLookalike request,
                                                        IExpectedError error) {
        return toArray(
                request,
                error,
                description
        );
    }

    public static SegmentRequestLookalike createLookalikeForGeoLast() {
        return getLookalikeSegment(LOOKALIKE_GEO_LAST_SEGMENT_ID);
    }

    public static SegmentRequestLookalike createLookalikeForDmp() {
        return getLookalikeSegment(LOOKALIKE_DMP_SEGMENT_ID);
    }

    public static SegmentRequestLookalike createLookalikeForFewData() {
        return getLookalikeSegment(LOOKALIKE_FEW_DATA_SEGMENT_ID);
    }

    public static SegmentRequestLookalike createLookalikeForNoAccess() {
        return getLookalikeSegment(LOOKALIKE_NO_ACCESS_SEGMENT_ID);
    }

    public static SegmentRequestLookalike createLookalikeForInactive() {
        return getLookalikeSegment(LOOKALIKE_INACTIVE_SEGMENT_ID);
    }

    public static Object[] createGeoNegativeParam(String description, SegmentRequestGeoCircle segmentRequestGeo,
                                                  IExpectedError error) {
        return toArray(
                description,
                segmentRequestGeo,
                error
        );
    }

    public static Object[] createGeoNegativeParam(String description, SegmentRequestGeoPolygon segmentRequestGeo,
                                                  IExpectedError error) {
        return toArray(
                description,
                segmentRequestGeo,
                error
        );
    }

    private static GeoPoint getGeoPoint() {
        return new GeoPoint().withLatitude(GEO_LATITUDE_LIMIT - nextDouble(0d, GEO_LATITUDE_LIMIT * 2))
                .withLongitude(180d - nextDouble(0d, 360d));
    }

    public static GeoPoint getGeoPointLat(Double latitude) {
        return getGeoPoint().withLatitude(latitude);
    }

    public static GeoPoint getGeoPointLon(Double longitude) {
        return getGeoPoint().withLongitude(longitude);
    }

    public static List<GeoPoint> getGeoPointsLat(Double latitude) {
        return ImmutableList.of(getGeoPointLat(latitude));
    }

    public static List<GeoPoint> getGeoPointsLon(Double longitude) {
        return ImmutableList.of(getGeoPointLon(longitude));
    }

    public static List<GeoPoint> getGeoPoints(int count) {
        return Stream.generate(TestData::getGeoPoint).limit(count).collect(toList());
    }

    public static List<GeoPolygon> getGeoPolygons(int count) {
        return Stream.generate(TestData::getGeoPolygon).limit(count).collect(toList());
    }

    private static GeoPolygon getGeoPolygon() {
        return new GeoPolygon()
//                .withDescription("Баклажан-убийца")
                .withPoints(ImmutableList.of(
                        new GeoPoint()
                                .withLatitude(-17.8375)
                                .withLongitude(179.4397),
                        new GeoPoint()
                                .withLatitude(-17.8385)
                                .withLongitude(179.4397),
                        new GeoPoint()
                                .withLatitude(-17.8385)
                                .withLongitude(179.4387),
                        new GeoPoint()
                                .withLatitude(-17.8375)
                                .withLongitude(179.4397)
                ));
    }

    private static GeoPolygon getGeoPolygonCryptaSender() {
        return new GeoPolygon()
                .withPoints(ImmutableList.of(
                        new GeoPoint()
                                .withLatitude(59.92078110547634)
                                .withLongitude(30.354316518890307),
                        new GeoPoint()
                                .withLatitude(59.92117969393408)
                                .withLongitude(30.354574010955755),
                        new GeoPoint()
                                .withLatitude(59.920910377934916)
                                .withLongitude(30.35616187869256),
                        new GeoPoint()
                                .withLatitude(59.92039328506893)
                                .withLongitude(30.355947301971376),
                        new GeoPoint()
                                .withLatitude(59.92078110547634)
                                .withLongitude(30.354316518890307)
                ));
    }

    public static GeoPolygon getInvalidGeoPolygon() {
        return new GeoPolygon()
//                .withDescription("Кабачок-убийца")
                .withPoints(ImmutableList.of(
                        new GeoPoint()
                                .withLatitude(-17.8375)
                                .withLongitude(179.4397),
                        new GeoPoint()
                                .withLatitude(-17.8385)
                                .withLongitude(179.4397),
                        new GeoPoint()
                                .withLatitude(-17.8375)
                                .withLongitude(179.4387),
                        new GeoPoint()
                                .withLatitude(-17.8385)
                                .withLongitude(179.4387),
                        new GeoPoint()
                                .withLatitude(-17.8375)
                                .withLongitude(179.4397)
                ));
    }

    public static Object[] createDmpNegativeParam(String description, SegmentRequestDmp segment, IExpectedError error) {
        return toArray(
                description,
                SegmentRequestDmpWrapper.wrap(segment),
                error
        );
    }

    public static SegmentRequestDmp createDeletedDmpSegment() {
        return getDmpSegment(DMP_ID, DELETED_DMP_SEGMENT_ID);
    }

    public static SegmentRequestDmp createNoAccessDmpSegment() {
        return getDmpSegment(NO_ACCESS_DMP_ID, NO_ACCESS_DMP_SEGMENT_ID);
    }

    public static SegmentRequestDmp createTooSmallSizeDmpSegment() {
        return getDmpSegment(DMP_ID, TOO_SMALL_SIZE_DMP_SEGMENT_ID);
    }

    public static SegmentRequestDmp createExistingDmpSegment() {
        return getDmpSegment(DMP_ID, EXISTING_DMP_SEGMENT_ID);
    }

    public static Object[] createPixelNegativeParam(String description, String name, IExpectedError error) {
        return toArray(
                description,
                name,
                error
        );
    }

    public static PixelControllerInnerPixelRequest getPixel() {
        return getPixel(getPixelName());
    }

    public static PixelControllerInnerPixelRequest getPixel(String name) {
        return new PixelControllerInnerPixelRequest().withName(name);
    }

    public static Pixel getExpectedPixel(PixelControllerInnerPixelRequest request) {
        return new Pixel().withName(request.getName());
    }

    public static Object[] createPixelSegmentNegativeParam(String description, SegmentRequestPixel segmentRequest,
                                                           IExpectedError error) {
        return toArray(
                description,
                segmentRequest,
                error
        );
    }

    public static Object[] createStatNegativeParams(String description, Long counterId, List<Long> goalIds,
                                                    IExpectedError error) {
        return toArray(
                description,
                counterId,
                goalIds,
                error
        );
    }

    public static Object[] editClientNegativeParams(String description, Long segmentId, UploadingSegment segment,
                                                    IExpectedError error) {
        return toArray(
                description,
                segmentId,
                segment,
                error
        );
    }

    public static Object[] confirmClientSegmentNegativeParams(String description, Long segmentId,
                                                              SegmentRequestUploading segmentRequest,
                                                              User userParam, IExpectedError error) {
        return toArray(
                description,
                segmentId,
                segmentRequest,
                UserSteps.withUser(userParam),
                error
        );
    }

    public static Object[] modifyDataInYuidSegmentParams(String description, Long segmentId,
                                                         InputStream content, ModificationType modificationType,
                                                         User userParam, IExpectedError error) {
        return toArray(
                description,
                segmentId,
                content,
                modificationType,
                UserSteps.withUser(userParam),
                error
        );
    }

    public static InputStream getContentForAddition() {
        return getContent(getFakeYuids(2L));
    }

    public static InputStream getContentForSubtraction() {
        return getContent(getYuidsFromFile(3L));
    }

    public static InputStream getContentForReplace() {
        return getContent(getYuidsFromFile(11L));
    }

    private static Long getFakeYuid() {
        return nextLong(10000000000000000L, 999999999999999999L);
    }

    private static List<String> getFakeYuids(long limit) {
        return Stream.generate(TestData::getFakeYuid).map(Object::toString).limit(limit).collect(toList());
    }

    private static List<String> getFakeClientIds(long limit) {
        return Stream.generate(TestData::getFakeYuid).map(Object::toString).limit(limit).collect(toList());
    }

    private static List<String> getYuidsFromFile(Long limit) {
        try {
            List<String> allLines = IOUtils.readLines(TestData.class.getClassLoader()
                    .getResourceAsStream("data/plain/yuid2"));
            shuffle(allLines);
            return allLines.stream().limit(limit).collect(toList());
        } catch (IOException e) {
            throw propagate(e);
        }
    }

    public static Grant getGrant() {
        return getGrant(USER_GRANTEE);
    }

    public static Grant getGrant(User user) {
        return getGrant(user.toString());
    }

    public static Grant getGrant(String userLogin) {
        return new Grant()
                .withUserLogin(userLogin)
                .withComment(RandomUtils.getString(10));
    }

    public static Object[] createGrantNegativeParam(String description, String userLogin, Long segmentId,
                                                    IExpectedError error) {
        return toArray(
                description,
                getGrant(userLogin),
                segmentId,
                error
        );
    }

    public static Delegate getDelegate(String userLogin, DelegateType perm) {
        return new Delegate()
                .withUserLogin(userLogin)
                .withPerm(perm)
                .withComment(RandomUtils.getString(10));
    }

    public static Delegate getDelegate(User user, DelegateType perm) {
        return getDelegate(user.toString(), perm);
    }

    public static Object[] createDelegateNegativeParam(String description, String userLogin, DelegateType perm,
                                                       IExpectedError error) {
        return toArray(
                description,
                DelegateWrapper.wrap(getDelegate(userLogin, perm)),
                error
        );
    }

    public static ExperimentAB getSimpleExperiment(User user) {
        return new ExperimentAB()
                .withName(getExperimentName())
                .withCounterIds(Arrays.asList(user.get(METRIKA_COUNTER_ID)))
                .withSegments(Arrays.asList(getSegmentAB("0", "50"), getSegmentAB("50", "100")));
    }

    public static ExperimentAB getBkExperiment(User user) {
        return new ExperimentAB()
                .withName(getExperimentName())
                .withCounterIds(Arrays.asList(user.get(METRIKA_COUNTER_ID)))
                .withSegments(Arrays.asList(getSegmentAB("0", "50"), getSegmentAB("50", "100")))
                .withBkSettings("{\"answer\":42}");
    }

    public static SegmentAB getSegmentAB(String start, String end) {
        return new SegmentAB()
                .withName(getSegmentName())
                .withStart(start)
                .withEnd(end);
    }


    public static List getSuperUser() {
        return ImmutableList.of(SUPER_USER, "с ролью суперпользователь");
    }

    public static List getUserWithPermEdit() {
        return ImmutableList.of(USER_WITH_PERM_EDIT, "с правом на редактирование");
    }

    public static List getOwner() {
        return ImmutableList.of(USER_DELEGATOR, "владелец");
    }
}
