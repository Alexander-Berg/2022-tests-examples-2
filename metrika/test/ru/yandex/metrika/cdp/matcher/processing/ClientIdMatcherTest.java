package ru.yandex.metrika.cdp.matcher.processing;

import java.time.Instant;
import java.util.Collection;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.CompletableFuture;

import gnu.trove.decorator.TLongSetDecorator;
import gnu.trove.map.TLongObjectMap;
import gnu.trove.map.hash.TLongObjectHashMap;
import gnu.trove.set.TLongSet;
import gnu.trove.set.hash.TLongHashSet;
import org.apache.logging.log4j.Level;
import org.junit.Before;
import org.junit.Ignore;
import org.junit.Test;

import ru.yandex.metrika.cdp.dto.core.ClientKey;
import ru.yandex.metrika.cdp.processing.dao.ClientIdMatchingDao;
import ru.yandex.metrika.cdp.processing.dto.matching.ClientIdKey;
import ru.yandex.metrika.cdp.processing.dto.matching.MetrikaClientIdAdd;
import ru.yandex.metrika.cdp.processing.ydb.ClientIdMatchingDaoYdb;
import ru.yandex.metrika.dbclients.ydb.YdbClientProperties;
import ru.yandex.metrika.dbclients.ydb.YdbTemplate;
import ru.yandex.metrika.dbclients.ydb.async.QueryExecutionContext;
import ru.yandex.metrika.dbclients.ydb.async.YdbSessionManager;
import ru.yandex.metrika.dbclients.ydb.async.YdbTransactionManagerStub;
import ru.yandex.metrika.lb.write.LogbrokerWriter;
import ru.yandex.metrika.lb.write.LogbrokerWriterStub;
import ru.yandex.metrika.util.app.XmlPropertyConfigurer;
import ru.yandex.metrika.util.log.Log4jSetup;

import static java.time.temporal.ChronoUnit.DAYS;
import static org.hamcrest.core.IsCollectionContaining.hasItems;
import static org.hamcrest.core.IsNot.not;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertThat;
import static org.junit.Assert.assertTrue;
import static ru.yandex.metrika.cdp.processing.dto.matching.CdpClientIdChange.add;
import static ru.yandex.metrika.cdp.processing.dto.matching.CdpClientIdChange.remove;

public class ClientIdMatcherTest {

    private static final int userIdType = 1;

    private static final int counterId1 = 1;
    private static final int counterId2 = 2;

    private static final long cdpUid1 = 1001L;
    private static final long cdpUid2 = 1002L;
    private static final long cdpUid3 = 1003L;
    private static final long cdpUid4 = 1004L;
    private static final long cdpUid5 = 1005L;
    private static final long cdpUid6 = 1006L;

    private static final long clientId1 = 2001L;
    private static final long clientId2 = 2002L;
    private static final long clientId3 = 2003L;
    private static final long clientId4 = 2004L;
    private static final long clientId5 = 2005L;
    private static final long clientId6 = 2006L;

    private static final long userId1 = 3001L;
    private static final long userId2 = 3002L;
    private static final long userId3 = 3003L;
    private static final long userId4 = 3004L;
    private static final long userId5 = 3005L;
    private static final long userId6 = 3006L;


    private StorageStub storageStub;
    private LogbrokerWriterStub<ClientKey> downstreamStub;
    private ClientIdMatcher clientIdMatcher;

    @Before
    public void setUp() {
        storageStub = new StorageStub();
        downstreamStub = new LogbrokerWriterStub<>();
        clientIdMatcher = new ClientIdMatcher(new YdbTransactionManagerStub(), storageStub, downstreamStub);
    }

    @Test
    public void basicCdpTest() {
        //setup
        storageStub.addClientIdUserId(new ClientIdKey(counterId1, clientId1), userId1);
        storageStub.assertConsistent();

        // process changes
        clientIdMatcher.processCdp(List.of(
                add(clientId1, counterId1, cdpUid1)
        )).join();

        // should be consistent
        storageStub.assertConsistent();

        // should have userIds
        var clientKey = new ClientKey(cdpUid1, counterId1);
        storageStub.assertClientHasUserIds(clientKey, userId1);

        // should be clientKey in downstream
        downstreamStub.assertHaveExactlyOneMessage(clientKey);
    }

