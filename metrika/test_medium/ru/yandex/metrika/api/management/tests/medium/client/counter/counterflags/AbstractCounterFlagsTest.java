package ru.yandex.metrika.api.management.tests.medium.client.counter.counterflags;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;

import org.junit.BeforeClass;
import org.junit.ClassRule;
import org.junit.Rule;
import org.junit.runners.Parameterized;
import org.springframework.test.context.junit4.rules.SpringClassRule;
import org.springframework.test.context.junit4.rules.SpringMethodRule;

import ru.yandex.metrika.api.management.client.counter.CounterFlags;
import ru.yandex.metrika.dbclients.MySqlTestSetup;

import static java.util.stream.Collectors.toList;
import static org.assertj.core.util.Arrays.array;
import static ru.yandex.metrika.api.management.client.counter.CounterFlags.Incognito.disabled;
import static ru.yandex.metrika.api.management.client.counter.CounterFlags.Incognito.disabled_by_user;
import static ru.yandex.metrika.api.management.client.counter.CounterFlags.Incognito.enabled_by_classifier;
import static ru.yandex.metrika.api.management.client.counter.CounterFlags.Incognito.enabled_by_user;
import static ru.yandex.metrika.api.management.client.counter.CounterFlags.Incognito.mergeValueFromApi;


public abstract class AbstractCounterFlagsTest {

    @ClassRule
    public static final SpringClassRule scr = new SpringClassRule();

    @Rule
    public final SpringMethodRule smr = new SpringMethodRule();

    @Parameterized.Parameter
    public CounterFlags counterFlags;
    @Parameterized.Parameter(1)
    public CounterFlags expected;

    @BeforeClass
    public static void beforeClass() throws Exception {
        MySqlTestSetup.globalSetup();
    }

    static CounterFlags getExpected(CounterFlags counterFlags) {
        boolean collectFirstPartyData;
        if (enabled_by_user.equals(counterFlags.incognito())) {
            collectFirstPartyData = false;
        } else {
            collectFirstPartyData = counterFlags.collectFirstPartyData() == null || counterFlags.collectFirstPartyData();
        }
        return new CounterFlags(counterFlags.counterId(),
                counterFlags.useInBenchmarks() == null || counterFlags.useInBenchmarks(),
                counterFlags.directAllowUseGoalsWithoutAccess() != null ?
                        counterFlags.directAllowUseGoalsWithoutAccess() : false,
                mergeValueFromApi(counterFlags.incognito(), disabled),
                collectFirstPartyData,
                counterFlags.statisticsOverSite() == null || counterFlags.statisticsOverSite(),
                Boolean.TRUE.equals(counterFlags.newsEnabledByClassifier()) && Boolean.TRUE.equals(counterFlags.newsEnabledByUser()),
                counterFlags.newsEnabledByClassifier() != null ? counterFlags.newsEnabledByClassifier() : false
        );
    }

    protected static List<List<Optional<?>>> getFlagsVariations() {
        List<List<Optional<?>>> result = new ArrayList<>();
        int flagsCount = 7;
        var useInBenchmarksValues = Arrays.asList(Optional.of(true), Optional.of(false));
        var directAllowUseGoalsWithoutAccessValues = Arrays.asList(Optional.of(true), Optional.of(false));
        var incognitoValues = Arrays.asList(Optional.of(disabled), Optional.of(enabled_by_classifier),
                Optional.of(disabled_by_user), Optional.of(enabled_by_user));
        var collectFirstPartyDataValues = Arrays.asList(Optional.of(true), Optional.of(false));
        var statisticsOverSite = Arrays.asList(Optional.of(true), Optional.of(false));
        var newsEnabledByUser = Arrays.asList(Optional.of(true), Optional.of(false));
        var newsEnabledByClassifier = Arrays.asList(Optional.of(true), Optional.of(false));

        //all combinations of each flag values with all others flags nulled
        for (var value : useInBenchmarksValues) {
            result.add(getOptionalEmptyListWithOneValue(flagsCount, 0, value));
        }
        for (var value : directAllowUseGoalsWithoutAccessValues) {
            result.add(getOptionalEmptyListWithOneValue(flagsCount, 1, value));
        }
        for (var value : incognitoValues) {
            result.add(getOptionalEmptyListWithOneValue(flagsCount, 2, value));
        }
        for (var value : collectFirstPartyDataValues) {
            result.add(getOptionalEmptyListWithOneValue(flagsCount, 3, value));
        }
        for (var value : statisticsOverSite) {
            result.add(getOptionalEmptyListWithOneValue(flagsCount, 4, value));
        }
        for (var value : newsEnabledByUser) {
            result.add(getOptionalEmptyListWithOneValue(flagsCount, 5, value));
        }
        for (var value : newsEnabledByClassifier) {
            result.add(getOptionalEmptyListWithOneValue(flagsCount, 6, value));
        }
        //default
        result.add(Arrays.asList(Optional.of(true), Optional.of(true), Optional.of(disabled),
                Optional.of(true), Optional.of(true), Optional.of(false), Optional.of(false)));
        //all flags nulled, to check once
        result.add(getOptionalEmptyListWithOneValue(flagsCount, null, Optional.empty()));
        //some random combination just in case
        result.add(Arrays.asList(Optional.of(false), Optional.of(false), Optional.of(enabled_by_user),
                Optional.of(false), Optional.of(false), Optional.of(false), Optional.of(false)));
        //checking try to enable incognito and collect_first_party_data at the same time
        result.add(Arrays.asList(Optional.of(true), Optional.empty(), Optional.of(enabled_by_user),
                Optional.of(true), Optional.of(true), Optional.of(true), Optional.of(false)));
        return result;
    }

    private static List<Optional<?>> getOptionalEmptyListWithOneValue(Integer size, Integer valuePosition, Optional<?> value) {
        List<Optional<?>> empties = new ArrayList<>();
        for (Integer i = 0; i < size; i++) {
            if (i.equals(valuePosition)) {
                empties.add(value);
            } else {
                empties.add(Optional.empty());
            }
        }
        return empties;
    }

    public static List<Object[]> getAllCounterFlagsVariationsWithExpectedUploadingsResults(Integer counterId) {
        return getFlagsVariations().stream()
                .map(objs -> {
                            var creating = new CounterFlags(counterId,
                                    (Boolean) objs.get(0).orElse(null),
                                    (Boolean) objs.get(1).orElse(null),
                                    (CounterFlags.Incognito) objs.get(2).orElse(null),
                                    (Boolean) objs.get(3).orElse(null),
                                    (Boolean) objs.get(4).orElse(null),
                                    (Boolean) objs.get(5).orElse(null),
                                    (Boolean) objs.get(6).orElse(null)
                            );
                            return array(
                                    creating,
                                    getExpected(creating)
                            );
                        }
                )
                .collect(toList());
    }
}
