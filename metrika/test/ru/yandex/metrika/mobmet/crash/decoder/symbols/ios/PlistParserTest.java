package ru.yandex.metrika.mobmet.crash.decoder.symbols.ios;

import java.nio.file.Paths;

import org.junit.Assert;
import org.junit.Test;

import ru.yandex.metrika.mobmet.crash.decoder.symbols.ios.meta.plist.InfoPlistData;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.ios.meta.plist.PlistParser;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.ios.meta.plist.UuidPlistData;
import ru.yandex.metrika.util.io.IOUtils;

public class PlistParserTest {

    @Test
    public void testInfoPlist() {

        String infoPlist = IOUtils.resourceAsString(PlistParserTest.class, "Info.plist");

        PlistParser parser = new PlistParser();
        InfoPlistData actual = parser.parseInfoPlist(
                Paths.get("F42C1D75-0217-3386-A3AD-BA23D792E84D.dSYM/Contents/Info.plist"),
                infoPlist);

        InfoPlistData expected = new InfoPlistData(
                Paths.get("F42C1D75-0217-3386-A3AD-BA23D792E84D.dSYM/Contents/Info.plist"),
                "196",
                "1967");

        Assert.assertEquals(expected, actual);
    }

    @Test
    public void testUUIDPlist() {

        String infoPlist = IOUtils.resourceAsString(PlistParserTest.class, "F42C1D75-0217-3386-A3AD-BA23D792E84D.plist");

        PlistParser parser = new PlistParser();
        UuidPlistData actual = parser.parseUuidPlist(
                Paths.get("F42C1D75-0217-3386-A3AD-BA23D792E84D.dSYM/Contents/Resources/F42C1D75-0217-3386-A3AD-BA23D792E84D.plist"),
                infoPlist);

        UuidPlistData expected = new UuidPlistData(
                Paths.get("F42C1D75-0217-3386-A3AD-BA23D792E84D.dSYM/Contents/Resources/F42C1D75-0217-3386-A3AD-BA23D792E84D.plist"),
                "f42c1d7502173386a3adba23d792e84d",
                "290624b635653c58bb1fb6878ed2f7a9");

        Assert.assertEquals(expected, actual);
    }
}
