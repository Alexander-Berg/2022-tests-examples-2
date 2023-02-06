package ru.yandex.autotests.metrika.appmetrica.utils;

import com.google.common.collect.ImmutableSet;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.appmetrica.wrappers.GrantWrapper;

import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Collection;
import java.util.Date;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

import static com.google.common.collect.Iterables.getFirst;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assumeThat;
import static ru.yandex.autotests.metrika.appmetrica.parameters.FreeFormParameters.makeParameters;
import static ru.yandex.metrika.api.management.client.external.GrantType.AGENCY_EDIT;
import static ru.yandex.metrika.api.management.client.external.GrantType.AGENCY_VIEW;

/**
 * Created by konkov on 05.05.2016.
 */
public class Utils {

    public static IFormParameters aggregate(IFormParameters... parameterses) {
        return makeParameters().append(parameterses);
    }

    public static Map<String, String> toMap(IFormParameters parameters) {
        return makeParameters().append(parameters);
    }

    public static <T> T single(Collection<T> collection) {
        assumeThat("присутствует ровно один элемент", collection.size(), equalTo(1));
        return getFirst(collection, null);
    }

    public static boolean isAgency(GrantWrapper grant) {
        return ImmutableSet.of(AGENCY_VIEW, AGENCY_EDIT).contains(grant.getGrant().getPerm());
    }

    public static String formatIsoDtf(Date date) {
        return DateTimeFormatter.ISO_DATE_TIME.format(ZonedDateTime.ofInstant(date.toInstant(), ZoneId.systemDefault()));
    }

    public static List<Double> listDifference(List<Double> first, List<Double> second) {
        return IntStream.range(0, first.size())
                .mapToObj(i -> Math.abs(first.get(i) - second.get(i)))
                .collect(Collectors.toList());
    }

}
