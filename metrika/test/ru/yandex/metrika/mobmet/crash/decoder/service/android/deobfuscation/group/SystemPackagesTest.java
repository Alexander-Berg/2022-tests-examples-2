package ru.yandex.metrika.mobmet.crash.decoder.service.android.deobfuscation.group;

import java.util.Collection;
import java.util.List;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import org.junit.runners.Parameterized.Parameters;

import static org.junit.Assert.assertEquals;

@RunWith(Parameterized.class)
public class SystemPackagesTest {

    private SystemPackages systemPackages;

    @Parameter
    public String pkg;

    @Parameter(1)
    public boolean expectedResult;

    @Parameters(name = "Class: {0}; isSystem: {1}")
    public static Collection<Object[]> params() {
        return List.of(
                // Просто проверяем, все системные пакеты
                param("android.Test", true),
                param("com.android.Test", true),
                param("dalvik.Test", true),
                param("java.Test", true),
                param("javax.Test", true),
                param("junit.Test", true),
                param("org.apache.http.Test", true),
                param("org.json.Test", true),
                param("org.w3c.Test", true),
                param("org.xml.Test", true),

                // Сложные случаи системных классов
                param("org.xml.test.Test", true),

                // Несистемные классы
                param("org.Test", false),
                param("javaa.Test", false),
                param("ru.yandex.Test", false),
                param("мой_пакет.Test", false)
        );
    }

    private static Object[] param(String className, boolean expectedResult) {
        return new Object[]{className, expectedResult};
    }

    @Before
    public void setUp() {
        systemPackages = new SystemPackages(List.of(
                "android",
                "com.android",
                "dalvik",
                "java",
                "javax",
                "junit",
                "org.apache.http",
                "org.json",
                "org.w3c",
                "org.xml"
        ));
    }

    @Test
    public void testIsSystem() {
        assertEquals(expectedResult, systemPackages.isSystem(pkg));
    }
}
