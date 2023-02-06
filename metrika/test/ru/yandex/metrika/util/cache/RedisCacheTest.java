package ru.yandex.metrika.util.cache;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;
import java.util.TreeMap;

import com.fasterxml.jackson.core.JsonProcessingException;
import io.lettuce.core.KeyValue;
import io.lettuce.core.RedisCommandTimeoutException;
import io.lettuce.core.api.sync.RedisCommands;
import io.lettuce.core.cluster.pubsub.api.sync.RedisClusterPubSubCommands;
import junit.framework.TestCase;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.mockito.Mock;
import org.mockito.Mockito;
import org.mockito.runners.MockitoJUnitRunner;

@RunWith(MockitoJUnitRunner.class)
public class RedisCacheTest extends TestCase {

    private Integer bufferSize = 30;
    private String prefix = "test";
    private long ttl = 30;

    @Mock
    private RedisCommands commands;

    private RedisConnectionMock<String, String> connection;
    private RedisConnectorMock connector;
    private CacheBuilder builder;
    private RedisCache<Integer, ArrayList<Integer>> cache;
    private CacheLoader<Integer, ArrayList<Integer>> cacheLoader;

    private class TestCacheLoader extends CacheLoader<Integer, ArrayList<Integer>> {
        protected TestCacheLoader() {
            super(prefix);
        }

        @Override
        public ArrayList<Integer> castDeserialization(Iterable<?> data) {
            return super.castDeserialization(data);
        }

        @Override
        public ArrayList<Integer> load(Integer key) {
            return factorialValues(key);
        }

        @Override
        public Map<Integer, ArrayList<Integer>> loadAll(Iterable<Integer> keys) {
            Map<Integer, ArrayList<Integer>> result = new HashMap<>();
            keys.forEach(key -> result.put(key, load(key)));
            return result;
        }

        private ArrayList<Integer> factorialValues(int factorial) {
            ArrayList<Integer> result = new ArrayList<>();

            int value = 1;
            for (int i = 1; i <= factorial; i++) {
                result.add(value);
                value = value * i;
            }
            result.add(value);

            return result;

        }
    }

    private class TestWithErrorCacheLoader extends TestCacheLoader{
        @Override
        public ArrayList<Integer> castDeserialization(Iterable<?> data) {
            ArrayList<Integer> result = new ArrayList<>();
            // Make error without adding "throws Throwable"
            result.get(0);
            return result;
        }
    }

    @After
    public void tearDown() {
        commands = null;
        connector = null;
        connection = null;
        cacheLoader = null;
        builder = null;
        cache = null;
    }

    @Before
    public void setUp() throws Exception {
        commands = Mockito.mock(RedisClusterPubSubCommands.class);
        connection = new RedisConnectionMock<String, String>(commands);
        connector = new RedisConnectorMock(connection, true);
        builder = new CacheBuilder(connector)
                .withTtl(ttl)
                .withExpireStrategy(ExpireStrategy.AFTER_READ);
        builder.setBufferSize(bufferSize);
        cacheLoader = new TestCacheLoader();
        cache = (RedisCache<Integer, ArrayList<Integer>>) builder.create(cacheLoader);

    }

    @Test
    public void getWithDeserializationFail(){
        cache = (RedisCache<Integer, ArrayList<Integer>>) builder.create(new TestWithErrorCacheLoader());

        Integer key = 3;
        ArrayList<Integer> result = cacheLoader.load(key);
        String keyStr = String.format("metrika:%s:%d", prefix, key);

        Mockito.when(commands.get(keyStr)).thenReturn("[1,1,2,6]");
        assertEquals(cache.get(key), result);
    }

    @Test
    public void getDisconected() {
        Integer key = 3;
        ArrayList<Integer> result = cacheLoader.load(key);
        connector.setConnected(false);
        assertEquals(cache.get(3), result);
        Mockito.verify(commands, Mockito.times(0)).get("metrika:test:3");

    }

    @Test
    public void get() {
        Integer key = 3;
        ArrayList<Integer> result = cacheLoader.load(key);
        String keyStr = String.format("metrika:%s:%d", prefix, key);

        Mockito.when(commands.get(keyStr)).thenReturn("[1,1,2,6]");
        assertEquals(cache.get(key), result);
        Mockito.verify(commands, Mockito.times(1)).get(keyStr);
        Mockito.verify(commands, Mockito.times(1)).expire(keyStr, ttl);
        Mockito.verify(commands, Mockito.times(0)).setex(keyStr, ttl, result);

    }