    @Test
    public void basicCdpTest2() {
        //setup
        storageStub.addClientIdUserId(new ClientIdKey(counterId1, clientId1), userId1);
        storageStub.addClientIdUserId(new ClientIdKey(counterId1, clientId1), userId2);
        storageStub.addClientIdUserId(new ClientIdKey(counterId1, clientId2), userId3);
        storageStub.assertConsistent();

        // process changes
        clientIdMatcher.processCdp(List.of(
                add(clientId1, counterId1, cdpUid1),
                add(clientId2, counterId1, cdpUid1)
        )).join();

        // should be consistent
        storageStub.assertConsistent();

        // should have userIds
        var clientKey = new ClientKey(cdpUid1, counterId1);
        storageStub.assertClientHasUserIds(clientKey, userId1, userId2, userId3);

        // should be clientKey in downstream
        downstreamStub.assertHaveExactlyOneMessage(clientKey);
    }

    @Test
    public void complexCdpTest() {
        //setup
        var clientKey = new ClientKey(cdpUid1, counterId1);
        storageStub.addClientClientId(clientKey, clientId1);
        storageStub.addClientClientId(clientKey, clientId2);

        storageStub.addClientIdUserId(new ClientIdKey(counterId1, clientId1), userId1);
        storageStub.addClientIdUserId(new ClientIdKey(counterId1, clientId1), userId2);
        storageStub.addClientIdUserId(new ClientIdKey(counterId1, clientId2), userId2);
        storageStub.addClientIdUserId(new ClientIdKey(counterId1, clientId2), userId3);

        storageStub.addClientUserId(clientKey, userId1);
        storageStub.addClientUserId(clientKey, userId2);
        storageStub.addClientUserId(clientKey, userId3);
        storageStub.assertConsistent();

        // process changes
        clientIdMatcher.processCdp(List.of(
                remove(clientId2, counterId1, cdpUid1)
        )).join();

        // should be consistent
        storageStub.assertConsistent();

        // should have userIds
        storageStub.assertClientHasUserIds(clientKey, userId1, userId2);
        storageStub.assertClientNotHasUserIds(clientKey, userId3);

        // should be clientKey in downstream
        downstreamStub.assertHaveExactlyOneMessage(clientKey);
    }

    @Test
    public void multipleClientsCdpTest() {
        //setup
        storageStub.addClientIdUserId(new ClientIdKey(counterId1, clientId1), userId1);
        storageStub.addClientIdUserId(new ClientIdKey(counterId1, clientId2), userId2);
        storageStub.assertConsistent();

        // process changes
        clientIdMatcher.processCdp(List.of(
                add(clientId1, counterId1, cdpUid1),
                add(clientId2, counterId1, cdpUid2)
        )).join();

        // should be consistent
        storageStub.assertConsistent();

        // should have userIds
        var clientKey1 = new ClientKey(cdpUid1, counterId1);
        var clientKey2 = new ClientKey(cdpUid2, counterId1);
        storageStub.assertClientHasUserIds(clientKey1, userId1);
        storageStub.assertClientHasUserIds(clientKey2, userId2);

        // should be both clientKeys in downstream
        downstreamStub.assertHaveOnlyMessages(clientKey1, clientKey2);
    }

    @Test
    public void basicMetrikaTest() {
        //setup
        var clientKey = new ClientKey(cdpUid1, counterId1);
        storageStub.addClientClientId(clientKey, clientId1);
        storageStub.assertConsistent();

        // process changes
        clientIdMatcher.processMetrika(List.of(
                new MetrikaClientIdAdd(clientId1, counterId1, userId1, userIdType)
        )).join();

        storageStub.assertConsistent();

        storageStub.assertClientHasUserIds(clientKey, userId1);

        // should be clientKey in downstream
        downstreamStub.assertHaveOnlyMessages(clientKey);
    }

