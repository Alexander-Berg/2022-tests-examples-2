package ru.yandex.autotests.topsites.core;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonDeserializer;
import com.google.gson.reflect.TypeToken;
import org.joda.time.LocalDate;
import org.joda.time.YearMonth;
import ru.yandex.autotests.metrika.commons.clients.http.LowercaseEnumTypeAdapterFactory;
import ru.yandex.autotests.metrika.commons.clients.http.jackson.Jackson2FieldNamingStrategy;
import ru.yandex.autotests.metrika.commons.clients.http.jackson.Jackson2JsonIgnoreStrategy;

public class TopSitesJson {

    private static final String JSON_DATE_FORMAT = "yyyy-MM-dd'T'HH:mm:ssX";

    public static final Gson GSON_RESPONSE = new GsonBuilder()
            .registerTypeAdapter(new TypeToken<LocalDate>(){}.getType(), (JsonDeserializer<LocalDate>)(jsonElement, type, jsonDeserializationContext) -> LocalDate.parse(jsonElement.getAsString()))
            .registerTypeAdapter(new TypeToken<YearMonth>(){}.getType(), (JsonDeserializer<YearMonth>) (jsonElement, type, jsonDeserializationContext) -> YearMonth.parse(jsonElement.getAsString()))
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
