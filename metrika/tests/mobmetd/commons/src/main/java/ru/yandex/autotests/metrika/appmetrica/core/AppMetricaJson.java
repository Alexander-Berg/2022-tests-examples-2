package ru.yandex.autotests.metrika.appmetrica.core;

import com.google.gson.*;

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;

public class AppMetricaJson {

    public static final String JSON_DATE_FORMAT = "yyyy-MM-dd'T'HH:mm:ssX";

    public static Gson createGsonRequest(TypeAdapterFactory typeAdapterFactory) {
        return new GsonBuilder()
                .enableComplexMapKeySerialization()
                // Это для java.util.Date, java.sql.Timestamp, java.sql.Date
                .setDateFormat(JSON_DATE_FORMAT)
                // Это для java.time.LocalDate
                .registerTypeAdapter(
                        LocalDate.class,
                        (JsonSerializer<LocalDate>) (date, typeOfSrc, context) ->
                                new JsonPrimitive(date.format(DateTimeFormatter.ISO_LOCAL_DATE)))
                .setFieldNamingStrategy(Jackson2FieldNamingStrategy.STRATEGY)
                .setPrettyPrinting()
                .registerTypeAdapterFactory(typeAdapterFactory)
                .create();
    }

    public static Gson createGsonResponse(TypeAdapterFactory typeAdapterFactory) {
        return new GsonBuilder()
                .enableComplexMapKeySerialization()
                // Это для java.util.Date, java.sql.Timestamp, java.sql.Date
                .setDateFormat(JSON_DATE_FORMAT)
                // Это для java.time.LocalDate
                .registerTypeAdapter(
                        LocalDate.class,
                        (JsonDeserializer<LocalDate>) (json, type, jsonDeserializationContext) ->
                                LocalDate.parse(json.getAsJsonPrimitive().getAsString()))
                .setFieldNamingStrategy(Jackson2FieldNamingStrategy.STRATEGY)
                .setPrettyPrinting()
                .registerTypeAdapterFactory(typeAdapterFactory)
                .serializeNulls()
                .create();
    }
}