    @Test
    public void basicMetrikaTest2() {
        //setup
        var clientKey = new ClientKey(cdpUid1, counterId1);
        storageStub.addClientClientId(clientKey, clientId1);
        storageStub.addClientClientId(clientKey, clientId2);
        storageStub.assertConsistent();

        // process changes
        clientIdMatcher.processMetrika(List.of(
                new MetrikaClientIdAdd(clientId1, counterId1, userId1, userIdType),
                new MetrikaClientIdAdd(clientId2, counterId1, userId2, userIdType)
        )).join();

        // should be consistent
        storageStub.assertConsistent();

        storageStub.assertClientHasUserIds(clientKey, userId1);
        storageStub.assertClientHasUserIds(clientKey, userId2);

        // should be clientKey in downstream
        downstreamStub.assertHaveOnlyMessages(clientKey);
    }

    @Test
    public void multiClientMetrikaTest() {
        //setup
        var clientKey1 = new ClientKey(cdpUid1, counterId1);
        var clientKey2 = new ClientKey(cdpUid2, counterId1);
        storageStub.addClientClientId(clientKey1, clientId1);
        storageStub.addClientClientId(clientKey2, clientId1);
        storageStub.assertConsistent();

        // process changes
        clientIdMatcher.processMetrika(List.of(
                new MetrikaClientIdAdd(clientId1, counterId1, userId1, userIdType)
        )).join();

        // should be consistent
        storageStub.assertConsistent();

        storageStub.assertClientHasUserIds(clientKey1, userId1);
        storageStub.assertClientHasUserIds(clientKey2, userId1);

        // should be both clientKeys in downstream
        downstreamStub.assertHaveOnlyMessages(clientKey1, clientKey2);
    }

    @Test
    public void simpleRepeatedClientIdsMetrikaTest() {
        var clientKey = new ClientKey(cdpUid1, counterId1);
        storageStub.addClientClientId(clientKey, clientId1);

        storageStub.addClientIdUserId(new ClientIdKey(counterId1, clientId1), userId1);

        storageStub.addClientUserId(clientKey, userId1);

        storageStub.assertConsistent();

        clientIdMatcher.processMetrika(List.of(new MetrikaClientIdAdd(clientId1, counterId1, userId1, userIdType))).join();

        storageStub.assertConsistent();

        downstreamStub.assertHaveNoMessages();
    }

    @Test
    public void complexRepeatedClientIdsMetrikaTest() {
        var clientKey1 = new ClientKey(cdpUid1, counterId1);
        var clientKey2 = new ClientKey(cdpUid2, counterId1);

        storageStub.addClientClientId(clientKey1, clientId1);
        storageStub.addClientClientId(clientKey2, clientId2);

        storageStub.addClientIdUserId(new ClientIdKey(counterId1, clientId1), userId1);

        storageStub.addClientUserId(clientKey1, userId1);

        storageStub.assertConsistent();

        clientIdMatcher.processMetrika(List.of(
                new MetrikaClientIdAdd(clientId1, counterId1, userId1, userIdType),
                new MetrikaClientIdAdd(clientId2, counterId1, userId2, userIdType)
        )).join();

        storageStub.assertConsistent();

        // no clientKey1, only clientKey2
        downstreamStub.assertHaveOnlyMessages(clientKey2);
    }

    @Test
    public void cdpAndMetrikaBasicTest() {
        storageStub.assertConsistent();

        // process changes
        clientIdMatcher.processCdp(List.of(
                add(clientId1, counterId1, cdpUid1)
        )).join();

        // should be consistent
        storageStub.assertConsistent();

        // should be 0 messages
        downstreamStub.assertHaveNoMessages();

        // process changes
        clientIdMatcher.processMetrika(List.of(
                new MetrikaClientIdAdd(clientId1, counterId1, userId1, userIdType)
        )).join();

        // should be consistent
        storageStub.assertConsistent();

        var clientKey = new ClientKey(cdpUid1, counterId1);
        storageStub.assertClientHasUserIds(clientKey, userId1);

        // should be clientKey in downstream
        downstreamStub.assertHaveExactlyOneMessage(clientKey);
    }

