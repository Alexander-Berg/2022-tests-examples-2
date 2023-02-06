package ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.cutter;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.StringReader;
import java.util.Collections;
import java.util.List;

import org.junit.Assert;
import org.junit.Test;

import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.model.DsymHeaderFields;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.model.DwarfCompileUnit;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.model.DwarfCompileUnitMeta;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.model.DwarfFileInfo;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.model.DwarfFunction;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.model.DwarfLineInfo;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.model.ObjectFile;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.model.ObjectFileHeader;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.model.Range;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.model.SymTabEntry;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.parser.SymbolsCutterParser;

import static ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.model.DwarfFunction.inlinedSubroutine;
import static ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.model.DwarfFunction.subprogram;
import static ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.model.SymbolTableType.Function;
import static ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.model.SymbolTableType.Unknown;
import static ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.parser.SymbolsCutterParser.SymbolsCutterFormat.APPLE_DSYM;
import static ru.yandex.metrika.util.io.IOUtils.resourceAsString;

public class SymbolsCutterParserTest {

    @Test
    public void test() throws IOException {
        String headersStr = resourceAsString(SymbolsCutterParserTest.class, "output.txt");
        BufferedReader reader = new BufferedReader(new StringReader(headersStr));

        List<ObjectFile> actual = new SymbolsCutterParser(APPLE_DSYM).parse(reader);

        List<SymTabEntry> expectedSymbolTable = List.of(
                new SymTabEntry(addr("100005aac"), Function, "-[MMSReportWithApiKeyController viewDidLoad]"),
                new SymTabEntry(addr("100006014"), Function, "-[MMSReportWithApiKeyController reloadData]"),
                new SymTabEntry(addr("100232188"), Unknown, "__block_descriptor_tmp.265"),
                new SymTabEntry(addr("1002fb898"), Unknown, "OBJC_METACLASS_$_YMMConnectionErrorsFactory"),
                new SymTabEntry(addr("10014687c"), Function, "ymm__request_parameters__init"),
                new SymTabEntry(addr("100146898"), Function, "ymm__request_parameters__get_packed_size"),
                new SymTabEntry(addr("100000000"), Function, "_mh_execute_header")
        );

        List<DwarfFileInfo> expectedFiles = List.of(
                new DwarfFileInfo(1, "/Users/teamcity/buildAgent/work/47913ed13ba5eb01/metrika/ios/appmetrica-sdk/YandexMobileMetricaSampleApp/YandexMobileMetricaSampleApp/MMSLocationManager.m"),
                new DwarfFileInfo(2, "/Applications/Xcode10.1.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/SDKs/iPhoneOS12.1.sdk/usr/include/dispatch/once.h")
        );

        List<DwarfLineInfo> expectedLines = List.of(
                new DwarfLineInfo(addr("1000074c4"), 25, 0L, 1, false),
                new DwarfLineInfo(addr("1000074d4"), 27, 12, 1, false),
                new DwarfLineInfo(addr("100007624"), 44, 15, 1, false),
                new DwarfLineInfo(addr("10000762c"), 44, 9, 1, false),
                new DwarfLineInfo(addr("100007644"), 45, 5, 1, true),
                new DwarfLineInfo(addr("1000076bc"), 83, 6, 2, false),
                new DwarfLineInfo(addr("1000076cc"), 86, 3, 2, false),
                new DwarfLineInfo(addr("100007d58"), 23, 17, 1, false),
                new DwarfLineInfo(addr("100007d9c"), 23, 17, 1, true)
        );

        List<DwarfFunction> expectedFunctions = List.of(
                subprogram("-[MMSLocationManager init]", List.of(range("1000074c4", "100007540"))),
                subprogram("-[MMSLocationManager addObserver:]", List.of(range("100007540", "1000075e0"))),
                subprogram("-[MMSLocationManager removeObserver:]", List.of(range("1000075e0", "100007680"))),
                subprogram("+[MMSLocationManager sharedManager]", List.of(range("100007680", "1000076f4"))),
                inlinedSubroutine("dispatch_once", List.of(range("1000076bc", "1000076cc"), range("1000076e0", "1000076f4")), 1, 1, 53, 0),
                subprogram("_35+[MMSLocationManager sharedManager]_block_invoke", List.of(range("1000076f4", "100007730")))
        );

        ObjectFileHeader expectedHeader = new ObjectFileHeader("E8D657B5-89CC-3948-A8E4-1FFA48C5479E", "arm64",
                addr("100000000"), new DsymHeaderFields("feedfacf", Integer.parseUnsignedInt("100000c", 16), Integer.parseUnsignedInt("0", 16), "a"));

        DwarfCompileUnit expectedCompileUnit = new DwarfCompileUnit(
                new DwarfCompileUnitMeta(
                        "/Users/teamcity/buildAgent/work/47913ed13ba5eb01/metrika/ios/appmetrica-sdk/YandexMobileMetricaSampleApp/YandexMobileMetricaSampleApp/MMSLocationManager.m",
                        List.of(range("1000074c4", "100007d9c"))),
                expectedFunctions,
                expectedLines,
                expectedFiles);

        ObjectFile expectedFile = new ObjectFile(
                expectedHeader,
                List.of(expectedCompileUnit),
                expectedSymbolTable,
                Collections.emptyList(), Collections.emptyList());

        Assert.assertEquals(List.of(expectedFile), actual);
    }

    private static Range range(String start, String end) {
        return new Range(addr(start), addr(end));
    }

    public static Long addr(String address) {
        return Long.parseUnsignedLong(address, 16);
    }
}
