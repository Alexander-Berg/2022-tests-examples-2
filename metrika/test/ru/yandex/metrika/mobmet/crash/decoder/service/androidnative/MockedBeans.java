package ru.yandex.metrika.mobmet.crash.decoder.service.androidnative;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

import org.mockito.Mockito;

import ru.yandex.metrika.mobmet.crash.decoder.service.ios.decoder.InternalModelDecoder;
import ru.yandex.metrika.mobmet.crash.decoder.service.ios.decoder.YDBImageDecoder;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.functions.Demangler;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.functions.FunctionLinesBuilder;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.functions.FunctionTableBuilder;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.functions.FunctionsYDBService;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.functions.serialization.FilesSerializer;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.functions.serialization.InlinesSerializer;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.functions.serialization.LinesSerializer;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.functions.serialization.YDBFunctionSerializer;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.model.DwarfDebugData;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.model.ObjectFile;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.parser.DwarfProcessor;
import ru.yandex.metrika.mobmet.crash.ios.FunctionsYDBDaoImpl;
import ru.yandex.metrika.mobmet.crash.ios.SerializedYDBFunction;
import ru.yandex.metrika.mobmet.crash.symbols.DebugSymbolsMeta;
import ru.yandex.metrika.mobmet.crash.symbols.DebugSymbolsMetaDao;
import ru.yandex.metrika.mobmet.crash.symbols.DebugSymbolsSourceType;
import ru.yandex.metrika.mobmet.crash.symbols.DebugSymbolsStatus;
import ru.yandex.metrika.mobmet.crash.symbols.SymbolsYdbTableType;
import ru.yandex.metrika.util.collections.F;

import static java.util.Collections.emptyMap;

class MockedBeans {

    public static InternalModelDecoder mockInternalModelDecoder(int appid, List<ObjectFile> symbols) throws Exception {
        List<DwarfDebugData> debugDataList = convertToDebugData(symbols);
        FunctionsYDBService functionsYdbService = mockFunctionsYDBService(debugDataList);
        DebugSymbolsMetaDao debugSymbolsMetaDao = mockDebugSymbolsMetaDao(appid, debugDataList);
        YDBImageDecoder ydbImageDecoder = new YDBImageDecoder(functionsYdbService);
        InternalModelDecoder internalModelDecoder = new InternalModelDecoder(
                ydbImageDecoder,
                debugSymbolsMetaDao
        );
        internalModelDecoder.init();
        return internalModelDecoder;
    }

    private static DebugSymbolsMetaDao mockDebugSymbolsMetaDao(int appId, List<DwarfDebugData> debugDataList) {
        DebugSymbolsMetaDao debugSymbolsMetaDao = Mockito.mock(DebugSymbolsMetaDao.class);
        Mockito.when(debugSymbolsMetaDao.getAppsMetadataForSymbolication(Mockito.anyMap()))
                .thenAnswer(invocation -> F.map(debugDataList, debugData -> new DebugSymbolsMeta(
                        0,
                        appId,
                        debugData.getInfo().getUuid(),
                        debugData.getInfo().getArch(),
                        DebugSymbolsStatus.ACTIVE,
                        0,
                        "",
                        debugData.getInfo().getSlide(),
                        DebugSymbolsSourceType.DWARF.getPriority(),
                        SymbolsYdbTableType.COMPRESSED
                )));
        return debugSymbolsMetaDao;
    }

    private static FunctionsYDBService mockFunctionsYDBService(List<DwarfDebugData> debugDataList) {
        List<SerializedYDBFunction> allFunctions = new ArrayList<>();

        FunctionsYDBService functionsYdbService = new FunctionsYDBService(
                mockFunctionsYDBDao(allFunctions),
                new YDBFunctionSerializer(
                        new FilesSerializer(),
                        new InlinesSerializer(),
                        new LinesSerializer()
                ));

        for (var debugData : debugDataList) {
            List<SerializedYDBFunction> serialized = functionsYdbService.serializeFunctions(debugData);
            allFunctions.addAll(serialized);
        }

        return functionsYdbService;
    }

    private static FunctionsYDBDaoImpl mockFunctionsYDBDao(List<SerializedYDBFunction> allFunctions) {
        FunctionsYDBDaoImpl functionsYdbDao = Mockito.mock(FunctionsYDBDaoImpl.class);
        Mockito.when(functionsYdbDao.findFunctions(Mockito.anyObject(), Mockito.anyListOf(Long.class)))
                .thenAnswer(invocation -> {
                    List<Long> addresses = invocation.getArgument(1, List.class);
                    List<SerializedYDBFunction> result = new ArrayList<>();
                    // Имитируем работу запроса в YDB
                    for (Long address : addresses) {
                        allFunctions.stream()
                                .sorted(Comparator.comparing(SerializedYDBFunction::getEnd))
                                .filter(f -> f.getEnd() > address)
                                .limit(1)
                                .forEach(result::add);
                    }
                    return result;
                });
        return functionsYdbDao;
    }

    private static Demangler mockDemangler() throws Exception {
        Demangler demangler = Mockito.mock(Demangler.class);
        Mockito.when(demangler.isMangled(Mockito.anyString())).thenReturn(false);
        Mockito.when(demangler.demangle(Mockito.anyListOf(String.class))).thenReturn(emptyMap());
        return demangler;
    }

    private static List<DwarfDebugData> convertToDebugData(List<ObjectFile> symbols) throws Exception {
        DwarfProcessor dwarfProcessor = new DwarfProcessor(
                null,
                new FunctionTableBuilder(mockDemangler()),
                new FunctionLinesBuilder()
        );
        return dwarfProcessor.convertToDwarfDebugData(symbols);
    }

}
