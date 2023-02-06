package ru.yandex.autotests.metrika.core;

import org.apache.http.NameValuePair;
import org.apache.http.client.utils.URIBuilder;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;

import java.util.ArrayList;
import java.util.List;

/**
 * Created by konkov on 21.07.2015.
 */
public class MetrikaURIBuilder extends URIBuilder {

    /**
     * Некоторые общие параметры запроса, добавляются в запрос, если не были заданы извне.
     */
    private IFormParameters commonParameters;

    public void setCommonParameters(IFormParameters commonParameters) {
        this.commonParameters = commonParameters;
    }

    public IFormParameters getCommonParameters() {
        return commonParameters;
    }

    @Override
    public URIBuilder setParameters(final List<NameValuePair> nvps) {
        super.setParameters(merge(commonParameters.getParameters(), nvps));
        return this;
    }

    @Override
    public URIBuilder setParameters(final NameValuePair... nvps) {
        super.setParameters(nvps);
        addParameters(commonParameters.getParameters());
        return this;
    }

    private static List<NameValuePair> merge(final List<NameValuePair> base, final List<NameValuePair> params) {
        List<NameValuePair> result = new ArrayList<>(params);
        //если p.getName() нет в params, то нужно его туда добавить
        base.stream()
                .filter(p -> !result.stream().anyMatch(r -> r.getName().equals(p.getName())))
                .forEach(result::add);
        return result;
    }
}
