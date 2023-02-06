package ru.yandex.autotests.metrika.serializers;

import com.google.common.collect.ImmutableSet;
import com.google.gson.*;
import org.apache.http.message.BasicNameValuePair;
import ru.yandex.autotests.metrika.data.b2b.B2bSample;
import ru.yandex.autotests.metrika.data.common.handles.RequestType;
import ru.yandex.autotests.metrika.data.common.handles.RequestTypes;
import ru.yandex.autotests.metrika.data.parameters.FreeFormParameters;

import java.lang.reflect.Type;
import java.util.function.Supplier;

/**
 * Created by konkov on 15.07.2016.
 */
public class B2bSampleDeserializer implements JsonDeserializer<B2bSample> {

    /**
     * Типы запросов в семплах
     */
    private static final ImmutableSet<RequestType<?>> REQUEST_TYPES = ImmutableSet.<RequestType<?>>builder()
            .add(RequestTypes.TABLE)
            .add(RequestTypes.DRILLDOWN)
            .add(RequestTypes.COMPARISON)
            .add(RequestTypes.COMPARISON_DRILLDOWN)
            .add(RequestTypes.BY_TIME)
            .build();

    @Override
    public B2bSample deserialize(JsonElement json, Type typeOfT, JsonDeserializationContext context)
            throws JsonParseException {
        try {
            JsonObject jsonObject = json.getAsJsonObject();
            return new B2bSample()
                    .withTitle(jsonObject.get("title").getAsString())
                    .withRequestType(REQUEST_TYPES.stream()
                            .filter(r -> r.getTitle().equals(jsonObject.get("request_type").getAsString()))
                            .findFirst()
                            .get())
                    .withParameters(jsonObject.get("parameters").getAsJsonObject().entrySet()
                            .stream()
                            .map(e -> new BasicNameValuePair(e.getKey(), e.getValue().getAsString()))
                            .collect((Supplier<FreeFormParameters>) FreeFormParameters::makeParameters,
                                    (params, param) -> params.append(param.getName(), param.getValue()),
                                    FreeFormParameters::append));
        } catch (Exception e) {
            throw new JsonParseException(String.format("Ошибка десериализации %s из %s", typeOfT.toString(),
                    json.toString()), e);
        }
    }
}
