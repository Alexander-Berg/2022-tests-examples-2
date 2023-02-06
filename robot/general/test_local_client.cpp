#include "test_local_client.h"
#include <robot/jupiter/library/rtdoc/file/yt_client.h>
#include <robot/jupiter/library/rtdoc/file/portions_output.h>
#include <kernel/yt/utils/yt_utils.h>
#include <util/system/fs.h>

namespace NRtDoc {
    class TTestLocalClient::TImpl {
    public:
        const TFsPath Arena;
        TBuilderTask Task;
        TBuilderLocalClientPtr Client;

    public:
        TImpl(const TFsPath& tempDirectory)
            : Arena(tempDirectory / "test_local_index")
        {
            tempDirectory.CheckExists();
            Cleanup();
            Arena.MkDir();

            auto deltaInput = Task.AddInputs();
            deltaInput->SetSrcDir(Arena);
            deltaInput->SetIsFinalIndex(false);

            const TFsPath& deltaDir = Arena;
            Task.MutableOutput()->SetTempDir(deltaDir);

            auto portionsConfig = MakeIntrusive<TBuilderPortionsConfig>("test.table.");
            auto portionsOutput = MakeIntrusive<TPortionsOutput>(deltaDir, portionsConfig);

            Client = MakeIntrusive<TBuilderLocalClient>(Task, /*delta=*/true);
            Client->SetPortionsInput(portionsConfig, deltaDir);
            Client->SetPortionsOutput(portionsOutput);
        }

        void Cleanup() {
            if (NFs::Exists(Arena)) {
                NFs::RemoveRecursive(Arena);
            }
        }
    };

    TTestLocalClient::TTestLocalClient(const TFsPath& tempDirectory)
        : Impl(MakeHolder<TImpl>(tempDirectory))
    {
    }

    TTestLocalClient::~TTestLocalClient() {
    }

    void TTestLocalClient::FinishWriters() {
        ILocalClient& localClient = *Impl->Client;
        localClient.Finish();
    }

    void TTestLocalClient::CleanupTempFiles() {
        Impl->Cleanup();
    }

    NYT::IIOClient& TTestLocalClient::AsIOClient() const {
        return *Impl->Client;
    }

    NYT::TTableWriterPtr<NProtoBuf::Message> TTestLocalClient::CreateCombinedWriter(
            const TString& tblName1,
            const NProtoBuf::Descriptor* type1,
            const TString& tblName2,
            const NProtoBuf::Descriptor* type2)
    {
        ILocalJoinClient& localClient = *Impl->Client;
        auto writerImpl = localClient.CreateLocalJoinWriter({{tblName1, type1}, {tblName2, type2}});
        return new NYT::TTableWriter<NProtoBuf::Message>(writerImpl);
    }


}
