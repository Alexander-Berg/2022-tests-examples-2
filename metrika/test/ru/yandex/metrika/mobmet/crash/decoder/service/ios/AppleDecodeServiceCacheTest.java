package ru.yandex.metrika.mobmet.crash.decoder.service.ios;

import java.util.AbstractMap;
import java.util.Collections;
import java.util.List;
import java.util.Map;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import org.jetbrains.annotations.Nullable;
import org.junit.Assert;
import org.junit.Test;

import ru.yandex.metrika.mobmet.crash.decoder.ios.protocol.IOSCrashReport;
import ru.yandex.metrika.mobmet.crash.decoder.service.ios.decoder.InstructionKey;
import ru.yandex.metrika.mobmet.crash.decoder.service.ios.decoder.InternalModelDecoder;
import ru.yandex.metrika.mobmet.crash.decoder.service.ios.decoder.model.InstructionDecoded;
import ru.yandex.metrika.mobmet.crash.decoder.service.ios.group.CrashReasonInfoFactory;
import ru.yandex.metrika.mobmet.crash.decoder.service.ios.group.ErrorMessageTrimWordsDao;
import ru.yandex.metrika.mobmet.crash.decoder.service.ios.group.ErrorMessageTrimmer;
import ru.yandex.metrika.mobmet.crash.decoder.service.ios.group.NsExceptionNameTrimmer;
import ru.yandex.metrika.mobmet.crash.decoder.service.ios.proto.AppleSdkProtocolConverter;
import ru.yandex.metrika.mobmet.crash.decoder.service.library.DummyLibraryService;
import ru.yandex.metrika.mobmet.crash.decoder.service.library.LibraryResultFactory;
import ru.yandex.metrika.mobmet.crash.decoder.service.model.CrashParams;
import ru.yandex.metrika.mobmet.crash.decoder.service.model.ParseResult;
import ru.yandex.metrika.mobmet.crash.decoder.service.model.result.ProcessingResult;
import ru.yandex.metrika.mobmet.crash.symbols.DebugSymbolsMeta;
import ru.yandex.metrika.mobmet.crash.symbols.DebugSymbolsMetaDao;
import ru.yandex.metrika.mobmet.crash.symbols.DebugSymbolsSourceType;
import ru.yandex.metrika.mobmet.crash.symbols.DebugSymbolsStatus;
import ru.yandex.metrika.mobmet.crash.symbols.SymbolsYdbTableType;
import ru.yandex.metrika.segments.apps.bundles.AppEventType;
import ru.yandex.metrika.segments.apps.misc.crashes.ProcessingStatus;
import ru.yandex.metrika.segments.apps.type.OperatingSystem;

import static org.mockito.Matchers.anyMap;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;
import static ru.yandex.metrika.mobmet.crash.ios.AppleDSymMeta.SYSTEM_APP_ID;
import static ru.yandex.metrika.util.io.IOUtils.resourceAsString;

public class AppleDecodeServiceCacheTest {

