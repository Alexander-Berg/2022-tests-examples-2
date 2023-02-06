#include <robot/library/plutonium/offroad_struct_wad/offroad_struct_wad_global_lumps_processor.h>
#include <robot/library/plutonium/offroad_struct_wad/offroad_struct_wad_yt_writer.h>
#include <robot/library/plutonium/protos/doc_wad_lumps.pb.h>
#include <robot/library/plutonium/protos/global_wad_lump.pb.h>
#include <robot/library/plutonium/wad/utility.h>
#include <robot/library/plutonium/wad/yt_wad_lumps_writer.h>

#include <robot/jupiter/library/rtdoc/file/test_local_client.h>

#include <kernel/doom/offroad_struct_wad/offroad_struct_wad_io.h>
#include <kernel/doom/offroad_struct_wad/serializers.h>
#include <kernel/doom/standard_models/standard_models.h>

#include <library/cpp/logger/global/global.h>
#include <library/cpp/testing/unittest/registar.h>

#include <util/stream/str.h>
#include <util/string/printf.h>
#include <util/string/subst.h>

using namespace NDoom;
using namespace std::string_view_literals;

template <size_t dataSize>
class TFakeDataSerializer: public TStringBufSerializer {
public:
    using TStringBufSerializer::Deserialize;
    using TStringBufSerializer::Serialize;

    enum {
        DataSize = dataSize
    };
};

using TNewSerializer = TFakeDataSerializer<3>;
using TOldSerializer = TFakeDataSerializer<2>;

template <ECompressionType compressionType>
class TIndex {
public:
    using Io = TOffroadStructWadIo<OmniUrlType, TStringBuf, TNewSerializer, FixedSizeStructType, compressionType, DefaultOmniUrlIoModel>;
    using OldIo = TOffroadStructWadIo<OmniUrlType, TStringBuf, TOldSerializer, FixedSizeStructType, compressionType, DefaultOmniUrlIoModel>;
};

