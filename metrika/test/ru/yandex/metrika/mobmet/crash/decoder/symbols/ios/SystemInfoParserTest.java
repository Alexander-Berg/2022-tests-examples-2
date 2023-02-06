package ru.yandex.metrika.mobmet.crash.decoder.symbols.ios;

import org.junit.Assert;
import org.junit.Test;

import ru.yandex.metrika.mobmet.crash.RawSymbolsProcessingException;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.ios.meta.IosSystemMetaProcessor;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.ios.meta.SystemInfo;

/**
 * Парсер проверяет только наиболее простые ошибки
 */
public class SystemInfoParserTest {

    @Test
    public void test() {
        SystemInfo info = IosSystemMetaProcessor.parse("12.3.1 (16F203)");
        Assert.assertEquals("12.3.1", info.getOsVersion());
        Assert.assertEquals("16F203", info.getOsBuild());
    }

    @Test
    public void test2() {
        SystemInfo info = IosSystemMetaProcessor.parse("5.0 (9A334)");
        Assert.assertEquals("5.0", info.getOsVersion());
        Assert.assertEquals("9A334", info.getOsBuild());
    }

    @Test
    public void testWithArch() {
        SystemInfo info = IosSystemMetaProcessor.parse("13.2 (17B84) arm64e");
        Assert.assertEquals("13.2", info.getOsVersion());
        Assert.assertEquals("17B84", info.getOsBuild());
    }

    @Test
    public void testWithArch2() {
        SystemInfo info = IosSystemMetaProcessor.parse("5.0 (9A334)_arm64");
        Assert.assertEquals("5.0", info.getOsVersion());
        Assert.assertEquals("9A334", info.getOsBuild());
    }

    @Test(expected = RawSymbolsProcessingException.class)
    public void testInvalid() {
        IosSystemMetaProcessor.parse(" (9A334)");
    }

    @Test(expected = RawSymbolsProcessingException.class)
    public void testInvalid2() {
        IosSystemMetaProcessor.parse("5.0");
    }

    @Test(expected = RawSymbolsProcessingException.class)
    public void testInvalid3() {
        IosSystemMetaProcessor.parse("5.0A (9A334)");
    }

    @Test(expected = RawSymbolsProcessingException.class)
    public void testInvalid4() {
        IosSystemMetaProcessor.parse("12.1.4 (9A3 34)");
    }
}
