#pragma once

#include "test_input_context.h"

#include <portal/morda/blocks/common/block_answer.h>
#include <portal/morda/blocks/common/block_input.h>

#include <util/generic/map.h>
#include <util/generic/maybe.h>

namespace NMordaBlocks {

    class TTestPrepareInput : public TNonCopyable {
    public:
        TTestPrepareInput();
        explicit TTestPrepareInput(const NJson::TJsonValue& settings);
        explicit TTestPrepareInput(TStringBuf rawJsonSettings);

        virtual ~TTestPrepareInput();

        void AddBlockInputsData(const TString& blockTag, const google::protobuf::Message& data);

        TPrepareInputPtr MakeReal(const TString& blockName) const;

        const TMap<TString, TString> Inputs() const {
            return Inputs_;
        }

        const NJson::TJsonValue& Settings() const {
            return Settings_;
        }

    protected:
        TIntrusivePtr<TTestInputContext> MakeInputContext(const TString& blockName) const;

    private:
        NJson::TJsonValue Settings_;
        TMap<TString, TString> Inputs_;
    };

    class TTestProcessorInput : public TTestPrepareInput {
    public:
        using TTestPrepareInput::TTestPrepareInput;
        ~TTestProcessorInput() override;

        TProcessorInputPtr MakeReal(const TString& blockName) const;

        void SetPreprocessorData(const google::protobuf::Message& data);
        void SetPreprocessorDataFromAnswer(TPrepareAnswerPtr answer);
        void SetHttpResponse(const TString& externalSourceTag, const TProcessorInput::THttpResponse& response);
        void SetHttpJsonResponse(const TString& externalSourceTag, const NJson::TJsonValue& json);
        void SetHttpRawDataResponse(const TString& externalSourceTag, TStringBuf raw);
        void SetHttpRawJsonResponse(const TString& externalSourceTag, TStringBuf rawJson);
        void SetProtobufResponse(const TString& externalSourceTag, const google::protobuf::Message& data);
        void SetHttpResponseError(const TString& externalSourceTag, int error);

        const TMap<TString, TString> HttpResponses() const {
            return HttpResponses_;
        }

    private:
        TMaybe<TString> Data_;
        TMap<TString, TString> HttpResponses_;
    };

    class TTestFormatterInput: public TTestPrepareInput {
    public:
        using TTestPrepareInput::TTestPrepareInput;
        ~TTestFormatterInput() override;

        TFormatterInputPtr MakeReal(const TString& blockName) const;

        void SetProcessorData(const google::protobuf::Message& data);
        void SetFormatterData(const google::protobuf::Message& data);
        void SetAllDataFromAnswer(TProcessorAnswerPtr answer);

    private:
        using TTestPrepareInput::AddBlockInputsData;

    private:
        TMaybe<TString> ProcessorData_;
        TMaybe<TString> FormatterData_;
    };

} // namespace NMordaBlocks
