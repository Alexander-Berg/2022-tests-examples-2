package ru.yandex.autotests.audience.internal.api.core;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import ru.yandex.autotests.metrika.commons.clients.http.LowercaseEnumTypeAdapterFactory;
import ru.yandex.autotests.metrika.commons.clients.http.jackson.Jackson2FieldNamingStrategy;
import ru.yandex.autotests.metrika.commons.clients.http.jackson.Jackson2JsonIgnoreStrategy;

public class AudienceIntapiJson {

    private static final String JSON_DATE_FORMAT = "yyyy-MM-dd'T'HH:mm:ssX";

    public static final Gson GSON_RESPONSE = new GsonBuilder()
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