    @Test
    public void cdpAndMetrikaDifferentCountersTest() {
        var clientKey1 = new ClientKey(cdpUid1, counterId1);
        var clientKey2 = new ClientKey(cdpUid2, counterId2);

        // process changes
        clientIdMatcher.processCdp(List.of(
                add(clientId1, counterId1, cdpUid1),
                add(clientId2, counterId2, cdpUid2)
        )).join();

        // should be consistent
        storageStub.assertConsistent();

        // should be 0 messages
        downstreamStub.assertHaveNoMessages();

        // process changes
        clientIdMatcher.processMetrika(List.of(
                new MetrikaClientIdAdd(clientId1, counterId1, userId1, userIdType),
                new MetrikaClientIdAdd(clientId2, counterId2, userId2, userIdType)
        )).join();

        // should be consistent
        storageStub.assertConsistent();

        storageStub.assertClientHasUserIds(clientKey1, userId1);
        storageStub.assertClientHasUserIds(clientKey2, userId2);

        // should be clientKey in downstream
        downstreamStub.assertHaveOnlyMessages(clientKey1, clientKey2);
    }

    @Test
    public void cdpAndMetrikaWithTTLTest() {
        storageStub.assertConsistent();

        // process changes
        clientIdMatcher.processCdp(List.of(
                add(clientId1, counterId1, cdpUid1),
                add(clientId2, counterId1, cdpUid1),
                add(clientId3, counterId1, cdpUid1)
        )).join();

        storageStub.assertConsistent();

        // should be 0 messages
        downstreamStub.assertHaveNoMessages();

        clientIdMatcher.processMetrika(List.of(
                new MetrikaClientIdAdd(clientId1, counterId1, userId1, userIdType),
                new MetrikaClientIdAdd(clientId2, counterId1, userId2, userIdType),
                new MetrikaClientIdAdd(clientId2, counterId1, userId3, userIdType),
                new MetrikaClientIdAdd(clientId3, counterId1, userId2, userIdType),
                new MetrikaClientIdAdd(clientId3, counterId1, userId4, userIdType)
        ));

        storageStub.assertConsistent();

        var clientKey = new ClientKey(cdpUid1, counterId1);
        storageStub.assertClientHasUserIds(clientKey, userId1, userId2, userId3, userId4);

        // should be clientKey in downstream
        downstreamStub.assertHaveOnlyMessages(clientKey);
        // clear downstream
        downstreamStub.clear();

        // ttl be like
        var clientIdKey = new ClientIdKey(counterId1, clientId2);
        storageStub.removeClientIdUserId(clientIdKey, userId2);
        storageStub.removeClientIdUserId(clientIdKey, userId3);

        storageStub.assertWeakConsistent();

        clientIdMatcher.processMetrika(List.of(
                new MetrikaClientIdAdd(clientId4, counterId1, userId5, userIdType)
        ));

        storageStub.assertWeakConsistent();

        // should be 0 messages
        downstreamStub.assertHaveNoMessages();

        clientIdMatcher.processCdp(List.of(
                add(clientId4, counterId1, cdpUid1),
                remove(clientId3, counterId1, cdpUid1)
        ));

        storageStub.assertWeakConsistent();

        storageStub.assertClientHasUserIds(clientKey, userId1, userId3, userId5);
        // should be clientKey in downstream
        downstreamStub.assertHaveOnlyMessages(clientKey);
    }

