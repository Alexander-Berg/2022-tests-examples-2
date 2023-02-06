package ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.cutter;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.StringReader;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;

import org.junit.Assert;
import org.junit.Test;

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

import static ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.model.DwarfFunction.subprogram;
import static ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.model.SymbolTableType.Function;
import static ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.parser.SymbolsCutterParser.SymbolsCutterFormat.ANDROID_NATIVE;
import static ru.yandex.metrika.util.io.IOUtils.resourceAsString;

public class SymbolsCutterParserAndroidNativeTest {

    @Test
    public void test() throws IOException {
        String symbols = resourceAsString(SymbolsCutterParserAndroidNativeTest.class, "android_native.ysym");
        // Убираем красивые отступы, поскольку SymbolsCutterParser пока не научили в .strip()
        String symbolsWithoutIndentation = Arrays.stream(symbols.split("\n"))
                .map(String::strip)
                .collect(Collectors.joining("\n"));
        BufferedReader reader = new BufferedReader(new StringReader(symbolsWithoutIndentation));

        List<ObjectFile> actual = new SymbolsCutterParser(ANDROID_NATIVE).parse(reader);

        ObjectFileHeader expectedHeader = new ObjectFileHeader(
                "f1866f4e67674651e7a38bc8240e1912",
                "aarch64",
                0,
                null);

        List<DwarfFileInfo> expectedFiles = List.of(
                new DwarfFileInfo(1, "/Users/alex98/Yandex/Projects/test-crashlytics/app/src/main/cpp/string-lib.cpp"),
                new DwarfFileInfo(2, "/Users/alex98/Library/Android/sdk/ndk-bundle/toolchains/llvm/prebuilt/darwin-x86_64/sysroot/usr/include/jni.h")
        );

        List<DwarfLineInfo> expectedLines = List.of(
                new DwarfLineInfo(addr("9dc"), 15, 0, 1, false),
                new DwarfLineInfo(addr("9e8"), 16, 5, 1, false),
                new DwarfLineInfo(addr("9fc"), 17, 24, 1, false),
                new DwarfLineInfo(addr("a04"), 17, 10, 1, false),
                new DwarfLineInfo(addr("a18"), 16, 5, 1, false),
                new DwarfLineInfo(addr("a30"), 17, 5, 1, false)
        );

        List<DwarfFunction> expectedFunctions = List.of(
                subprogram("Java_com_example_testcrashlytics_MainActivity_addHexPrefixJNI", List.of(range("9dc", "a74"))),
                subprogram("_ZN7_JNIEnv8ThrowNewEP7_jclassPKc", List.of(range("a74", "ac4")))
        );

        DwarfCompileUnit expectedCompileUnit = new DwarfCompileUnit(
                new DwarfCompileUnitMeta(
                        "/Users/alex98/Yandex/Projects/test-crashlytics/app/src/main/cpp/string-lib.cpp",
                        List.of(range("9dc", "ac4"))),
                expectedFunctions,
                expectedLines,
                expectedFiles);

        List<SymTabEntry> expectedSymbolTable = List.of(
                new SymTabEntry(addr("9a0"), addr("c"), Function, "__on_dlclose"),
                new SymTabEntry(addr("9b0"), addr("4"), Function, "__on_dlclose_late"),
                new SymTabEntry(addr("9b4"), addr("c"), Function, "__atexit_handler_wrapper"),
                new SymTabEntry(addr("9c0"), addr("1c"), Function, "atexit"),
                new SymTabEntry(addr("9ac"), addr("4"), Function, "__emutls_unregister_key"),
                new SymTabEntry(addr("ca0"), addr("114"), Function, "_ZN7_JNIEnv16CallObjectMethodEP8_jobjectP10_jmethodIDz"),
                new SymTabEntry(addr("a74"), addr("50"), Function, "_ZN7_JNIEnv8ThrowNewEP7_jclassPKc")
        );

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
