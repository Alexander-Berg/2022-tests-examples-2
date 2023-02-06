#include "test_input_context.h"

namespace NMordaBlocks {

    TTestInputContext::TTestInputContext()
        : Context_(NJson::JSON_ARRAY) {
    }

    TTestInputContext::~TTestInputContext() = default;

    void TTestInputContext::AddItem(TStringBuf type, NJson::TJsonValue&& response) {
        Context_.AddItem(std::move(response), type);
    }

    void TTestInputContext::AddProtobufItem(TStringBuf type, const google::protobuf::Message& item) {
        Context_.AddProtobufItem(item, type);
    }

    void TTestInputContext::AddRawProtobufItem(TStringBuf type, TStringBuf data) {
        RawProtobufs_[TString(type)] = TString(data);
    }

    const NJson::TJsonValue* TTestInputContext::FindFirstItem(TStringBuf type) const {
        return Context_.FindFirstItem(type);
    }

    const NJson::TJsonValue& TTestInputContext::GetOnlyItem(TStringBuf type) const {
        return Context_.GetOnlyItem(type);
    }

    TStringBuf TTestInputContext::GetGraphName() const {
        const NAppHost::TLocation location = Context_.GetLocation();
        return location.Path.substr(0, location.Path.find('/'));
    }

    bool TTestInputContext::FindFirstProtobufItem(TStringBuf type, google::protobuf::Message* out) const {
        if (!out)
            return false;

        {
            const auto refs = Context_.GetProtobufItemRefs(type);
            if (!refs.empty())
                return refs.front().Fill(out);
        }
        const auto it = RawProtobufs_.find(TString(type));
        if (it == RawProtobufs_.end())
            return false;

        const auto& rawData = it->second;
        return out->ParseFromArray(rawData.data(), rawData.size());
    }

} // namespace NMordaBlocks