Y_UNIT_TEST_SUITE(TPlutoniumFixedStructVersioning) {
    enum {
        DocLumpsTableIndex = 0,
        GlobalLumpsTableIndex = 1
    };

    constexpr TStringBuf TestShard = "-";
    const TString DocLumpsTable = "doc_lumps";
    const TString GlobalLumpsTable = "global_lumps";

    static constexpr ui32 DocCount = 3;

    template <typename Io, bool OldStructSize>
    static ui32 WriteTestData(NYT::TTableWriter<NProtoBuf::Message>* output, const ui32 beginDocId, const ui32 endDocId) {
        NPlutonium::TYtWadLumpsWriter LumpsWriter;
        NPlutonium::TOffroadStructWadYtWriter<Io> StructWriter;

        LumpsWriter.Reset(output, DocLumpsTableIndex, GlobalLumpsTableIndex, TString(TestShard));
        StructWriter.Reset(&LumpsWriter);

        TStringBuf data;
        if constexpr (OldStructSize) {
            data = TStringBuf("ab");
        } else {
            data = TStringBuf("abc");
        }

        for (ui32 docId = beginDocId; docId < endDocId; ++docId) {
            StructWriter.Write(docId, data);
        };

        StructWriter.Finish();
        LumpsWriter.Finish();
        return endDocId;
    }

    static ui32 FormatExpectedResult(IOutputStream* output, TStringBuf value, const ui32 beginDocId, const ui32 endDocId) {
        ui32 docId = beginDocId;
        for (; docId < endDocId; ++docId) {
            *output << docId << ":" << value << " ";
        }
        return docId;
    }

    template <typename TIo>
    static TString ReadActualWad(const TFsPath& wadPath) {
        TStringStream result;
        ui32 docId;

        THolder<IWad> wad = IWad::Open(wadPath);
        using TReader = typename TIo::TReader;
        TReader reader(wad.Get());

        while (reader.ReadDoc(&docId)) {
            TStringBuf hit;
            while (reader.ReadHit(&hit)) {
                result << docId << ":" << hit << " ";
            }
        }
        return result.Str();
    }

    template <ECompressionType CompressionType>
    void DoTest(bool hasOld, bool hasNew, bool mergeAsNew) {
        const TString compressionDisplayName = CompressionType == OffroadCompressionType ? "OffroadCompressionType" : "RawCompressionType";
        const TString testCaseDisplayName = Sprintf("DoTest<%s>(hasOld=%d, hasNew=%d, mergeAsNew=%d)", compressionDisplayName.c_str(), !!hasOld, !!hasNew, !!mergeAsNew);

        using TOldIo = typename TIndex<CompressionType>::OldIo;
        using TIo = typename TIndex<CompressionType>::Io;

        //
        // 1. Write data using NPlutonium::TYtWadLumpsWriter
        //
        NRtDoc::TTestLocalClient mockClient(TFsPath::Cwd());
        {
            auto mockWriter = mockClient.CreateCombinedWriter<NPlutonium::TDocWadLumps, NPlutonium::TGlobalWadLump>(DocLumpsTable, GlobalLumpsTable);
            ui32 docId = 0;
            if (hasOld) {
                docId = WriteTestData<TOldIo, /*WriteAsOld=*/true>(mockWriter.Get(), docId, docId + DocCount);
            }
            if (hasNew) {
                docId = WriteTestData<TIo, /*WriteAsOld=*/false>(mockWriter.Get(), docId, docId + DocCount);
            }
        }
        mockClient.FinishWriters();

        //
        // 2. Get data from YT tables and write a single-chunked MegaWad using NPlutonium::WriteRawLumps
        //
        const TString outputPath = TFsPath::Cwd() / "test_local_index" / "index.test";
        const TFsPath outputWadPath = outputPath + ".wad";
        {
            NDoom::TMegaWadWriter megawadWriter(outputWadPath);
            const TVector<NYT::TRichYPath> docLumpsPaths = {DocLumpsTable};
            const TVector<NYT::TRichYPath> globalLumpsPaths = {GlobalLumpsTable};

            TVector<THolder<NPlutonium::IRawGlobalWadLumpsProcessor>> processors;
            if (mergeAsNew) {
                processors.push_back(MakeHolder<NPlutonium::TOffroadStructWadGlobalLumpsProcessor<TIo>>());
            } else {
                processors.push_back(MakeHolder<NPlutonium::TOffroadStructWadGlobalLumpsProcessor<TOldIo>>());
            }

            NPlutonium::WriteRawLumps(
                processors,
                mockClient.AsIOClient(),
                docLumpsPaths,
                globalLumpsPaths,
                TString(TestShard),
                &megawadWriter);
        }
        UNIT_ASSERT(outputWadPath.Exists());

        const bool readAsNew = mergeAsNew;
        //
        // 3. Read data from index.test.wad, dump it into string and compare
        //
        TString expected;
        {
            TStringStream ss;
            ui32 docId = 0;
            if (hasOld) {
                const TStringBuf oldHitStr = !readAsNew ? "ab"sv : "ab\0"sv;
                docId = FormatExpectedResult(&ss, oldHitStr, docId, docId + DocCount);
            }
            if (hasNew) {
                const TStringBuf newHitStr = !readAsNew ? "ab"sv : hasOld ? "ab\0"sv : "abc"sv;
                docId = FormatExpectedResult(&ss, newHitStr, docId, docId + DocCount);
            }
            expected = ss.Str();
        }

        TString actual;
        if (readAsNew) {
            actual = ReadActualWad<TIo>(outputWadPath);
        } else {
            actual = ReadActualWad<TOldIo>(outputWadPath);
        }

        // for better readability, replace '\0' with '0' in both 'expected' and 'actual'
        SubstGlobal(expected, '\0', '0');
        SubstGlobal(actual, '\0', '0');

        UNIT_ASSERT_VALUES_EQUAL_C(expected, actual, testCaseDisplayName);
        Cout << "Check OK: " << testCaseDisplayName << " -> " << actual << Endl;
    }

    Y_UNIT_TEST(SizeChangedCompressed) {
        // compressed, no mixing
        DoTest<OffroadCompressionType>(true, false, false);
        DoTest<OffroadCompressionType>(false, true, false);
        DoTest<OffroadCompressionType>(true, false, true);
        DoTest<OffroadCompressionType>(false, true, true);

        // compressed, mix old and new lumps
        DoTest<OffroadCompressionType>(true, true, true);
        DoTest<OffroadCompressionType>(true, true, false);
    }

    Y_UNIT_TEST(SizeChangedRaw) {
        // uncompressed, no mixing
        DoTest<RawCompressionType>(true, false, false);
        DoTest<RawCompressionType>(false, true, false);
        DoTest<RawCompressionType>(true, false, true);
        DoTest<RawCompressionType>(false, true, true);

        // uncompressed, mix old and new lumps
        DoTest<RawCompressionType>(true, true, true);
        DoTest<RawCompressionType>(true, true, false);
    }
}
