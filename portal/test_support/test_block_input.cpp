#include "test_block_input.h"

#include <portal/morda/blocks/test_support/json_test_utils.h>

#include <library/cpp/json/json_writer.h>

namespace NMordaBlocks {

    namespace {
    } // namespace

    TTestPrepareInput::TTestPrepareInput() = default;

    TTestPrepareInput::TTestPrepareInput(const NJson::TJsonValue& settings)
        : Settings_(settings) {
    }

    TTestPrepareInput::TTestPrepareInput(TStringBuf rawJsonSettings)
        : TTestPrepareInput(NTest::ReadJsonFromString(rawJsonSettings)) {
    }

    TTestPrepareInput::~TTestPrepareInput() = default;

    void TTestPrepareInput::AddBlockInputsData(const TString& blockTag, const google::protobuf::Message& data) {
        TStringStream buffer;
        data.SerializeToArcadiaStream(&buffer);
        Inputs_[blockTag] = buffer.Str();
    }

    TPrepareInputPtr TTestPrepareInput::MakeReal(const TString& blockName) const {
        return MakeIntrusiveConst<TPrepareInput>(blockName, MakeInputContext(blockName).Get());
    }

    TIntrusivePtr<TTestInputContext> TTestPrepareInput::MakeInputContext(const TString& blockName) const {
        auto context = MakeIntrusive<TTestInputContext>();
        NJson::TJsonValue settingsCopy = Settings_;
        if (settingsCopy.IsDefined())
            context->AddItem("block_settings_" + blockName, std::move(settingsCopy));
        for (const auto& it : Inputs()) {
            context->AddRawProtobufItem(it.first, it.second);
        }
        return context;
    }

    TTestProcessorInput::~TTestProcessorInput() = default;

    TProcessorInputPtr TTestProcessorInput::MakeReal(const TString& blockName) const {
        auto context = MakeInputContext(blockName);
        for (const auto& it : HttpResponses_) {
            context->AddRawProtobufItem(TProcessorInput::MakeHttpResponseContextType(it.first), it.second);
        }
        if (Data_) {
            context->AddRawProtobufItem(TPrepareAnswer::MakePrepareContextType(blockName), *Data_);
        }
        return MakeIntrusiveConst<TProcessorInput>(blockName, context.Get());
    }

    void TTestProcessorInput::SetPreprocessorData(const google::protobuf::Message& data) {
        TStringStream buffer;
        data.SerializeToArcadiaStream(&buffer);
        Data_ = buffer.Str();
    }

    void TTestProcessorInput::SetPreprocessorDataFromAnswer(TPrepareAnswerPtr answer) {
        if (!answer || !answer->Data())
            return;

        SetPreprocessorData(*answer->Data());
    }

    void TTestProcessorInput::SetHttpResponse(const TString& externalSourceTag, const TProcessorInput::THttpResponse& response) {
        TStringStream buffer;
        response.SerializeToArcadiaStream(&buffer);
        HttpResponses_[externalSourceTag] = buffer.Str();
    }

    void TTestProcessorInput::SetHttpJsonResponse(const TString& externalSourceTag, const NJson::TJsonValue& json) {
        SetHttpRawDataResponse(externalSourceTag, WriteJson(json));
    }

    void TTestProcessorInput::SetHttpResponseError(const TString& externalSourceTag, int error) {
        TProcessorInput::THttpResponse response;
        response.SetStatusCode(error);
        SetHttpResponse(externalSourceTag, response);
    }

    void TTestProcessorInput::SetHttpRawDataResponse(const TString& externalSourceTag, TStringBuf raw) {
        TProcessorInput::THttpResponse response;
        response.SetStatusCode(200);
        response.SetContent(TString(raw));
        SetHttpResponse(externalSourceTag, response);
    }

    void TTestProcessorInput::SetHttpRawJsonResponse(const TString& externalSourceTag, TStringBuf rawJson) {
        SetHttpJsonResponse(externalSourceTag, NTest::ReadJsonFromString(rawJson));
    }

    void TTestProcessorInput::SetProtobufResponse(const TString& externalSourceTag, const google::protobuf::Message& data) {
        TStringStream buffer;
        data.SerializeToArcadiaStream(&buffer);
        SetHttpRawDataResponse(externalSourceTag, buffer.Str());
    }

    TTestFormatterInput::~TTestFormatterInput() = default;

    TFormatterInputPtr TTestFormatterInput::MakeReal(const TString& blockName) const {
        auto context = MakeInputContext(blockName);
        if (ProcessorData_) {
            context->AddRawProtobufItem(TProcessorAnswer::MakeDataContextType(blockName), *ProcessorData_);
        }
        if (FormatterData_) {
            context->AddRawProtobufItem(TProcessorAnswer::MakeFormatterDataContextType(blockName), *FormatterData_);
        }
        return MakeIntrusiveConst<TFormatterInput>(blockName, context.Get());
    }

    void TTestFormatterInput::SetProcessorData(const google::protobuf::Message& data) {
        TStringStream buffer;
        data.SerializeToArcadiaStream(&buffer);
        ProcessorData_ = buffer.Str();
    }

    void TTestFormatterInput::SetFormatterData(const google::protobuf::Message& data) {
        TStringStream buffer;
        data.SerializeToArcadiaStream(&buffer);
        FormatterData_ = buffer.Str();
    }

    void TTestFormatterInput::SetAllDataFromAnswer(TProcessorAnswerPtr answer) {
        if (!answer)
            return;

        if (answer->Data())
            SetProcessorData(*answer->Data());

        if (answer->FormatterData())
            SetFormatterData(*answer->FormatterData());
    }

} // namespace NMordaBlocks
