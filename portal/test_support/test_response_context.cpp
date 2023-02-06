#include "test_response_context.h"

namespace NMordaBlocks {

    TTestResponseContext::TTestResponseContext()
        : Context_(NJson::JSON_ARRAY) {
    }

    TTestResponseContext::~TTestResponseContext() = default;

    void TTestResponseContext::Add(TStringBuf type, NJson::TJsonValue&& response) {
        Context_.AddItem(std::move(response), type);
    }

    void TTestResponseContext::AddProtobuf(const TStringBuf& type, const google::protobuf::Message& item) {
        Context_.AddProtobufItem(item, type);
    }

    void TTestResponseContext::AddFlag(TString flag) {
        Context_.AddFlag(flag);
    }

    const NJson::TJsonValue* TTestResponseContext::FindFirstItem(TStringBuf type) const {
        return Context_.FindFirstItem(type);
    }

    const NJson::TJsonValue& TTestResponseContext::GetOnlyItem(TStringBuf type) const {
        return Context_.GetOnlyItem(type);
    }

    const THashSet<TString>& TTestResponseContext::GetFlags() const {
        return Context_.GetFlags();
    }

    const NAppHost::NService::TProtobufItem* TTestResponseContext::FindFirstProtobufItemImpl(TStringBuf type) const {
        const auto refs = Context_.GetProtobufItemRefs(type);
        return refs.empty() ? nullptr : &refs.front();
    }

    bool TTestResponseContext::HasAnyData() const {
        return !Context_.GetRawItemRefs().empty();
    }

    bool TTestResponseContext::HasProtobufData() const {
        return !Context_.GetProtobufItemRefs().empty();
    }

} // namespace NMordaBlocks