    @Test
    public void decode() throws Exception {

        int applicationId = 10180;

        DebugSymbolsMetaDao metaDao = mock(DebugSymbolsMetaDao.class);
        when(metaDao.getAppsMetadataForSymbolication(anyMap()))
                .thenReturn(ImmutableList.of(
                        meta(applicationId, "715e8ded2eea3ebbad836d3b67258392", "arm64", 10L),
                        meta(SYSTEM_APP_ID, "6225b1cd39843071a64add8f31b09c36", "arm64", 12L),
                        meta(SYSTEM_APP_ID, "61d2e950add73139aea459b55997ea48", "arm64", 13L),
                        meta(SYSTEM_APP_ID, "e102701ef8803cd4a5d54f5f14433dbd", "arm64", 14L),
                        meta(SYSTEM_APP_ID, "6dd6981adef530b3b6062f29ade13bb2", "arm64", 15L),
                        meta(SYSTEM_APP_ID, "07c87e3874b73d128f0fa331d8894b97", "arm64", 16L),
                        meta(SYSTEM_APP_ID, "533c841ed6e9313d8adb02388744e2ef", "arm64", 17L),
                        meta(SYSTEM_APP_ID, "2eacef3cb1e5323eac1a2e0d743c81a5", "arm64", 18L),
                        meta(SYSTEM_APP_ID, "5011ec2511d73a56af501e8207d54962", "arm64", 19L),
                        meta(SYSTEM_APP_ID, "be6ef0203caa393986da6dd6737541d5", "arm64", 20L)
                ));

        InternalModelDecoder internalModelDecoder = new InternalModelDecoder(null, metaDao);
        internalModelDecoder.init();
        AppleParseService parseService = new AppleParseService(new AppleSdkProtocolConverter());
        ErrorMessageTrimWordsDao errorTrimDao = mock(ErrorMessageTrimWordsDao.class);
        when(errorTrimDao.getWords()).thenReturn(Collections.emptyList());
        CrashReasonInfoFactory crashReasonInfoFactory =
                new CrashReasonInfoFactory(new NsExceptionNameTrimmer(), new ErrorMessageTrimmer(errorTrimDao), new DummyLibraryService());
        LibraryResultFactory libraryResultFactory = new LibraryResultFactory();
        AppleDecodeService decodeService = new AppleDecodeService(internalModelDecoder, crashReasonInfoFactory, libraryResultFactory);

        Map<InstructionKey, List<InstructionDecoded>> cache = ImmutableMap.<InstructionKey, List<InstructionDecoded>>builder()
                .put(brief(10L, 13292204L, "std::__y1::__tree<std::__y1::__value_type<TString, std::__y1::pair<void const*, int> >, std::__y1::__map_value_compare<TString, std::__y1::__value_type<TString, std::__y1::pair<void const*, int> >, std::__y1::less<TString>, true>, std::__y1::allocator<std::__y1::__value_type<TString, std::__y1::pair<void const*, int> > > >::destroy(std::__y1::__tree_node<std::__y1::__value_type<TString, std::__y1::pair<void const*, int> >, void*>*)", 140L))
                .put(brief(10L, 13292104L, "std::__y1::__tree<std::__y1::__value_type<TString, std::__y1::pair<void const*, int> >, std::__y1::__map_value_compare<TString, std::__y1::__value_type<TString, std::__y1::pair<void const*, int> >, std::__y1::less<TString>, true>, std::__y1::allocator<std::__y1::__value_type<TString, std::__y1::pair<void const*, int> > > >::destroy(std::__y1::__tree_node<std::__y1::__value_type<TString, std::__y1::pair<void const*, int> >, void*>*)", 40L))
                .put(brief(10L, 13292116L, "std::__y1::__tree<std::__y1::__value_type<TString, std::__y1::pair<void const*, int> >, std::__y1::__map_value_compare<TString, std::__y1::__value_type<TString, std::__y1::pair<void const*, int> >, std::__y1::less<TString>, true>, std::__y1::allocator<std::__y1::__value_type<TString, std::__y1::pair<void const*, int> > > >::destroy(std::__y1::__tree_node<std::__y1::__value_type<TString, std::__y1::pair<void const*, int> >, void*>*)", 52L))
                .put(brief(10L, 13288416L, "google::protobuf::EncodedDescriptorDatabase::~EncodedDescriptorDatabase()", 120L))
                .put(brief(10L, 13288460L, "google::protobuf::EncodedDescriptorDatabase::~EncodedDescriptorDatabase()", 12L))
                .put(brief(10L, 13594672L, "google::protobuf::internal::LazyDescriptor::OnceInternal()", 348))
                .put(brief(10L, 13073168L, "google::protobuf::internal::ShutdownData::~ShutdownData()", 48))
                .put(brief(10L, 13072816L, "google::protobuf::ShutdownProtobufLibrary()", 96))
                .put(brief(10L, 13973668L, "NSystemInfo::GetPageSize()", 572))
                .put(full(10L, 456432L, "main", 60, 13L, 13L, "AppDelegate.swift"))
                .put(brief(12L, 4032L, "start", 4))
                .put(brief(13L, 404748L, "abort", 140))
                .put(brief(13L, 407808L, "__cxa_finalize_ranges", 400))
                .put(brief(13L, 53852L, "exit", 24))
                .put(brief(14, 140000L, "__pthread_kill", 8))
                .put(brief(14, 142712L, "__workq_kernreturn", 8))
                .put(brief(14, 3560L, "mach_msg_trap", 8))
                .put(brief(14, 3168L, "mach_msg", 72))
                .put(brief(15L, 52724L, "_szone_default_reader.34", 0))
                .put(brief(15L, 95636L, "free_list_checksum_botch.330", 36))
                .put(brief(15L, 17560L, "tiny_free_list_remove_ptr", 308))
                .put(brief(15L, 96324L, "tiny_free_no_lock", 680))
                .put(brief(15L, 97844L, "free_tiny", 252))
                .put(brief(16L, 12936L, "pthread_kill$VARIANT$mp", 376))
                .put(brief(16L, 3764L, "_pthread_wqthread", 928))
                .put(brief(16L, 8736L, "_pthread_body", 272))
                .put(brief(16L, 8464L, "_pthread_body", 0))
                .put(brief(17L, 973072L, "__CFRUNLOOP_IS_CALLING_OUT_TO_AN_OBSERVER_CALLBACK_FUNCTION__", 32))
                .put(brief(17L, 963128L, "__CFRunLoopDoObservers", 412))
                .put(brief(17L, 964740L, "__CFRunLoopRun", 1436))
                .put(brief(17L, 48552L, "CFRunLoopRunSpecific", 552))
                .put(brief(17L, 974400L, "__CFRunLoopServiceMachPort", 196))
                .put(brief(17L, 964872L, "__CFRunLoopRun", 1568))
                .put(brief(18L, 34420L, "-[NSRunLoop(NSRunLoop) runMode:beforeDate:]", 304))
                .put(brief(18L, 34076L, "-[NSRunLoop(NSRunLoop) runUntilDate:]", 148))
                .put(brief(18L, 1150716L, "__NSThread__start__", 1040))
                .put(brief(19L, 45088L, "GSEventRunModal", 100))
                .put(brief(20L, 3301120L, "-[UIApplication applicationWillTerminate]", 0L))
                .put(brief(20L, 6572228L, "__98-[__UICanvasLifecycleMonitor_Compatability deactivateEventsOnly:withContext:forceExit:completion:]_block_invoke.271", 336L))
                .put(brief(20L, 4384900L, "_runAfterCACommitDeferredBlocks", 296))
                .put(brief(20L, 4344152L, "_cleanUpAfterCAFlushAndRunDeferredBlocks", 384))
                .put(brief(20L, 3183900L, "_afterCACommitHandler", 132))
                .put(brief(20L, 3266392L, "UIApplicationMain", 236))
                .put(brief(20L, 10088L, "-[UIEventFetcher threadMain]", 136))
                .build();
        internalModelDecoder.getInstructionsCacheF().get().putAll(cache);

        String crash = resourceAsString(AppleDecodeServiceCacheTest.class, "fake_crash.json");
        IOSCrashReport crashReport = new ObjectMapper().readValue(crash, IOSCrashReport.class);
        ParseResult<IOSCrashReport> parseResult = parseService.parseIosEvent(applicationId, crashReport);
        Assert.assertFalse(parseResult.isParseError());

        CrashParams crashParams = new CrashParams(applicationId, 0L, 0L,
                OperatingSystem.IOS,
                "1.0", 1,
                AppEventType.EVENT_PROTOBUF_CRASH,
                null,
                0L, 0L, 0L, (byte) 0);

        ProcessingResult result = decodeService.decodeCrash(crashParams, parseResult, false, false).get(0);
        Assert.assertNotNull(result);
        Assert.assertEquals(result.getStatus(), ProcessingStatus.DECODE_SUCCESS);
    }

