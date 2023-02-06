#pragma once

#include <mapreduce/yt/interface/io.h>
#include <util/folder/path.h>

namespace NRtDoc {
    //
    // TTestLocalClient: A slim file-based IIOClient. Useful for non-SaaS unittests
    //
    class TTestLocalClient {
    private:
        class TImpl;

    public:
        TTestLocalClient(const TFsPath& tempDirectory);
        ~TTestLocalClient();

        void FinishWriters();
        void CleanupTempFiles();

        NYT::IIOClient& AsIOClient() const;

    public:
        // Helper method to create a combined writer in a simple test case
        NYT::TTableWriterPtr<NProtoBuf::Message> CreateCombinedWriter(const TString& tblName1, const NProtoBuf::Descriptor* type1,
                const TString& tblName2, const NProtoBuf::Descriptor* type2);

        template <typename TProto1, typename TProto2>
        inline NYT::TTableWriterPtr<NProtoBuf::Message> CreateCombinedWriter(const TString& tblName1, const TString& tblName2) {
            return CreateCombinedWriter(tblName1, TProto1::descriptor(), tblName2, TProto2::descriptor());
        }

    private:
        THolder<TImpl> Impl;
    };
}
