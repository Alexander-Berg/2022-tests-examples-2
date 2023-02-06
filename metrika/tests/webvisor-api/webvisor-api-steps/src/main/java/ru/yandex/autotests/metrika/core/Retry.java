package ru.yandex.autotests.metrika.core;

import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableSet;
import org.apache.commons.lang3.StringUtils;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.apache.commons.lang3.tuple.Pair;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.methods.HttpHead;
import org.apache.http.client.methods.HttpOptions;
import org.apache.http.conn.ConnectTimeoutException;
import org.apache.http.conn.HttpHostConnectException;
import ru.yandex.autotests.metrika.beans.schemes.ProfileOnlySchema;
import ru.yandex.metrika.spring.profile.DBType;
import ru.yandex.metrika.spring.profile.ProfileQuery;

import java.net.NoRouteToHostException;
import java.net.SocketTimeoutException;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.TimeoutException;
import java.util.regex.Pattern;

import static com.google.common.base.Preconditions.checkNotNull;

/**
 * Created by konkov on 09.06.2017.
 */
public final class Retry {

    private static final List<Pair<DBType, Pattern>> QUERY_SIGNATURES = ImmutableList.<Pair<DBType, Pattern>>builder()
            .add(ImmutablePair.of(DBType.METRAGE, Pattern.compile("^http request error")))
            .add(ImmutablePair.of(DBType.METRAGE, Pattern.compile("^Metrage error: Read timed out$")))
            .add(ImmutablePair.of(DBType.CLICKHOUSE, Pattern.compile("^ClickHouse exception, code: 160")))
            .add(ImmutablePair.of(DBType.CLICKHOUSE, Pattern.compile("^ClickHouse exception, code: 159")))
            .add(ImmutablePair.of(DBType.CLICKHOUSE, Pattern.compile("^ClickHouse exception, code: 210,.* failed: connect timed out at .*, code 210$")))
            .add(ImmutablePair.of(DBType.CLICKHOUSE, Pattern.compile("(?s)^ClickHouse exception, code: 49,.* Query log have been already shutdown, .*, code 49$")))
            .build();

    private static final List<Pattern> EXCEPTION_SIGNATURES = ImmutableList.<Pattern>builder()
            .add(Pattern.compile("ru.yandex.metrika.util.chunk.clickhouse.haze.CreateHazeChunkException:.*ClickHouse exception, code: 1002.*failed to respond.*code 1002"))
            .add(Pattern.compile("ru.yandex.metrika.util.chunk.clickhouse.haze.CreateHazeChunkException:.*ClickHouse exception, code: 210.*connect timed out.*code 210"))
            .build();

    private static final Set<String> SAFE_HTTP_METHODS = ImmutableSet.of(
            HttpGet.METHOD_NAME,
            HttpHead.METHOD_NAME,
            HttpOptions.METHOD_NAME
    );

    public static boolean isRetryable(ProfileOnlySchema profileOnlySchema) {
        return Retry.isRetryable(profileOnlySchema.getCode()) ||
                (profileOnlySchema.getProfile() != null && profileOnlySchema.getProfile().getQueries().stream()
                        .anyMatch(p -> Retry.isRetryable(p))) ||
                (profileOnlySchema.getProfile() != null && isRetryable(profileOnlySchema.getProfile().getAdditional()));
    }

    private static boolean isRetryable(Map<String, Object> additional) {
        if (additional != null) {
            List<List<String>> exception = (List<List<String>>) additional.get("exception");
            if (exception != null) {
                return exception.stream()
                        .anyMatch(e -> e.stream()
                                .anyMatch(s -> EXCEPTION_SIGNATURES.stream()
                                        .anyMatch(p -> p.matcher(s).find())));
            } else {
                return false;
            }
        } else {
            return false;
        }
    }

    private static boolean isRetryable(ProfileQuery query) {
        if (StringUtils.isEmpty(query.getErrorMessage())) {
            return false;
        } else {
            return QUERY_SIGNATURES.stream()
                    .anyMatch(p -> p.getLeft().equals(query.getDbType())
                            && p.getRight().matcher(query.getErrorMessage()).find());
        }
    }

    private static boolean isRetryable(Long code) {
        return code != null && code == 504L;
    }

    public static boolean isRetryable(Throwable e, String method) {
        checkNotNull(e);
        if (e instanceof ExecutionException) {
            e = e.getCause();
        }

        if (e instanceof ConnectTimeoutException || e instanceof HttpHostConnectException || e instanceof NoRouteToHostException) {
            // если не удалось подключиться, можно поретраить любой метод
            return true;
        }

        if (SAFE_HTTP_METHODS.contains(method)) {
            if (e instanceof TimeoutException || e instanceof SocketTimeoutException) {
                // в случае таймаута после подключения неизвестно, был ли выполнен запрос на стороне сервера
                // поэтому можно поретраить только "безопасные" методы
                return true;
            }
        }

        return false;
    }
}
