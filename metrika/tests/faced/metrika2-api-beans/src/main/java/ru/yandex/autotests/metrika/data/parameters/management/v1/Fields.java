package ru.yandex.autotests.metrika.data.parameters.management.v1;

import ch.lambdaj.function.convert.StringConverter;
import org.apache.http.NameValuePair;
import org.apache.http.message.BasicNameValuePair;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;

import java.util.Arrays;
import java.util.EnumSet;
import java.util.List;

import static ch.lambdaj.collection.LambdaCollections.with;

/**
 * Created by konkov on 24.04.2015.
 */
public class Fields implements IFormParameters {

    private final EnumSet<Field> fields;

    private Fields(EnumSet<Field> fields) {
        this.fields = fields;
    }

    public static Fields all() {
        return new Fields(EnumSet.allOf(Field.class));
    }

    @Override
    public List<NameValuePair> getParameters() {
        String fieldNames = with(fields).convert(new StringConverter<Field>() {
            @Override
            public String convert(Field from) {
                return from.name().toLowerCase();
            }
        }).join(",");

        return Arrays.<NameValuePair>asList(new BasicNameValuePair(Field.PARAMETER_NAME, fieldNames));
    }
}