    @Test
    @Ignore("Runs only localy")
    public void realTest() {

        Log4jSetup.basicArcadiaSetup(Level.INFO);
        var properties = new YdbClientProperties();
        properties.setDatabase("/ru-prestable/metrika/development/cdp");
        properties.setEndpoint("ydb-ru-prestable.yandex.net:2135");
        properties.setCallThreadCount(2);
        properties.setYdbToken(XmlPropertyConfigurer.getTextFromFile("~/.ydb/token"));

        var ydbSessionManager = new YdbSessionManager(properties);
        var ydbTemplate = new YdbTemplate(ydbSessionManager);
        Runtime.getRuntime().addShutdownHook(new Thread(ydbSessionManager::close));


        ydbTemplate.dropTable("/ru-prestable/metrika/development/cdp/matching/client_client_id").join().expect("Can not drop");
        ydbTemplate.dropTable("/ru-prestable/metrika/development/cdp/matching/client_id_client").join().expect("Can not drop");
        ydbTemplate.dropTable("/ru-prestable/metrika/development/cdp/matching/client_user_id").join().expect("Can not drop");
        ydbTemplate.dropTable("/ru-prestable/metrika/development/cdp/matching/client_id_user_id").join().expect("Can not drop");


        var clientIdMatchingDaoYdb = new ClientIdMatchingDaoYdb(ydbTemplate);
        clientIdMatchingDaoYdb.setTablePrefix("/ru-prestable/metrika/development/cdp/matching");
        clientIdMatchingDaoYdb.afterPropertiesSet();

        var clientIdMatcher = new ClientIdMatcher(ydbSessionManager, clientIdMatchingDaoYdb, LogbrokerWriter.devNull());

        // process changes
        clientIdMatcher.processCdp(List.of(
                add(clientId1, counterId1, cdpUid1),
                add(clientId2, counterId1, cdpUid1),
                add(clientId3, counterId1, cdpUid1)
        )).join();

        clientIdMatcher.processMetrika(List.of(
                new MetrikaClientIdAdd(clientId1, counterId1, userId1, userIdType, Instant.now().minus(1, DAYS)),
                new MetrikaClientIdAdd(clientId2, counterId1, userId2, userIdType, Instant.now().minus(10, DAYS)),
                new MetrikaClientIdAdd(clientId2, counterId1, userId3, userIdType, Instant.now().minus(10, DAYS)),
                new MetrikaClientIdAdd(clientId3, counterId1, userId2, userIdType, Instant.now().minus(1, DAYS)),
                new MetrikaClientIdAdd(clientId3, counterId1, userId4, userIdType, Instant.now().minus(1, DAYS))
        )).join();

        var clientKey = new ClientKey(cdpUid1, counterId1);
        var userIds = clientIdMatchingDaoYdb.getClientUserIdMapping(Set.of(clientKey), QueryExecutionContext.read()).join().get(clientKey);
        assertEquals(new TLongHashSet(Set.of(userId1, userId2, userId3, userId4)), userIds);

        var stats = clientIdMatchingDaoYdb.cleanUp(Instant.now().minus(5, DAYS));
        assertEquals(Map.of("/ru-prestable/metrika/development/cdp/matching/client_id_user_id", 2L), stats);

        clientIdMatcher.processMetrika(List.of(
                new MetrikaClientIdAdd(clientId4, counterId1, userId5, userIdType)
        )).join();

        clientIdMatcher.processCdp(List.of(
                add(clientId4, counterId1, cdpUid1),
                remove(clientId3, counterId1, cdpUid1)
        )).join();
        userIds = clientIdMatchingDaoYdb.getClientUserIdMapping(Set.of(clientKey), QueryExecutionContext.read()).join().get(clientKey);
        assertEquals(userIds, new TLongHashSet(Set.of(userId1, userId3, userId5)));
    }

    private static class StorageStub implements ClientIdMatchingDao {

        private final Map<ClientKey, TLongSet> clientKeyClientIdMap = new HashMap<>();
        private final Map<ClientIdKey, TLongSet> clientIdUserIdMap = new HashMap<>();
        private final Map<ClientKey, TLongSet> clientKeyUserIdMap = new HashMap<>();
        private final Map<ClientIdKey, TLongSet> clientIdKeyCdpUidMap = new HashMap<>();

        public void addClientClientId(ClientKey clientKey, long clientId) {
            clientKeyClientIdMap.computeIfAbsent(clientKey, k -> new TLongHashSet()).add(clientId);
            clientIdKeyCdpUidMap.computeIfAbsent(new ClientIdKey(clientKey.getCounterId(), clientId), k -> new TLongHashSet()).add(clientKey.getCdpUid());
        }

        public void addClientIdUserId(ClientIdKey clientIdKey, long userId) {
            clientIdUserIdMap.computeIfAbsent(clientIdKey, k -> new TLongHashSet()).add(userId);
        }

        public void removeClientIdUserId(ClientIdKey clientIdKey, long userId) {
            clientIdUserIdMap.computeIfAbsent(clientIdKey, k -> new TLongHashSet()).remove(userId);
        }

        public void addClientUserId(ClientKey clientKey, long userId) {
            clientKeyUserIdMap.computeIfAbsent(clientKey, k -> new TLongHashSet()).add(userId);
        }


        @Override
        public CompletableFuture<Map<ClientIdKey, TLongSet>> getClientIdUserIdMapping(Collection<ClientIdKey> clientIdKeys, QueryExecutionContext executionContext) {
            var result = new HashMap<ClientIdKey, TLongSet>();
            for (var clientIdKey : clientIdKeys) {
                var userIds = clientIdUserIdMap.get(clientIdKey);
                if (userIds == null || userIds.isEmpty()) {
                    continue;
                }
                result.put(clientIdKey, new TLongHashSet(userIds));
            }
            return CompletableFuture.completedFuture(result);
        }