    @Test
    public void getNotInCache() throws JsonProcessingException {
        Integer key = 3;
        ArrayList<Integer> result = cacheLoader.load(key);
        String resultStr = cacheLoader.serialize(result);
        String keyStr = String.format("metrika:%s:%d", prefix, key);

        Mockito.when(commands.get(keyStr)).thenReturn(null);
        assertEquals(cache.get(key), result);
        Mockito.verify(commands, Mockito.times(1)).setex(keyStr, ttl, resultStr);

    }

    @Test
    public void getWithTimeout() throws JsonProcessingException {
        Integer key = 3;
        ArrayList<Integer> result = cacheLoader.load(key);
        String resultStr = cacheLoader.serialize(result);
        String keyStr = String.format("metrika:%s:%d", prefix, key);

        Mockito.when(commands.get(keyStr)).thenThrow(new RedisCommandTimeoutException());
        assertEquals(cache.get(key), result);
        // After errors fetch from Loader and put new value.
        Mockito.verify(commands, Mockito.times(1)).setex(keyStr, ttl, resultStr);
    }

    @Test
    public void getWithSingleTimeout() throws JsonProcessingException {
        Integer key = 3;
        ArrayList<Integer> result = cacheLoader.load(key);
        String resultStr = cacheLoader.serialize(result);
        String keyStr = String.format("metrika:%s:%d", prefix, key);

        Mockito.when(commands.get(keyStr)).thenThrow(new RedisCommandTimeoutException()).thenReturn("[1,1,2,6]");
        assertEquals(cache.get(key), result);
        // After first error, successfuly Retries, and not put fetched value.
        Mockito.verify(commands, Mockito.times(0)).setex(keyStr, ttl, resultStr);
    }

    @Test
    public void getAll() throws JsonProcessingException {
        ArrayList<Integer> income = new ArrayList<>();
        ArrayList<String> incomeKeys = new ArrayList<>();
        Map<Integer, ArrayList<Integer>> result = new HashMap<>();
        ArrayList<Map<String, String>> putPairs = new ArrayList<>();
        ArrayList<KeyValue<String, String>> requestResult  = new ArrayList<>();
        TreeMap<String, String> pairBlock = new TreeMap<>();
        putPairs.add(pairBlock);
        for (int i = 0; i < bufferSize * 1.5; i++) {
            income.add(i);
            String keyStr = String.format("metrika:%s:%d", prefix, i);
            ArrayList<Integer> value = cacheLoader.load(i);
            String valueStr = cacheLoader.serialize(value);
            incomeKeys.add(keyStr);
            result.put(i, value);
            if(i % 2 == 0){
                requestResult.add(KeyValue.fromNullable(keyStr, valueStr));
            } else {
                requestResult.add(KeyValue.fromNullable(keyStr, null));
                pairBlock.put(keyStr, valueStr);
            }
            if (incomeKeys.size() >= bufferSize){
                String[] arr = new String[incomeKeys.size()];
                incomeKeys.toArray(arr);
                Mockito
                        .when(commands.mget(arr))
                        .thenThrow(new RedisCommandTimeoutException())
                        .thenReturn(requestResult);
                incomeKeys.clear();
                requestResult = new ArrayList<>();
                pairBlock = new TreeMap<>();
                putPairs.add(pairBlock);
            }
        }
        String[] arr = new String[incomeKeys.size()];
        incomeKeys.toArray(arr);
        Mockito.when(commands.mget(arr)).thenReturn(requestResult);
        assertEquals(cache.getAll(income), result);
        putPairs.forEach(block -> Mockito.verify(commands, Mockito.times(1)).mset(block));
    }

    @Test
    public void getAllDisconected() {
        ArrayList<Integer> income = new ArrayList<>();
        HashMap<Integer, ArrayList<Integer>> result = new HashMap<>();
        connector.setConnected(false);
        for (int i = 0; i < bufferSize / 2; i++) {
            income.add(i);
            result.put(i, cacheLoader.load(i));
        }
        assertEquals(cache.getAll(income), result);
        Mockito.verify(commands, Mockito.times(0)).mget(income);
    }

