package ru.yandex.autotests.advapi.core;

import com.google.common.collect.ImmutableList;
import org.apache.commons.lang3.StringUtils;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.apache.commons.lang3.tuple.Pair;
import org.apache.http.conn.HttpHostConnectException;
import ru.yandex.autotests.advapi.beans.ProfileOnlySchema;
import ru.yandex.metrika.spring.profile.DBType;
import ru.yandex.metrika.spring.profile.ProfileQuery;

import java.net.NoRouteToHostException;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ExecutionException;
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

    public static boolean isRetryable(Throwable e) {
        checkNotNull(e);
        if (e instanceof ExecutionException &&
                (e.getCause() instanceof HttpHostConnectException
                        || e.getCause() instanceof NoRouteToHostException)) {
            return false;
        } else {
            return true;
        }
    }

    public static boolean isRetryable(ProfileOnlySchema profileOnlySchema) {
        return Retry.isRetryable(profileOnlySchema.getCode()) ||
                (profileOnlySchema.getProfile() != null && profileOnlySchema.getProfile().getQueries().stream()
                        .anyMatch(Retry::isRetryable)) ||
                (profileOnlySchema.getProfile() != null && isRetryable(profileOnlySchema.getProfile().getAdditional()));
    }
}