        @Override
        public CompletableFuture<Map<ClientIdKey, TLongSet>> getClientIdClientMapping(Collection<ClientIdKey> clientIdKeys, QueryExecutionContext executionContext) {
            var result = new HashMap<ClientIdKey, TLongSet>();
            for (var clientIdKey : clientIdKeys) {
                var cdpUids = clientIdKeyCdpUidMap.get(clientIdKey);
                if (cdpUids == null || cdpUids.isEmpty()) {
                    continue;
                }
                result.put(clientIdKey, new TLongHashSet(cdpUids));
            }
            return CompletableFuture.completedFuture(result);
        }

        @Override
        public CompletableFuture<Map<ClientKey, TLongSet>> getClientClientIdMapping(Collection<ClientKey> clientKeys, QueryExecutionContext executionContext) {
            var result = new HashMap<ClientKey, TLongSet>();
            for (var clientKey : clientKeys) {
                var clientIds = clientKeyClientIdMap.get(clientKey);
                result.put(clientKey, clientIds);
            }
            return CompletableFuture.completedFuture(result);
        }

        @Override
        public CompletableFuture<Map<ClientKey, TLongSet>> getClientUserIdMapping(Collection<ClientKey> clientKeys, QueryExecutionContext executionContext) {
            var result = new HashMap<ClientKey, TLongSet>();
            for (var clientKey : clientKeys) {
                var userIds = clientKeyUserIdMap.get(clientKey);
                if (userIds == null || userIds.isEmpty()) {
                    continue;
                }
                result.put(clientKey, new TLongHashSet(userIds));
            }
            return CompletableFuture.completedFuture(result);
        }

        @Override
        public CompletableFuture<Map<ClientKey, TLongObjectMap<TLongSet>>> getChainedMapping(Collection<ClientKey> clientKeys, QueryExecutionContext executionContext) {
            var result = new HashMap<ClientKey, TLongObjectMap<TLongSet>>();
            for (var clientKey : clientKeys) {
                var clientIds = clientKeyClientIdMap.get(clientKey);
                var mappingClone = new TLongObjectHashMap<TLongSet>();
                result.put(clientKey, mappingClone);
                if (clientIds == null || clientIds.isEmpty()) {
                    continue;
                }
                for (long clientId : clientIds.toArray()) {
                    var localUserIds = clientIdUserIdMap.get(new ClientIdKey(clientKey.getCounterId(), clientId));
                    if (localUserIds != null && !localUserIds.isEmpty()) {
                        mappingClone.put(clientId, new TLongHashSet(localUserIds));
                    }
                }
            }
            return CompletableFuture.completedFuture(result);
        }

        @Override
        public CompletableFuture<Void> saveUserIdChanges(Map<ClientKey, TLongSet> add, Map<ClientKey, TLongSet> remove, QueryExecutionContext executionContext) {
            for (var clientKey : add.keySet()) {
                var userIds = clientKeyUserIdMap.get(clientKey);
                if (userIds == null) {
                    clientKeyUserIdMap.put(clientKey, new TLongHashSet(add.get(clientKey)));
                } else {
                    userIds.addAll(add.get(clientKey));
                }
            }
            for (var clientKey : remove.keySet()) {
                var userIds = clientKeyUserIdMap.get(clientKey);
                if (userIds != null) {
                    clientKeyUserIdMap.get(clientKey).removeAll(remove.get(clientKey));
                }
            }
            return CompletableFuture.completedFuture(null);
        }