    private static Map.Entry<InstructionKey, List<InstructionDecoded>> brief(long metaId, long offsetFromImage,
                                                                             String symbolName, long offsetFromSymbol) {
        return full(metaId, offsetFromImage, symbolName, offsetFromSymbol, null, null, null);
    }

    private static Map.Entry<InstructionKey, List<InstructionDecoded>> full(long metaId, long offsetFromImage,
                                                                            String symbolName, long offsetFromSymbol,
                                                                            @Nullable Long lineOfCode, @Nullable Long columnOfCode,
                                                                            @Nullable String sourceFileName) {
        InstructionDecoded decoded = new InstructionDecoded(offsetFromImage, symbolName, offsetFromSymbol,
                lineOfCode, columnOfCode, sourceFileName, false);
        return new AbstractMap.SimpleEntry<>(new InstructionKey(metaId, decoded.getOffsetFromImage()), List.of(decoded));
    }

    private static DebugSymbolsMeta meta(int applicationId, String uuid, String arch, long id) {
        return new DebugSymbolsMeta(id, applicationId, uuid, arch, DebugSymbolsStatus.ACTIVE, 0L, "", 0,
                DebugSymbolsSourceType.DWARF.getPriority(), SymbolsYdbTableType.UNCOMPRESSED);
    }
}
