package ru.yandex.autotests.audience.core;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import ru.yandex.audience.*;
import ru.yandex.audience.dmp.DmpSegment;
import ru.yandex.audience.geo.CircleGeoSegment;
import ru.yandex.audience.geo.GeoSegmentForm;
import ru.yandex.audience.geo.PolygonGeoSegment;
import ru.yandex.audience.pixel.PixelSegment;
import ru.yandex.audience.uploading.UploadingSegment;
import ru.yandex.autotests.metrika.commons.clients.http.LowercaseEnumTypeAdapterFactory;
import ru.yandex.autotests.metrika.commons.clients.http.jackson.Jackson2FieldNamingStrategy;
import ru.yandex.autotests.metrika.commons.clients.http.jackson.Jackson2JsonIgnoreStrategy;

public class AudienceJson {

    private static final String JSON_DATE_FORMAT = "yyyy-MM-dd'T'HH:mm:ssX";

    public static final Gson GSON_RESPONSE = new GsonBuilder()
            .registerTypeAdapter(BaseSegment.class, new SegmentDeserializer()
                    .registerSegmentType(AppMetricaSegment.class, SegmentType.APPMETRICA)
                    .registerSegmentType(CompositeSegment.class, SegmentType.COMPOSITION)
                    .registerSegmentType(DmpSegment.class, SegmentType.DMP)
                    .registerSegmentType(CircleGeoSegment.class, SegmentType.GEO, GeoSegmentForm.CIRCLE)
                    .registerSegmentType(PolygonGeoSegment.class, SegmentType.GEO, GeoSegmentForm.POLYGON)
                    .registerSegmentType(LookalikeSegment.class, SegmentType.LOOKALIKE)
                    .registerSegmentType(MetrikaSegment.class, SegmentType.METRIKA)
                    .registerSegmentType(PixelSegment.class, SegmentType.PIXEL)
                    .registerSegmentType(UploadingSegment.class, SegmentType.UPLOADING))
            .setExclusionStrategies(new Jackson2JsonIgnoreStrategy())
            .enableComplexMapKeySerialization()
            .setDateFormat(JSON_DATE_FORMAT)
            .setFieldNamingStrategy(Jackson2FieldNamingStrategy.STRATEGY)
            .setPrettyPrinting()
            .registerTypeAdapterFactory(new LowercaseEnumTypeAdapterFactory())
            .serializeNulls()
            .create();

    public static final Gson GSON_REQUEST = new GsonBuilder()
            .setExclusionStrategies(new Jackson2JsonIgnoreStrategy())
            .enableComplexMapKeySerialization()
            .setDateFormat(JSON_DATE_FORMAT)
            .setFieldNamingStrategy(Jackson2FieldNamingStrategy.STRATEGY)
            .setPrettyPrinting()
            .registerTypeAdapterFactory(new LowercaseEnumTypeAdapterFactory())
            .create();
}
