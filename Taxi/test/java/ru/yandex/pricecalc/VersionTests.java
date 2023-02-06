package ru.yandex.pricecalc;

import java.io.IOException;
import java.net.URL;
import java.util.jar.Manifest;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.JUnit4;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotEquals;

/**
 * Instrumented test, which will execute on an Android device.
 */
@RunWith(JUnit4.class)
public class VersionTests {
    @Test
    public void getVersionTest() throws IOException {
        ClassLoader cl = PriceCalc.class.getClassLoader();
        URL url = cl.getResource("META-INF/MANIFEST.MF");
        Manifest manifest = new Manifest(url.openStream());
        assertNotEquals("-1", Version.VERSION);
        assertEquals(manifest.getMainAttributes().getValue("Arcadia-Source-Last-Change"), Version.VERSION);
    }
}