        @Override
        public CompletableFuture<Void> saveCdpClientIdChanges(Map<ClientKey, TLongSet> added, Map<ClientKey, TLongSet> removed) {
            added.forEach(((clientKey, toAdd) -> clientKeyClientIdMap.computeIfAbsent(clientKey, k -> new TLongHashSet()).addAll(toAdd)));
            removed.forEach(((clientKey, toRemove) -> clientKeyClientIdMap.computeIfAbsent(clientKey, k -> new TLongHashSet()).removeAll(toRemove)));

            for (var entry : added.entrySet()) {
                var clientKey = entry.getKey();
                var clientIds = entry.getValue();
                for (long clientId : clientIds.toArray()) {
                    clientIdKeyCdpUidMap.computeIfAbsent(new ClientIdKey(clientKey.getCounterId(), clientId), k -> new TLongHashSet()).add(clientKey.getCdpUid());
                }
            }
            for (var entry : removed.entrySet()) {
                var clientKey = entry.getKey();
                var clientIds = entry.getValue();
                for (long clientId : clientIds.toArray()) {
                    clientIdKeyCdpUidMap.computeIfAbsent(new ClientIdKey(clientKey.getCounterId(), clientId), k -> new TLongHashSet()).remove(clientKey.getCdpUid());
                }
            }
            return CompletableFuture.completedFuture(null);
        }

        @Override
        public CompletableFuture<Void> saveMetrikaClientIdChanges(List<MetrikaClientIdAdd> added) {
            for (MetrikaClientIdAdd e : added) {
                addClientIdUserId(e.getClientIdKey(), e.userId());
            }
            return CompletableFuture.completedFuture(null);
        }

        @Override
        public Map<String, Long> cleanUp(Instant minTimestamp) {
            return Map.of();
        }

        private Map<ClientKey, TLongSet> getCdpUidUserIdTransitiveMapping () {
            var result = new HashMap<ClientKey, TLongSet>();
            for (var clientKey : clientKeyClientIdMap.keySet()) {
                var clientIds = clientKeyClientIdMap.get(clientKey);
                var userIds = new TLongHashSet();
                if (clientIds == null || clientIds.isEmpty()) {
                    continue;
                }
                for (long clientId : clientIds.toArray()) {
                    var localUserIds = clientIdUserIdMap.get(new ClientIdKey(clientKey.getCounterId(), clientId));
                    if (localUserIds != null && ! localUserIds.isEmpty()) {
                        userIds.addAll(localUserIds);
                    }
                }
                if(!userIds.isEmpty()) {
                    result.put(clientKey, userIds);
                }
            }
            return result;
        }

        public void assertConsistent() {
            assertConsistent(false);
        }

        public void assertWeakConsistent() {
            assertConsistent(true);
        }

        public void assertConsistent(boolean weak) {
            var transitiveMapping = getCdpUidUserIdTransitiveMapping();
            if (weak) {
                for (var entry : transitiveMapping.entrySet()) {
                    var clientKey = entry.getKey();
                    var userIds = entry.getValue();
                    for (var userId : userIds.toArray()) {
                        assertTrue(clientKeyUserIdMap.get(clientKey).contains(userId));
                    }
                }
            } else {
                // stronger check
                assertEquals(getCdpUidUserIdTransitiveMapping(), clientKeyUserIdMap);
            }

            for (var entry : clientKeyClientIdMap.entrySet()) {
                var clientKey = entry.getKey();
                var clientIds = entry.getValue();
                for (long clientId : clientIds.toArray()) {
                    var clientIdKey = new ClientIdKey(clientKey.getCounterId(), clientId);
                    assertTrue(clientIdKeyCdpUidMap.get(clientIdKey).contains(clientKey.getCdpUid()));
                }
            }

            for (var entry : clientIdKeyCdpUidMap.entrySet()) {
                var clientIdKey = entry.getKey();
                var cdpUids = entry.getValue();
                for (long cdpUid : cdpUids.toArray()) {
                    var clientKey = new ClientKey(cdpUid, clientIdKey.counterId());
                    assertTrue(clientKeyClientIdMap.get(clientKey).contains(clientIdKey.clientId()));
                }

            }
        }

        public void assertClientNotHasUserIds(ClientKey clientKey, Long... userIds) {
            var actualUserIds = getClientUserIdMapping(Set.of(clientKey), null).join().get(clientKey);
            assertThat(new TLongSetDecorator(actualUserIds), not(hasItems(userIds)));
        }

        public void assertClientHasUserIds(ClientKey clientKey, Long... userIds) {
            var actualUserIds = getClientUserIdMapping(Set.of(clientKey), null).join().get(clientKey);
            assertThat(new TLongSetDecorator(actualUserIds), hasItems(userIds));
        }
    }

}
