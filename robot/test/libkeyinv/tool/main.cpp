#include <robot/pluto/library/libkeyinv/key_inv.h>

#include <robot/library/oxygen/indexer/keyinv/print/print_portions.h>

#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/registar.h>
#include <library/cpp/testing/unittest/tests_data.h>

#include <util/folder/filelist.h>
#include <util/folder/tempdir.h>
#include <util/system/shellcommand.h>


using namespace NPluto;

namespace {

    inline THolder<TKeyInvGenerator> InitializeGenerator(const TFsPath& dataDir) {
        const TFsPath resDir = BinaryPath("robot/rthub/packages/resources/libkeyinv");

        TFileEntitiesList archives(TFileEntitiesList::EM_FILES | TFileEntitiesList::EM_FILES_SLINKS);
        archives.Fill(resDir, {}, ".tar", 1);

        while (const auto name = archives.Next()) {
            TShellCommand untar("/bin/tar");
            untar << "-xvf" << (resDir / name).GetPath() << "-C" << dataDir.GetPath();
            untar.Run();

            const auto code = untar.GetExitCode();
            UNIT_ASSERT_C(code, "Cannot extract test data: " + untar.GetInternalError());
            UNIT_ASSERT_EQUAL_C(*code, 0, "Cannot extract test data: " + untar.GetError());
        }

        const auto directTextPurePath = dataDir / "pure/pure.trie";
        const auto directTextConfigPath = dataDir / "direct_text_config";
        const auto directTextSeoLnkPath = dataDir / "seolnk";
        const auto metaDescrDictPath = dataDir / "dict.dict";
        const auto metaDescrStopwordPath = dataDir / "stopword.lst";
        const auto nameExtractorFioPath = dataDir / "fio/name_extractor.cfg";
        const auto newshostPath = dataDir / "news_hosts.txt";
        const auto numberPath = dataDir / "numbers";
        const auto numeratorConfigsPath = dataDir / "numerator_config";
        const auto phoneNumberPath = dataDir / "phone_markers.gzt.bin";
        const auto segmentatorPath = dataDir / "2ld.list";
        const auto tasixhostPath = dataDir / "tasix_hosts.txt";

        return MakeHolder<TKeyInvGenerator>(
            directTextPurePath,
            directTextConfigPath,
            directTextSeoLnkPath,
            metaDescrDictPath,
            metaDescrStopwordPath,
            nameExtractorFioPath,
            newshostPath,
            numberPath,
            numeratorConfigsPath,
            phoneNumberPath,
            segmentatorPath,
            tasixhostPath,
            false);
    }

} // namespace

namespace NPluto {

    Y_UNIT_TEST_SUITE(LibKeyInv) {

        Y_UNIT_TEST(KeyInv) {
            const auto dataDir = TFsPath(GetWorkPath()) / "data";

            TTempDir dir(dataDir);

            const auto generator = InitializeGenerator(dataDir);
            const auto text = Cin.ReadAll();
            const auto language = ELanguage::LANG_RUS;

            const auto result = generator->Generate(
                text,
                {},
                0,
                0,
                ECharset::CODES_UTF8,
                language,
                language,
                0,
                MimeTypes::MIME_TEXT);

            NOxygen::PrintKeyInvPortions(result, "zlib+oki1", Cout);
        }

    }

} // namespace NPluto
