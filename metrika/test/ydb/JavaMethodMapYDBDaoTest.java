package ru.yandex.metrika.mobmet.crash.decoder.test.ydb;

import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;

import org.apache.commons.lang3.RandomUtils;
import org.junit.After;
import org.junit.AfterClass;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;

import ru.yandex.metrika.common.test.medium.MediumTestsLogSetup;
import ru.yandex.metrika.dbclients.ydb.YdbTemplate;
import ru.yandex.metrika.dbclients.ydb.async.YdbSessionManager;
import ru.yandex.metrika.mobmet.crash.decoder.test.common.YdbTestUtils;
import ru.yandex.metrika.mobmet.crash.deobfuscation.fork.FrameRemapper.MethodInfo;
import ru.yandex.metrika.mobmet.crash.deobfuscation.mapping.JavaMethodMapYDBDao;
import ru.yandex.metrika.mobmet.crash.deobfuscation.mapping.MethodInfoKey;
import ru.yandex.metrika.mobmet.crash.deobfuscation.mapping.ProguardMethodInfoSerializer;
import ru.yandex.metrika.mobmet.crash.deobfuscation.mapping.ProguardMethodMapping;

import static java.util.Arrays.asList;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;
import static ru.yandex.metrika.mobmet.crash.symbols.SymbolsYdbTableType.COMPRESSED;

public class JavaMethodMapYDBDaoTest {

    private static YdbSessionManager sessionManager;
    private static JavaMethodMapYDBDao<ProguardMethodMapping> proguardClassMethodMapYDBDao;

    private long mappingFile = RandomUtils.nextLong();
    private String tableName = COMPRESSED.getProguardMembersMapTable();

    private String originClass1 = "OriginКласс1";

    private String obfuscatedMethod1 = "m1";
    private ProguardMethodMapping methodInfo11 = new ProguardMethodMapping(
            new MethodInfo(1, 2, "OriginalClass11", 3, 4, "OriginalRType", "myМетод1", null));
    private ProguardMethodMapping methodInfo12 = new ProguardMethodMapping(
            new MethodInfo(1, 2, "OriginalClass12", 3, 4, "OriginalRType", "myМетод12", null));
    private LinkedHashSet<ProguardMethodMapping> methodInfos = new LinkedHashSet<>(asList(methodInfo11, methodInfo12));

    private String obfuscatedMethod2 = "m2";
    private ProguardMethodMapping methodInfo2 = new ProguardMethodMapping(
            new MethodInfo(11, 12, "OriginalClass2", 13, 14, "OriginalType", "myМетод2", null));

    private String originClass3 = "OriginКласс3";
    private String obfuscatedMethod3 = "m3";
    private ProguardMethodMapping methodInfo3 = new ProguardMethodMapping(
            new MethodInfo(21, 22, "OriginalClass3", 23, 24, "OriginalType", "myМетод3", null));

    private Map<MethodInfoKey, Set<ProguardMethodMapping>> mappings = Map.of(
            new MethodInfoKey(mappingFile, tableName, originClass1, obfuscatedMethod1), methodInfos,
            new MethodInfoKey(mappingFile, tableName, originClass1, obfuscatedMethod2), Set.of(methodInfo2),
            new MethodInfoKey(mappingFile, tableName, originClass3, obfuscatedMethod3), Set.of(methodInfo3)
    );

    @BeforeClass
    public static void setUpClass() {
        MediumTestsLogSetup.setup();
        YdbTestUtils.createCrashTables();
        sessionManager = new YdbSessionManager(YdbTestUtils.getTestProperties());
        proguardClassMethodMapYDBDao = new JavaMethodMapYDBDao<>(
                new YdbTemplate(sessionManager), new ProguardMethodInfoSerializer());
    }

    @Before
    public void setUp() {
        proguardClassMethodMapYDBDao.save(tableName, mappings);
    }

    @Test
    public void get() {
        Optional<Set<ProguardMethodMapping>> actual = proguardClassMethodMapYDBDao.get
                (new MethodInfoKey(mappingFile, tableName, originClass1, obfuscatedMethod1));

        assertTrue(actual.isPresent());
        assertEquals(methodInfos, actual.get());
    }

    @Test
    public void getAll() {
        Map<MethodInfoKey, Set<ProguardMethodMapping>> actualMappings = proguardClassMethodMapYDBDao.getAll(List.of(
                new MethodInfoKey(mappingFile, tableName, originClass1, obfuscatedMethod1),
                new MethodInfoKey(mappingFile, tableName, originClass1, obfuscatedMethod2)
        ));

        assertEquals(2, actualMappings.size());
        assertEquals(methodInfos,
                actualMappings.get(new MethodInfoKey(mappingFile, tableName, originClass1, obfuscatedMethod1)));
        assertEquals(Set.of(methodInfo2),
                actualMappings.get(new MethodInfoKey(mappingFile, tableName, originClass1, obfuscatedMethod2)));
    }

    @Test
    public void delete() {
        MethodInfoKey key = new MethodInfoKey(mappingFile, tableName, originClass3, obfuscatedMethod3);
        proguardClassMethodMapYDBDao.delete(tableName, List.of(key));
        Optional<Set<ProguardMethodMapping>> actual = proguardClassMethodMapYDBDao.get(key);

        assertTrue(actual.isEmpty());
    }

    @After
    public void tearDown() {
        proguardClassMethodMapYDBDao.delete(tableName, List.of(
                new MethodInfoKey(mappingFile, tableName, originClass1, obfuscatedMethod1)
        ));
        proguardClassMethodMapYDBDao.delete(tableName, List.of(
                new MethodInfoKey(mappingFile, tableName, originClass1, obfuscatedMethod2)
        ));
        proguardClassMethodMapYDBDao.delete(tableName, List.of(
                new MethodInfoKey(mappingFile, tableName, originClass3, obfuscatedMethod3)
        ));
    }

    @AfterClass
    public static void tearDownClass() {
        sessionManager.close();
    }
}
