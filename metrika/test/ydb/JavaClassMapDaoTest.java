package ru.yandex.metrika.mobmet.crash.decoder.test.ydb;

import java.util.List;
import java.util.Map;
import java.util.Optional;

import com.google.common.collect.ImmutableMap;
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
import ru.yandex.metrika.mobmet.crash.deobfuscation.mapping.ClassNameKey;
import ru.yandex.metrika.mobmet.crash.deobfuscation.mapping.JavaClassMapYDBDao;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;
import static ru.yandex.metrika.mobmet.crash.symbols.SymbolsYdbTableType.COMPRESSED;

public class JavaClassMapDaoTest {

    private static YdbSessionManager sessionManager;
    private static JavaClassMapYDBDao proguardClassMapYDBDao;

    private long mappingFile = RandomUtils.nextLong();
    private String tableName = COMPRESSED.getProguardClassMapTable();

    private String originClass1 = "OriginКласс1";
    private String obfuscatedClass1 = "o1";

    private String originClass2 = "OriginКласс2";
    private String obfuscatedClass2 = "o2";

    private String originClass3 = "OriginКласс3";
    private String obfuscatedClass3 = "o3";

    private Map<ClassNameKey, String> mappings = ImmutableMap.of(
            new ClassNameKey(mappingFile, tableName, obfuscatedClass1), originClass1,
            new ClassNameKey(mappingFile, tableName, obfuscatedClass2), originClass2,
            new ClassNameKey(mappingFile, tableName, obfuscatedClass3), originClass3
    );

    @BeforeClass
    public static void setUpClass() {
        MediumTestsLogSetup.setup();
        YdbTestUtils.createCrashTables();
        sessionManager = new YdbSessionManager(YdbTestUtils.getTestProperties());
        proguardClassMapYDBDao = new JavaClassMapYDBDao(new YdbTemplate(sessionManager));
    }

    @Before
    public void setUp() {
        proguardClassMapYDBDao.save(COMPRESSED.getProguardClassMapTable(), mappings);
    }

    @Test
    public void get() {
        Optional<String> actual = proguardClassMapYDBDao.get(
                new ClassNameKey(mappingFile, tableName, obfuscatedClass1));

        assertTrue(actual.isPresent());
        assertEquals(originClass1, actual.get());
    }

    @Test
    public void getAll() {
        Map<ClassNameKey, String> actualClasses = proguardClassMapYDBDao.getAll(List.of(
                new ClassNameKey(mappingFile, tableName, obfuscatedClass1),
                new ClassNameKey(mappingFile, tableName, obfuscatedClass2)
        ));

        assertEquals(2, actualClasses.size());
        assertEquals(originClass1, actualClasses.get(new ClassNameKey(mappingFile, tableName, obfuscatedClass1)));
        assertEquals(originClass2, actualClasses.get(new ClassNameKey(mappingFile, tableName, obfuscatedClass2)));
    }

    @Test
    public void delete() {
        ClassNameKey key = new ClassNameKey(mappingFile, tableName, obfuscatedClass3);
        proguardClassMapYDBDao.delete(tableName, List.of(key));
        Optional<String> actual = proguardClassMapYDBDao.get(key);

        assertTrue(actual.isEmpty());
    }

    @After
    public void tearDown() {
        proguardClassMapYDBDao.delete(tableName, List.of(
                new ClassNameKey(mappingFile, tableName, obfuscatedClass1)
        ));
        proguardClassMapYDBDao.delete(tableName, List.of(
                new ClassNameKey(mappingFile, tableName, obfuscatedClass2)
        ));
        proguardClassMapYDBDao.delete(tableName, List.of(
                new ClassNameKey(mappingFile, tableName, obfuscatedClass3)
        ));
    }

    @AfterClass
    public static void tearDownClass() {
        sessionManager.close();
    }
}
