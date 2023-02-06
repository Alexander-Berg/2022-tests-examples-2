package ru.yandex.autotests.metrika.core;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;

import ru.yandex.autotests.metrika.core.jodatime.DateTimeConverter;
import ru.yandex.autotests.metrika.core.jodatime.LocalDateConverter;
import ru.yandex.autotests.metrika.core.jodatime.LocalDateTimeConverter;
import ru.yandex.autotests.metrika.core.jodatime.LocalTimeConverter;
import ru.yandex.autotests.metrika.data.b2b.B2bSample;
import ru.yandex.autotests.metrika.factories.LowercaseEnumTypeAdapterFactory;
import ru.yandex.autotests.metrika.serializers.Jackson2FieldNamingStrategy;

import static ru.yandex.autotests.metrika.core.jodatime.DateTimeConverter.DATE_TIME_TYPE;
import static ru.yandex.autotests.metrika.core.jodatime.LocalDateConverter.LOCAL_DATE_TYPE;
import static ru.yandex.autotests.metrika.core.jodatime.LocalDateTimeConverter.LOCAL_DATE_TIME_TYPE;
import static ru.yandex.autotests.metrika.core.jodatime.LocalTimeConverter.LOCAL_TIME_TYPE;
import static ru.yandex.autotests.metrika.utils.Utils.JSON_DATE_FORMAT;

/**
 * Created by konkov on 20.03.2015.
 */
public class MetrikaJson {

    public static final Gson GSON_RESPONSE = new GsonBuilder()
            .enableComplexMapKeySerialization()
            .setDateFormat(JSON_DATE_FORMAT)
            .setFieldNamingStrategy(Jackson2FieldNamingStrategy.STRATEGY)
            .setPrettyPrinting()
            .registerTypeAdapterFactory(new LowercaseEnumTypeAdapterFactory())
            .registerTypeAdapter(DATE_TIME_TYPE, new DateTimeConverter())
            .registerTypeAdapter(LOCAL_DATE_TIME_TYPE, new LocalDateTimeConverter())
            .registerTypeAdapter(LOCAL_DATE_TYPE, new LocalDateConverter())
            .registerTypeAdapter(LOCAL_TIME_TYPE, new LocalTimeConverter())
            .serializeNulls()
            .create();

    public static final Gson GSON_REQUEST = new GsonBuilder()
            .enableComplexMapKeySerialization()
            .setDateFormat(JSON_DATE_FORMAT)
            .setFieldNamingStrategy(Jackson2FieldNamingStrategy.STRATEGY)
            .setPrettyPrinting()
            .registerTypeAdapterFactory(new LowercaseEnumTypeAdapterFactory())
            .registerTypeAdapter(DATE_TIME_TYPE, new DateTimeConverter())
            .registerTypeAdapter(LOCAL_DATE_TIME_TYPE, new LocalDateTimeConverter())
            .registerTypeAdapter(LOCAL_DATE_TYPE, new LocalDateConverter())
            .registerTypeAdapter(LOCAL_TIME_TYPE, new LocalTimeConverter())
            .create();

}
