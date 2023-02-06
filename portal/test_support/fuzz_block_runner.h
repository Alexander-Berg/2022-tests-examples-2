#pragma once

#include "test_block_runner.h"

#include <portal/morda/blocks/request_context/request_context.pb.h>

#include <library/cpp/json/json_value.h>

namespace NMordaBlocks {

    class TFuzzBlockRunner : public TTestBlockRunner {
    public:
        TFuzzBlockRunner();
        ~TFuzzBlockRunner() override;

        void SetStaticRequestLegacyData(NJson::TJsonValue value);
        void SetStaticRequestData(const TRequestContextProto& proto);

        void ProcessFuzzRequest(const uint8_t* data, size_t size);
    private:
        TRequestContextProto StaticRequestData_;
        NJson::TJsonValue StaticRequestLegacyData_;
    };

} // namespace NMordaBlocks
