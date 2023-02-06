package ru.yandex.metrika.userparams2d.tests;

import java.util.Arrays;
import java.util.Collection;
import java.util.List;
import java.util.Map;

import javax.annotation.Nonnull;

import org.apache.commons.lang3.StringUtils;
import org.hamcrest.Matcher;

import ru.yandex.metrika.api.management.client.external.userparams.UserParamUpdate;
import ru.yandex.metrika.userparams.ListParamWrapper;
import ru.yandex.metrika.userparams.Param;
import ru.yandex.metrika.userparams.ParamOwner;
import ru.yandex.metrika.userparams.ParamOwnerKey;
import ru.yandex.metrika.userparams.UserParamLBCHRow;
import ru.yandex.metrika.userparams2d.steps.TestCountersProvider;

import static java.util.stream.Collectors.groupingBy;
import static java.util.stream.Collectors.toList;
import static org.hamcrest.Matchers.allOf;
import static org.hamcrest.Matchers.anyOf;
import static org.hamcrest.Matchers.closeTo;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.everyItem;
import static org.hamcrest.Matchers.hasEntry;
import static org.hamcrest.Matchers.hasProperty;
import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.Matchers.in;
import static org.hamcrest.Matchers.is;
import static org.hamcrest.Matchers.not;

public class Matchers {

    public static Matcher<List<Param>> matchParams(List<Param> expectedParams) {
        return allOf(
                hasSize(expectedParams.size()),
                everyItem(anyOf(expectedParams.stream().map(Matchers::matchParam).toArray(Matcher[]::new)))
        );
    }

    public static Matcher<Param> matchParam(Param expected) {
        return allOf(
                hasProperty("key", allOf(
                        hasProperty("ownerKey", matchParamOwnerKey(expected.getOwnerKey())),
                        hasProperty("path", equalTo(expected.getPath()))
                )),
                hasProperty("valueString", equalTo(expected.getValueString())),
                hasProperty("valueDouble", equalTo(expected.getValueDouble()))
        );
    }

    public static Matcher<List<ParamOwner>> matchUpdatesOwners(List<UserParamUpdate> updates) {
        var ownersFromUpdates = getOwnersFromUpdates(updates);
        return allOf(
                hasSize(ownersFromUpdates.size()),
                everyItem(anyOf(ownersFromUpdates.stream().map(Matchers::matchOwnerUpdate).toArray(Matcher[]::new)))
        );
    }

    public static Matcher<List<ParamOwner>> matchUpdatesClientUserId(List<UserParamUpdate> updates) {
        var ownersFromUpdates = getOwnersFromUpdates(updates);
        return allOf(
                hasSize((int) updates.stream().map(UserParamUpdate::getParamWrapper).filter(params -> !params.getParams().isEmpty()).count()),
                everyItem(anyOf(ownersFromUpdates.stream().map(Matchers::matchClientUserId).toArray(Matcher[]::new)))
        );
    }

    public static Matcher<List<Param>> matchUpdatesParams(List<UserParamUpdate> updates) {
        return matchParams(getParamsFromUpdates(updates));
    }

    private static List<Param> getParamsFromUpdates(List<UserParamUpdate> updates) {
        return updates.stream().map(UserParamUpdate::getParams).flatMap(Collection::stream).collect(toList());
    }

    public static Matcher<ParamOwner> matchClientUserId(ParamOwner owner) {
        return allOf(
                hasProperty("key", equalTo(owner.getKey())),
                hasProperty("clientUserId", equalTo(owner.getClientUserId()))
        );
    }

    public static Matcher<ParamOwner> matchOwnerUpdate(ParamOwner owner) {
        return allOf(
                hasProperty("key", equalTo(owner.getKey())),
                hasProperty("paramQuantity", equalTo(owner.getParamQuantity())),
                hasProperty("clientUserId", equalTo(owner.getClientUserId()))
        );
    }

    private static Matcher<ParamOwnerKey> matchParamOwnerKey(ParamOwnerKey key) {
        return allOf(
                hasProperty("counterId", equalTo(key.getCounterId())),
                hasProperty("userId", equalTo(key.getUserId()))
        );
    }

    public static Matcher<List<UserParamLBCHRow>> matchLbRowsDelete(List<UserParamUpdate> updates) {
        return allOf(matchLbRowsContent(updates),
                everyItem(hasProperty("deleted", equalTo(true))));
    }

    public static Matcher<List<UserParamLBCHRow>> matchLbRowsUpdate(List<UserParamUpdate> updates) {
        return allOf(matchLbRowsContent(updates),
                everyItem(hasProperty("deleted", equalTo(false))));
    }