    @Test
    public void getAllTimeout() {
        ArrayList<Integer> income = new ArrayList<>();
        ArrayList<String> dbKeys = new ArrayList<>();
        HashMap<Integer, ArrayList<Integer>> result = new HashMap<>();
        for (int i = 0; i < bufferSize / 2; i++) {
            income.add(i);
            result.put(i, cacheLoader.load(i));
            dbKeys.add(String.format("metrika:%s:%d", prefix, i));
        };

        String[] arr = new String[dbKeys.size()];
        dbKeys.toArray(arr);
        Mockito.when(commands.mget(arr)).thenThrow(new RedisCommandTimeoutException());
        dbKeys.forEach(key -> Mockito.when(commands.expire(key, ttl)).thenThrow(new RedisCommandTimeoutException()));
        assertEquals(cache.getAll(income), result);

    }

    @Test
    public void put() throws JsonProcessingException {
        Integer key = 3;
        ArrayList<Integer> value = cacheLoader.load(key);
        String result = cacheLoader.serialize(value);
        String keyStr = String.format("metrika:%s:%d", prefix, 3);

        Mockito.when(commands.setex(
                keyStr,
                ttl,
                result)
        ).thenThrow(new RedisCommandTimeoutException()).thenReturn(null);
        cache.put(key, value);
        Mockito.verify(commands, Mockito.times(2)).setex(keyStr, ttl, result);

    }

    @Test
    public void putAll() throws JsonProcessingException {
        Map<Integer, ArrayList<Integer>> incomeMap = new TreeMap<>();
        Map<String, String> resultMap = new TreeMap<>();
        for (int i = 0; i < bufferSize / 2; i++) {
            Integer key = i + 3;
            ArrayList<Integer> value = cacheLoader.load(key);
            incomeMap.put(key, value);
            String dbKey = String.format("metrika:%s:%d", prefix, key);
            String dbValue = cacheLoader.serialize(value);
            resultMap.put(dbKey, dbValue);
        }

        Mockito.when(commands.mset(resultMap)).thenThrow(new RedisCommandTimeoutException()).thenReturn(null);
        cache.putAll(incomeMap);
        Mockito.verify(commands, Mockito.times(2)).mset(resultMap);

        resultMap.forEach((resKey, resVal) -> {
            Mockito.verify(commands, Mockito.times(1)).expire(resKey, ttl);
        });
    }

    @Test
    public void invalidate() {
        String key = String.format("metrika:%s:%d", prefix, 0);
        Mockito.when(commands.del(key)).thenThrow(new RedisCommandTimeoutException()).thenReturn(null);
        cache.invalidate(0);
        Mockito.verify(commands, Mockito.times(2)).del(key);
    }

    @Test
    public void invalidateAll() {
        ArrayList<Integer> items = new ArrayList<>();
        ArrayList<String> keys = new ArrayList<>();
        for (int i = 0; i < bufferSize / 2; i++) {
            items.add(i);
            keys.add(String.format("metrika:%s:%d", prefix, i));

        }
        String[] arr = new String[keys.size()];
        keys.toArray(arr);

        Mockito.when(commands.del(arr)).thenThrow(new RedisCommandTimeoutException()).thenReturn(null);
        cache.invalidateAll(items);
        Mockito.verify(commands, Mockito.times(2)).del(arr);
    }

    @Test
    public void invalidateAllBigCount() {
        ArrayList<Integer> items = new ArrayList<>();
        ArrayList<ArrayList<String>> keys = new ArrayList<>();
        ArrayList<String> workKeys = new ArrayList<>();
        keys.add(workKeys);

        for (int i = 0; i < 1000; i++) {
            items.add(i);
            workKeys.add(String.format("metrika:%s:%d", prefix, i));
            if (workKeys.size() >= bufferSize) {
                workKeys = new ArrayList<>();
                keys.add(workKeys);
            }

        }
        cache.invalidateAll(items);
        keys.forEach(keyBlock -> {
            String[] arr = new String[keyBlock.size()];
            keyBlock.toArray(arr);
            Mockito.verify(commands).del(arr);
        });
    }

    @Test
    public void invalidateDisconected() {
        connector.setConnected(false);
        cache.invalidate(0);
        Mockito.verify(commands, Mockito.times(0)).del("metrika:test:0");

    }
}
