package ru.yandex.metrika.api.constructor.ga;

import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.function.Function;

import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.collect.Lists;
import com.google.common.collect.Maps;
import com.google.common.collect.Sets;
import org.apache.http.HttpResponse;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.impl.conn.PoolingClientConnectionManager;
import org.apache.http.util.EntityUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import ru.yandex.metrika.api.error.ga.GAConstructorError;
import ru.yandex.metrika.util.collections.StringMap;
import ru.yandex.metrika.util.io.UncheckedIOException;

/**
 * @author jkee
 */

public class GAApiComparator {

    private static final Logger log = LoggerFactory.getLogger(GAApiComparator.class);

    private String leftUrl = "http://metrika-dev.yandex.ru:12345/analytics/v3/data/ga";
    private String rightUrl = "https://www.googleapis.com/analytics/v3/data/ga";

    private double valuesDiffThreshold = 0.2;
    private double keysIntersectionDiffThreshold = 0.1;

    private String leftToken;
    private String rightToken;

    private String leftIds;
    private String rightIds;

    private HttpClient client;
    private ObjectMapper mapper;

    private List<Result> results;

    private List<String> dims;
    private List<String> metrics;
    private String fixedDim;
    private String fixedMetric;

    private Set<String> goodAttrs;

    private Function<String, Boolean> isMetrStub = t->true;
    private Function<String, Boolean> isDimStub = t->true;

