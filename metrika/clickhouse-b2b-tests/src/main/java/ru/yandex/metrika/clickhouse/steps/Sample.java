package ru.yandex.metrika.clickhouse.steps;

import com.google.common.collect.ImmutableMap;
import freemarker.ext.beans.BeansWrapper;
import freemarker.template.Configuration;
import freemarker.template.Template;
import freemarker.template.TemplateException;
import freemarker.template.TemplateExceptionHandler;
import okhttp3.Headers;
import okhttp3.HttpUrl;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import org.apache.http.NameValuePair;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import ru.yandex.autotests.metrika.commons.clients.http.FreeFormParameters;

import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.util.Map;
import java.util.concurrent.TimeUnit;

public class Sample {

    private static final Logger LOG = LogManager.getLogger(Sample.class);

    private static final Map<String, String> HANDLE_TO_DATA_FIELD_EXCEPTIONS = ImmutableMap.<String, String>builder()
            .put("/analytics/v3/data/ga", "rows")
            .put("/stat/v1/custom/cross_device", "rows")
            .put("/maps/v1/data/form", "forms")
            .put("/v1/cohort/analysis", "cohort_analysis_data")
            .put("/v1/traffic/sources/events", "events_info")
            .build();

    private static final OkHttpClient CLIENT = new OkHttpClient.Builder()
            .readTimeout(120L, TimeUnit.SECONDS)
            .writeTimeout(5L, TimeUnit.SECONDS)
            .connectTimeout(10L, TimeUnit.SECONDS)
            .build();

    private String handle;
    private String params;
    private int counter;
    private int seq;
    private String id;
    private FreeFormParameters dynamicParams;
    private FreeFormParameters headers;
    private URL refHost;
    private URL testHost;

    public String getHandle() {
        return handle;
    }

    public String getParams() {
        return params;
    }

    public int getCounter() {
        return counter;
    }

    public int getSeq() {
        return seq;
    }

    public String getId() {
        return id;
    }

    public FreeFormParameters getDynamicParams() {
        return dynamicParams;
    }

    public FreeFormParameters getHeaders() {
        return headers;
    }

    private ResponseDescriptor executeRequest(Request request) {
        LOG.debug(request.toString());
        ResponseDescriptor.Builder builder = ResponseDescriptor.builder().withRequest(request);
        try {
            builder.withResponse(CLIENT.newCall(request).execute());
        } catch (IOException e) {
            builder.withException(e);
        }
        return builder.build();
    }

    private Request getRequestTo(URL host) {
        HttpUrl.Builder urlBuilder = HttpUrl.get(host).newBuilder(getHandle() + "?" + getParams());
        for (NameValuePair parameter : getDynamicParams().getParameters()) {
            urlBuilder.addQueryParameter(parameter.getName(), parameter.getValue());
        }
        Headers.Builder headersBuilder = Headers.of().newBuilder();
        for (NameValuePair parameter : getHeaders().getParameters()) {
            headersBuilder.add(parameter.getName(), parameter.getValue());
        }
        return new Request.Builder().get().url(urlBuilder.build()).headers(headersBuilder.build()).build();
    }

    public SampleResult perform(Path reportDestination) {
        LOG.trace("Start perform");
        SampleResult sampleResult = SampleResult.builder()
                .withHandle(this.handle)
                .withParams(this.params)
                .withCounter(this.counter)
                .withSeq(this.seq)
                .withId(this.id)
                .withDynamicParams(this.dynamicParams)
                .withRefHost(this.refHost)
                .withTestHost(this.testHost)
                .start()
                .withDiff(new DifferenceDescriptor(getDataField(), executeRequest(getRequestTo(testHost)), executeRequest(getRequestTo(refHost))))
                .finish()
                .build();
        writeReport(sampleResult, reportDestination);
        LOG.trace("Finish perform");
        return sampleResult;
    }

    private void writeReport(SampleResult sample, Path reportDestinaton) {
        Path dst = reportDestinaton.resolve(sample.getDiff().getResultKind().name());
        dst.toFile().mkdirs();

        Configuration configuration = new Configuration();
        configuration.setTemplateExceptionHandler(TemplateExceptionHandler.HTML_DEBUG_HANDLER);
        configuration.setClassForTemplateLoading(this.getClass(), "/");
        configuration.setOutputEncoding("UTF-8");
        configuration.setDefaultEncoding("UTF-8");
        try {
            Template template = configuration.getTemplate("Sample.html.ftl");
            Map<String, Object> root = ImmutableMap.<String, Object>builder()
                    .put("sample", sample)
                    .put("ResultKind", BeansWrapper.getDefaultInstance().getEnumModels().get("ru.yandex.metrika.clickhouse.steps.DifferenceDescriptor$ResultKind"))
                    .build();
            template.process(root, new OutputStreamWriter(new FileOutputStream(dst.resolve(String.format("%s.html", id)).toFile()), StandardCharsets.UTF_8));
        } catch (TemplateException | IOException e) {
            throw new RuntimeException("Error while processing template.", e);
        }
    }

    private String getDataField() {
        return HANDLE_TO_DATA_FIELD_EXCEPTIONS.getOrDefault(handle, "data");
    }

    private Sample(Builder builder) {
        this.handle = builder.handle;
        this.params = builder.params;
        this.counter = builder.counter;
        this.seq = builder.seq;
        this.id = builder.id;
        this.dynamicParams = new FreeFormParameters().append(builder.dynamicParams);
        this.headers = new FreeFormParameters().append(builder.headers);
        this.refHost = builder.refHost;
        this.testHost = builder.testHost;
    }

    public static Builder builder() {
        return new Builder();
    }

    public static class Builder {
        private String handle;
        private String params;
        private int counter;
        private int seq;
        private String id;
        private FreeFormParameters dynamicParams = FreeFormParameters.makeParameters();
        private FreeFormParameters headers;
        private URL refHost;
        private URL testHost;

        public Builder withHandle(final String handle) {
            this.handle = handle;
            return this;
        }

        public Builder withParams(final String params) {
            this.params = params;
            return this;
        }

        public Builder withCounter(final int counter) {
            this.counter = counter;
            return this;
        }

        public Builder withSeq(final int seq) {
            this.seq = seq;
            return this;
        }

        public Builder withId(final String id) {
            this.id = id;
            return this;
        }

        public Builder withDynamicParams(final FreeFormParameters dynamicParams) {
            this.dynamicParams = dynamicParams;
            return this;
        }

        public Builder withHeaders(FreeFormParameters headers) {
            this.headers = headers;
            return this;
        }

        public Builder withRefHost(final URL refHost) {
            this.refHost = refHost;
            return this;
        }

        public Builder withTestHost(final URL testHost) {
            this.testHost = testHost;
            return this;
        }

        private Builder() {
        }

        public Sample build() {
            return new Sample(this);
        }
    }
}