    public static Matcher<List<UserParamLBCHRow>> matchNanoLbRowsUpdate(List<UserParamUpdate> updates) {
        var nanoUpdates = updates.stream()
                .filter(row -> !TestCountersProvider.isBig(row.getCounterId()))
                .toList();
        return allOf(matchNanoLBRowsContent(nanoUpdates),
                everyItem(hasProperty("deleted", equalTo(false))));
    }

    private static Matcher<List<UserParamLBCHRow>> matchLbRowsContent(List<UserParamUpdate> updates) {
        return allOf(hasSize(getParamsQuantity(updates)),
                everyItem(anyOf(updates.stream()
                        .map(UserParamUpdate::getParams)
                        .flatMap(Collection::stream)
                        .map(Matchers::matchLbRow)
                        .toArray(Matcher[]::new)
                )));
    }

    private static int getParamsQuantity(List<UserParamUpdate> updates) {
        return updates.stream().mapToInt(update -> update.getParams().size()).sum();
    }

    private static Matcher<List<UserParamLBCHRow>> matchNanoLBRowsContent(List<UserParamUpdate> updates) {
        return allOf(
                (Matcher<? super List<UserParamLBCHRow>>) hasSize(getParamsQuantity(updates)),
                everyItem(matchesSomeUpdate(updates)),
                everyItem(hasSmallCounter())
        );
    }

    @Nonnull
    private static Matcher<UserParamLBCHRow> matchesSomeUpdate(List<UserParamUpdate> updates) {
        return anyOf(updates.stream().map(UserParamUpdate::getParams).flatMap(Collection::stream).map(Matchers::matchLbRow).toArray(Matcher[]::new));
    }

    @Nonnull
    private static Matcher<UserParamLBCHRow> hasSmallCounter() {
        return hasProperty("counterId", not(is(in(TestCountersProvider.getBigCounters()))));
    }

    private static Matcher<UserParamLBCHRow> matchLbRow(Param param) {
        return allOf(
                hasProperty("counterId", equalTo(param.getOwnerKey().getCounterId())),
                hasProperty("userId", equalTo(param.getOwnerKey().getUserId())),
                hasProperty("keys", matchParamPath(param)),
                hasProperty("valueString", equalTo(param.getValueString())),
                hasProperty("valueDouble", closeTo(param.getValueDouble(), 0.1e-14))
        );
    }

    private static Matcher<Map<String, String>> matchParamPath(Param param) {
        List<String> keys = parseKeys(param);
        return allOf(
                hasEntry(equalTo("key0"), equalTo(keys.get(0))),
                hasEntry(equalTo("key1"), equalTo(keys.get(1))),
                hasEntry(equalTo("key2"), equalTo(keys.get(2))),
                hasEntry(equalTo("key3"), equalTo(keys.get(3))),
                hasEntry(equalTo("key4"), equalTo(keys.get(4))),
                hasEntry(equalTo("key5"), equalTo(keys.get(5))),
                hasEntry(equalTo("key6"), equalTo(keys.get(6))),
                hasEntry(equalTo("key7"), equalTo(keys.get(7))),
                hasEntry(equalTo("key8"), equalTo(keys.get(8))),
                hasEntry(equalTo("key9"), equalTo(keys.get(9)))
        );
    }

    public static Matcher<Iterable<? extends ParamOwner>> haveClientUserIdFromParams(Param param) {
        return everyItem(hasProperty("clientUserId", equalTo(param.getValueString())));
    }

    @Nonnull
    private static List<String> parseKeys(Param param) {
        List<String> keys = Arrays.stream(param.getPath().split("\\.")).collect(toList());
        keys.add(param.getValueString());
        while (keys.size() != 10) {
            keys.add("");
        }
        return keys;
    }

    private static List<ParamOwner> getOwnersFromUpdates(List<UserParamUpdate> updates) {
        return updates.stream()
                .collect(groupingBy(UserParamUpdate::getParamOwnerKey))
                .entrySet()
                .stream()
                .map(entry -> new ParamOwner(
                        entry.getKey(),
                        entry.getValue().stream()
                                .map(UserParamUpdate::getParamWrapper)
                                .map(ListParamWrapper::getClientUserId)
                                .filter(StringUtils::isNotEmpty)
                                .reduce((a, b) -> b)
                                .orElse(""),
                        entry.getValue().stream()
                                .mapToInt(update -> update.getParamWrapper().getParams().size())
                                .sum()))
                .toList();
    }

}