    public void init() throws Exception {
        client = new DefaultHttpClient(new PoolingClientConnectionManager());
        mapper = new ObjectMapper();
        mapper.configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);
        /**
         * А это нужно чтобы кривые ga dimensions в виде строки маппилось на нашу правильную реализацию
         */
        mapper.configure(DeserializationFeature.ACCEPT_SINGLE_VALUE_AS_ARRAY, true);
        results = Lists.newArrayList();
    }

    public void compare() {
        for (String dim : dims) {
            compareOne(fixedMetric, dim, false);
        }

        for (String metr : metrics) {
            compareOne(metr, fixedDim, true);
        }
    }

    public void log() {
        log.info("Dims:");
        log(false);
        log.info("Metrics:");
        log(true);
    }

    public boolean fail() {
        return results.stream().map(i->i.ourFail).reduce(false, (f1, f2) -> f1 || f2);
    }

    private void compareOne(String metric, String dim, boolean isMetric) {
        StringMap params = StringMap.newMap()
                .with("ids", "ga:55193146")
                .with("start-date", "7daysAgo")
                .with("end-date", "yesterday")
                .with("dimensions", dim)
                .with("oauth_token", leftToken)
                .with("metrics", metric)
                .with("filters", "ga:pageviews%3E100")
                .with("sort", '-' + metric);

        StringMap rightParams = params
                .with("oauth_token", rightToken)
                .with("ids", "ga:683245");
        String target = isMetric ? metric : dim;
        Result result = new Result(target);
        result.setMetric(isMetric);
        boolean isStub = isMetric ? isMetrStub.apply(metric) : isDimStub.apply(dim);
        result.setStub(isStub);
        if (!isStub) log.info(target);
        try {
            GAConstructorResponse left = null;
            try {
                long base = System.currentTimeMillis();
                left = makeRequest(params, leftUrl, !isStub);
                long time = System.currentTimeMillis() - base;
                result.setLeftTime(time);
            } catch (Exception e) {
                result.setReason("Left fail: " + e.getMessage());
                result.setGaFail(true);
                results.add(result);
                return;
            }
            long base = System.currentTimeMillis();
            GAConstructorResponse right = makeRequest(rightParams, rightUrl, !isStub);
            long time = System.currentTimeMillis() - base;
            result.setRightTime(time);
            if (!isStub) {
                String errors = findErrors(left, right);
                if (errors == null || (goodAttrs != null && goodAttrs.contains(isMetric ? metric : dim))) {
                    log.info("Success: {}", target);
                } else {
                    log.warn("Error found: {}  {}", dim, errors);
                    result.setReason(errors);
                    result.setOurFail(true);
                }
            }
        } catch (Exception e) {
            if (!isStub) log.warn("FAIL: {} : {}", target, e.getMessage());
            if (!isStub) log.debug("FAIL: {}", target, e);
            result.setReason("EXC: " + e.getMessage());
            result.setOurFail(true);
        }
        results.add(result);
    }



    private String findErrors(GAConstructorResponse left, GAConstructorResponse right) {
        List<List<String>> leftRows = left.getRows();
        List<List<String>> rightRows = right.getRows();

        int dimsNum = left.getQuery().getDimensions().size();
        int metrsNum = left.getQuery().getMetrics().size();

        if (leftRows == null && rightRows == null) return null;
        if (leftRows == null || rightRows == null) return "Size mismatch - one empty";

        if (dimsNum > 0) {

            // 1. Проверяем пересечение по ключам
            Map<List<String>, List<String>> leftKeys = Maps.newHashMap();
            Map<List<String>, List<String>> rightKeys = Maps.newHashMap();
            for (List<String> leftRow : leftRows) {
                leftKeys.put(leftRow.subList(0, dimsNum), leftRow.subList(dimsNum, leftRow.size()));
            }
            for (List<String> rightRow : rightRows) {
                rightKeys.put(rightRow.subList(0, dimsNum), rightRow.subList(dimsNum, rightRow.size()));
            }

            //Sets.newHashSet(leftRows.subList(0, dimsNum + 1));
            Set<List<String>> intersection = Sets.intersection(leftKeys.keySet(), rightKeys.keySet());
            // пересечение должно быть по размеру >= порог
            if (Math.abs((leftKeys.size() - intersection.size()) / leftKeys.size()) > keysIntersectionDiffThreshold) {
                return "keys mismatch: left keys";
            }
            if (Math.abs((rightKeys.size() - intersection.size()) / rightKeys.size()) > keysIntersectionDiffThreshold) {
                return "keys mismatch: right keys";
            }

            // 2. Проверяем для ключей пересечения по метрикам
            for (List<String> key : intersection) {
                List<String> leftMetrics = leftKeys.get(key);
                List<String> rightMetrics = rightKeys.get(key);
                if (leftMetrics.size() != rightMetrics.size()) return "Row size mismatch";
                for (int j = 0; j < leftMetrics.size(); j++) {
                    // metrics
                    if (isMetrStub.apply(left.getQuery().getMetrics().get(j))) continue;
                    double leftValue = Double.parseDouble(leftMetrics.get(j));
                    double rightValue = Double.parseDouble(rightMetrics.get(j));
                    if (Math.abs((leftValue - rightValue) / leftValue) > valuesDiffThreshold) {
                        return "metrics mismatch: " + leftValue + "  " + rightValue;
                    }
                }
            }
        }

        // чекаем totals и расходимся
        for (int i = 0; i < metrsNum; i++) {
            double leftValue = Double.parseDouble(left.getTotalsForAllResults().get(left.getQuery().getMetrics().get(i)));
            double rightValue = Double.parseDouble(right.getTotalsForAllResults().get(right.getQuery().getMetrics().get(i)));
            if (Math.abs((leftValue - rightValue) / leftValue) > valuesDiffThreshold) {
                return "totals mismatch: " + leftValue + "  " + rightValue;
            }
        }


        return null;
    }

    private GAConstructorResponse makeRequest(StringMap params, String url, boolean isLog) throws Exception {
        StringBuilder urlBuilder = new StringBuilder(url).append('?');
        for (String key : params.keySet()) {
            urlBuilder.append(key).append('=').append(params.get(key)).append('&');
        }
        if (isLog) log.info(urlBuilder.toString());
        HttpGet request = new HttpGet(urlBuilder.toString());
        HttpResponse response = client.execute(request);
        GAConstructorResponse gaConstructorResponse;
        try {
            if (response.getStatusLine().getStatusCode() != 200) {
                try {
                    GAConstructorError error = mapper.readValue(response.getEntity().getContent(), GAConstructorError.class);
                    /*if ("Selected dimensions and metrics cannot be queried together.".equals(error.getMessage())) {
                        return null;
                    }*/
                    if (error != null && error.getMessage() != null) {
                        throw new UncheckedIOException(error.getMessage());
                    }
                } catch (IOException ignore) {
                }
                throw new UncheckedIOException("Response code: " + response.getStatusLine().getStatusCode());
            }
            gaConstructorResponse = mapper.readValue(response.getEntity().getContent(), GAConstructorResponse.class);
            EntityUtils.consumeQuietly(response.getEntity());
        } finally {
            try {
                response.getEntity().getContent().close();
            } catch (Exception ignored) {
            }
            request.reset();
        }
        return gaConstructorResponse;
    }

    private void log(boolean metrics) {
        int success = 0;
        int successStub = 0;
        int failed = 0;
        int failedStub = 0;
        int gaFailed = 0;

        long sumLeftTime = 0;
        long sumRightTime = 0;

        for (Result result : results) {
            if (result.isMetric != metrics) continue;
            if (result.ourFail) {
                if (result.isStub) failedStub += 1;
                else failed += 1;
            } else if (result.gaFail) {
                gaFailed += 1;
            } else {
                if (result.isStub) successStub += 1;
                else {
                    success += 1;
                    sumLeftTime += result.getLeftTime();
                    sumRightTime += result.getRightTime();
                }
            }
        }
        log.info("Success: {}", success);
        log.info("SuccessStub: {}", successStub);
        log.info("Failed: {}", failed);
        log.info("FailedStub: {}", failedStub);
        log.info("gaFailed: {}", gaFailed);
        log.info("left time: {}", ((double) sumLeftTime) / success);
        log.info("right time: {}", ((double) sumRightTime) / success);
    }

    public void setLeftUrl(String leftUrl) {
        this.leftUrl = leftUrl;
    }

    public void setRightUrl(String rightUrl) {
        this.rightUrl = rightUrl;
    }

    public void setValuesDiffThreshold(double valuesDiffThreshold) {
        this.valuesDiffThreshold = valuesDiffThreshold;
    }

    public void setKeysIntersectionDiffThreshold(double keysIntersectionDiffThreshold) {
        this.keysIntersectionDiffThreshold = keysIntersectionDiffThreshold;
    }

    public void setLeftToken(String leftToken) {
        this.leftToken = leftToken;
    }

    public void setRightToken(String rightToken) {
        this.rightToken = rightToken;
    }

    public void setDims(List<String> dims) {
        this.dims = dims;
    }

    public void setMetrics(List<String> metrics) {
        this.metrics = metrics;
    }

    public void setFixedDim(String fixedDim) {
        this.fixedDim = fixedDim;
    }

    public void setFixedMetric(String fixedMetric) {
        this.fixedMetric = fixedMetric;
    }

    public void setIsDimStub(Function<String, Boolean> isDimStub) {
        this.isDimStub = isDimStub;
    }

    public void setIsMetrStub(Function<String, Boolean> isMetrStub) {
        this.isMetrStub = isMetrStub;
    }

    public Set<String> getGoodAttrs() {
        return goodAttrs;
    }

    public void setGoodAttrs(Set<String> goodAttrs) {
        this.goodAttrs = goodAttrs;
    }
}
