package ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf;

import java.io.BufferedInputStream;
import java.io.FileInputStream;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.stream.Collectors;

import org.junit.Assert;
import org.junit.Ignore;
import org.junit.Test;
import org.slf4j.LoggerFactory;

import ru.yandex.metrika.dbclients.ydb.YdbClientProperties;
import ru.yandex.metrika.dbclients.ydb.YdbTemplate;
import ru.yandex.metrika.dbclients.ydb.async.YdbSessionManager;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.exec.DwarfProcessExecuter;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.functions.Demangler;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.functions.FunctionLinesBuilder;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.functions.FunctionTableBuilder;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.functions.FunctionsYDBService;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.functions.model.FunctionLine;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.functions.model.FunctionName;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.functions.serialization.FilesSerializer;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.functions.serialization.InlinesSerializer;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.functions.serialization.LinesSerializer;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.functions.serialization.YDBFunctionSerializer;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.model.DwarfDebugData;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.model.ObjectFile;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.model.SymTabEntry;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.parser.DwarfProcessor;
import ru.yandex.metrika.mobmet.crash.ios.FunctionsYDBDaoImpl;
import ru.yandex.metrika.mobmet.crash.symbols.SymbolsYdbTableType;

import static java.lang.String.format;
import static ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.cutter.SymbolsCutterParserTest.addr;
import static ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.model.SymbolTableType.Function;
import static ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.model.SymbolTableType.Object;
import static ru.yandex.metrika.util.app.XmlPropertyConfigurer.getTextFromVault;

public class DwarfProcessorTest {

    @Test
    public void testCompleteSymbolTableBuild() {
        List<SymTabEntry> objdumpTable = List.of(
                new SymTabEntry(addr("906c"), Function, "-[MMSReportWithApiKeyController viewDidLoad]"),
                new SymTabEntry(addr("95a4"), Function, "__accept"),
                new SymTabEntry(addr("aae0"), Function, "+[MMSLocationManager sharedManager]"),
                new SymTabEntry(addr("a8e7"), Function, "__destroy_helper_block_"),
                new SymTabEntry(addr("95a4"), Function, "accept"),
                new SymTabEntry(addr("a8f0"), Object, "CLSHexMap")
        );

        List<SymTabEntry> functionsStarts = List.of(
                new SymTabEntry(addr("95a4"), Function, null),
                new SymTabEntry(addr("aae0"), Function, null),
                new SymTabEntry(addr("95b0"), Function, null),
                new SymTabEntry(addr("95a4"), Function, null)
        );

        List<SymTabEntry> actual = DwarfProcessor.buildCompleteSymbolTable(
                new ObjectFile(null, null, objdumpTable, null, functionsStarts));

        List<SymTabEntry> expected = List.of(
                new SymTabEntry(addr("906c"), Function, "-[MMSReportWithApiKeyController viewDidLoad]"),
                new SymTabEntry(addr("95a4"), Function, "__accept"),
                new SymTabEntry(addr("95a4"), Function, "accept"),
                new SymTabEntry(addr("95b0"), Function, null),
                new SymTabEntry(addr("a8e7"), Function, "__destroy_helper_block_"),
                new SymTabEntry(addr("a8f0"), Object, "CLSHexMap"),
                new SymTabEntry(addr("aae0"), Function, "+[MMSLocationManager sharedManager]"));

        Assert.assertEquals(expected, actual);
    }

    @Ignore
    @Test
    public void testFull() throws Exception {

        YdbSessionManager sessionManager = new YdbSessionManager(new YdbClientProperties()
                .setEndpoint("ydb-ru-prestable.yandex.net:2135")
                .setDatabase("/ru-prestable/metricmob/test/crashes")
                .setYdbToken(getTextFromVault("sec-01cw6tk4ymzvcdavxyd6wxv0z9/robot-metrika-test-ydb-token")));
        YdbTemplate ydbTemplate = new YdbTemplate(sessionManager);

        initLogger();
        org.slf4j.Logger log = LoggerFactory.getLogger(DwarfProcessor.class);

        log.info("Test started");

        DwarfProcessExecuter processExecuter = new DwarfProcessExecuter();
        processExecuter.init();
        Demangler demangler = new Demangler(processExecuter);
        demangler.setItaniumDemanglerPath("/opt/llvm/bin/llvm-cxxfilt");
        demangler.setSwiftDemanglerPath("/opt/swift/usr/bin/swift-demangle");
        FunctionTableBuilder tableBuilder = new FunctionTableBuilder(demangler);
        FunctionLinesBuilder linesBuilder = new FunctionLinesBuilder();
        DwarfProcessor processor = new DwarfProcessor(processExecuter, tableBuilder, linesBuilder);
        processor.setSymbolsCutterPath("/home/dancingelf/src/arc/arcadia/metrika/java/tools/symbols-cutter/symbols-cutter");
        processor.init();
        //String file = "/home/dancingelf/syms/Translate";
        //String file = "/home/dancingelf/Downloads/12.3.1 (16F203)/Symbols/System/Library/Frameworks/Contacts.framework/Contacts";
        String file = "/home/dancingelf/Downloads/test/Music_true/bdb26bbb-966d-360e-9a50-acf2d547ac21.dSYM/Contents/Resources/DWARF/Maple";
        //String file = "/home/dancingelf/Downloads/test2/browser_ios.19.9.3.97.(armv7_d23197d5).(arm64_0e1dd791).app+dSYM/browser_ios.dSYM/Contents/Resources/DWARF/browser_ios";
        //String file = "/home/dancingelf/Downloads/system/CoreLocation";
        //String file = "/home/dancingelf/Downloads/system/disk/12.4.1 (16G102)/Symbols/usr/lib/dyld";
        //String file = "/home/dancingelf/for_medium_tests/libxpc.dylib_7.1.2(11D257)";
        //String file = "/home/dancingelf/Downloads/Telegram Desktop/YandexMobileMetricaCrashes";

        List<DwarfDebugData> result;
        try (FileInputStream fis = new FileInputStream(file);
             BufferedInputStream bis = new BufferedInputStream(fis)) {
            result = processor.process(bis);
        }

        DwarfDebugData data = result.get(0);

        log.info("Parsing finished");
        printStat(data);

        log.info("Stat printing finished");

        FunctionsYDBDaoImpl functionsYDBDao = new FunctionsYDBDaoImpl(ydbTemplate, "16_f", SymbolsYdbTableType.COMPRESSED);

        YDBFunctionSerializer serializer = new YDBFunctionSerializer(new FilesSerializer(), new InlinesSerializer(), new LinesSerializer());

        FunctionsYDBService functionsService = new FunctionsYDBService(functionsYDBDao, serializer);

        //functionsService.save(10L, data);

        log.info("Test finished");

        Assert.assertEquals(1, result.size());
    }

