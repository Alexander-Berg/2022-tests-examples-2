#pragma once

#include <portal/morda/blocks/server/response_context.h>

#include <apphost/lib/service_testing/service_testing.h>

namespace NMordaBlocks {

    class TTestResponseContext : public IResponseContext {
    public:
        explicit TTestResponseContext();
        ~TTestResponseContext() override;

        void Add(TStringBuf type, NJson::TJsonValue&& response) override;
        void AddProtobuf(const TStringBuf& type, const google::protobuf::Message& item) override;
        void AddFlag(TString flag) override;
        const NJson::TJsonValue* FindFirstItem(TStringBuf type) const;
        const NJson::TJsonValue& GetOnlyItem(TStringBuf type) const;
        const THashSet<TString>& GetFlags() const;

        bool HasAnyData() const;
        bool HasProtobufData() const;

        template <class T = google::protobuf::Message>
        std::unique_ptr<T> FindFirstProtobufItem(TStringBuf type) const {
            auto* apphostProtobufItem = FindFirstProtobufItemImpl(type);
            if (!apphostProtobufItem)
                return nullptr;

            auto result = std::make_unique<T>();
            Y_ENSURE(result, "Protobuf was not created!");
            if (!apphostProtobufItem->Fill(result.get())) {
                return nullptr;
            }
            return result;
        }

    private:
        const NAppHost::NService::TProtobufItem* FindFirstProtobufItemImpl(TStringBuf type) const;

    private:
        NAppHost::NService::TTestContext Context_;
    };

} // namespace NMordaBlocks
