package ru.yandex.metrika.restream.collector.processing;

import java.util.Collection;
import java.util.Map;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

import ru.yandex.metrika.dbclients.ydb.async.QueryExecutionContext;
import ru.yandex.metrika.restream.dao.UserSegmentProfilesDao;
import ru.yandex.metrika.restream.dto.UserSegmentProfile;
import ru.yandex.metrika.util.collections.F;

final class UserSegmentProfilesDaoStub implements UserSegmentProfilesDao {

    final ConcurrentHashMap<UserSegmentProfile.Key, UserSegmentProfile> state = new ConcurrentHashMap<>();

    @Override
    public CompletableFuture<Map<UserSegmentProfile.Key, UserSegmentProfile>> getProfiles(Collection<UserSegmentProfile.Key> keys, QueryExecutionContext executionContext) {
        return CompletableFuture.completedFuture(
                keys.stream().filter(state.keySet()::contains).collect(Collectors.toMap(F.id(), state::get))
        );

    }

    @Override
    public CompletableFuture<Void> saveProfiles(Collection<UserSegmentProfile> profiles, QueryExecutionContext executionContext) {
        profiles.forEach(p -> state.put(p.asKey(), p));
        return CompletableFuture.completedFuture(null);
    }

    public void clear() {
        state.clear();
    }
}
