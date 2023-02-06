#pragma once

#include <portal/morda/blocks/server/input_context.h>

#include <apphost/lib/service_testing/service_testing.h>

namespace NMordaBlocks {

    class TTestInputContext : public IInputContext {
    public:
        explicit TTestInputContext();
        ~TTestInputContext() override;

        void AddItem(TStringBuf type, NJson::TJsonValue&& response);
        void AddProtobufItem(TStringBuf type, const google::protobuf::Message& item);
        void AddRawProtobufItem(TStringBuf type, TStringBuf data);

        const NJson::TJsonValue* FindFirstItem(TStringBuf type) const override;
        const NJson::TJsonValue& GetOnlyItem(TStringBuf type) const override;
        TStringBuf GetGraphName() const override;
        bool FindFirstProtobufItem(TStringBuf type, google::protobuf::Message* out) const override;

    private:
        NAppHost::NService::TTestContext Context_;
        TMap<TString, TString> RawProtobufs_;
    };

} // namespace NMordaBlocks
