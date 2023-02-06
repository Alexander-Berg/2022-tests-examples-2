package ru.yandex.autotests.advapi.core;

import org.apache.http.StatusLine;
import org.apache.log4j.LogManager;
import org.apache.log4j.Logger;
import ru.yandex.autotests.httpclient.lite.core.BackEndResponse;
import ru.yandex.autotests.httpclient.lite.core.ResponseContent;
import ru.yandex.autotests.irt.testutils.allure.AllureUtils;

import static java.util.stream.Collectors.joining;

/**
 * Created by konkov on 25.11.2015.
 */
public abstract class MetrikaBaseResponse {

    private static final Logger log = LogManager.getLogger(MetrikaBaseResponse.class);

    protected final BackEndResponse backEndResponse;

    public MetrikaBaseResponse(BackEndResponse backEndResponse) {
        this.backEndResponse = backEndResponse;
    }

    public ResponseContent getResponseContent() {
        return backEndResponse.getResponseContent();
    }

    public StatusLine getStatusLine() {
        return backEndResponse.getStatusLine();
    }

    protected void logHeaders() {
        String headers = backEndResponse.getHeaders()
                .stream()
                .map(header -> String.format("%s: %s", header.getName(), header.getValue()))
                .collect(joining(System.lineSeparator()));

        log.info("Response headers");
        log.info(headers);

        AllureUtils.addTextAttachment("Response headers", headers);
    }
}
