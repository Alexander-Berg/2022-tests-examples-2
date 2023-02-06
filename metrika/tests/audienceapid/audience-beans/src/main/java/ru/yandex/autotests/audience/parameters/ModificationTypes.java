package ru.yandex.autotests.audience.parameters;

import org.apache.http.NameValuePair;
import org.apache.http.message.BasicNameValuePair;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;

import java.util.EnumSet;
import java.util.List;

import static java.util.Collections.singletonList;
import static java.util.stream.Collectors.joining;

/**
 * Created by konkov on 27.03.2017.
 */
public class ModificationTypes implements IFormParameters {

    private final EnumSet<ModificationType> items;

    private ModificationTypes(EnumSet<ModificationType> items) {
        this.items = items;
    }

    public static ModificationTypes all() {
        return new ModificationTypes(EnumSet.allOf(ModificationType.class));
    }

    @Override
    public List<NameValuePair> getParameters() {
        return singletonList(new BasicNameValuePair(ModificationType.PARAMETER_NAME,
                items.stream().map(s -> s.toString()).collect(joining(","))));
    }
}