    private static void initLogger() {
    }

    private static void printStat(DwarfDebugData data) {
        List<Long> starts = data.getFunctions().stream().filter(f -> f.getCallDepth() == 0).map(FunctionName::getStart).sorted().collect(Collectors.toList());

//        data.getFunctions().stream().filter(f -> f.getStart() == 16387744).forEach(f -> {
//            System.out.println(f);
//            System.out.println(Long.toUnsignedString(f.getStart(), 16));
//        });

        long functionStartCount = data.getFunctions().stream().map(FunctionName::getStart).distinct().count();
        long functionParentStartCount = data.getFunctions().stream().filter(f -> f.getCallDepth() == 0).map(FunctionName::getStart).distinct().count();
        long parentsCount = data.getFunctions().stream().filter(f -> f.getCallDepth() == 0).distinct().count();
        long inlinedCount = data.getFunctions().stream().filter(f -> f.getCallDepth() > 0).count();


        long maxDepth = data.getFunctions().stream().map(FunctionName::getCallDepth).max(Comparator.naturalOrder()).get();

        long maxInlinedCount = 0;
        long tmpMaxInlinedCount = 0;
        for (FunctionName f : data.getFunctions()) {
            if (f.getCallDepth() == 0) {
                if (tmpMaxInlinedCount > maxInlinedCount) {
                    maxInlinedCount = tmpMaxInlinedCount;
                }
                tmpMaxInlinedCount = 0;
            } else {
                tmpMaxInlinedCount++;
            }
        }

        Map<Long, String> fileNamesMap = new HashMap<>();
        data.getFilesMap().forEach((key, value) -> fileNamesMap.put(value, key));

        int sizeInBytes = data.getFunctions().stream().filter(f -> f.getName() != null).map(f -> f.getName().length()).mapToInt(i -> i).sum();

        int linesSizeInBytes = data.getLines().stream()
                .map(FunctionLine::getFileId)
                .filter(Objects::nonNull)
                .map(f -> fileNamesMap.get(f).length())
                .mapToInt(i -> i).sum();
        int uniqSizeInBytes = data.getLines().stream()
                .map(FunctionLine::getFileId)
                .sorted()
                .distinct()
                .map(id -> fileNamesMap.get(id).length()).mapToInt(i -> i).sum();
        long filesCount = data.getLines().stream().map(FunctionLine::getFileId).distinct().count();

        long callFilesInBytes = data.getFunctions().stream()
                .filter(f -> f.getCallFileId() != null)
                .mapToInt(f -> fileNamesMap.get(f.getCallFileId()).length())
                .sum();
        long uniqCallFilesInBytes = data.getFunctions().stream()
                .filter(f -> f.getCallFileId() != null)
                .map(FunctionName::getCallFileId)
                .distinct()
                .mapToInt(id -> fileNamesMap.get(id).length())
                .sum();

        System.out.println(format("Function compile units count: %s", data.getUnits().size()));
        System.out.println(format("Function count: %s", data.getFunctions().size()));
        System.out.println(format("Function lines count: %s", data.getLines().size()));

        System.out.println(format("Starts count: %s", functionStartCount));
        System.out.println(format("Parent count: %s. Parents starts count: %s", parentsCount, functionParentStartCount));
        System.out.println(format("Inlined count: %s", inlinedCount));

        System.out.println(format("Max depth: %s", maxDepth));
        System.out.println(format("Max inlined functions in top functions: %s", maxInlinedCount));
        System.out.println(format("Names total size: %s", toMb(sizeInBytes)));
        System.out.println(format("Call files total size: %s", toMb(callFilesInBytes)));
        System.out.println(format("Call files uniq total size: %s", toMb(uniqCallFilesInBytes)));

        System.out.println(format("Uniq files count: %s", filesCount));
        System.out.println(format("Lines file name total size: %s", toMb(linesSizeInBytes)));
        System.out.println(format("Uniq file name in lines total size: %s", toMb(uniqSizeInBytes)));
    }

    private static double toMb(long size) {
        return size / 1024.0 / 1024;
    }
}
