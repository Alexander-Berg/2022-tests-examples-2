#include "mocked_block_test.h"

#include <portal/morda/blocks/core/session/session_tasks_sequence.h>

#include <utility>

namespace NMordaBlocks {

    TIntrusivePtr<TBlockAnswerBase> TMockedBlockTest::TAnswerWaiter::WaitBase() {
        while (Answer_->RefCount() > 1) {
            Test_->GetTestTasksRunner()->RunPendingTasks();
        }
        return std::move(Answer_);
    }

    TMockedBlockTest::TMockedBlockTest() {
    }

    TMockedBlockTest::~TMockedBlockTest() = default;

    void TMockedBlockTest::SetUp() {
        TBlockPartTest::SetUp();
        if (!BlockStarted_) {
            Y_ASSERT(Block_);
            BlockStarted_ = true;
            Block_->Start();
            while (!Block_->IsReady()) {
                GetTestTasksRunner()->RunPendingTasks();
            }
        }
    }

    void TMockedBlockTest::AssignBlock(std::unique_ptr<TBlockBase> block) {
        Y_ASSERT(!BlockStarted_);
        Block_ = std::move(block);
    }

    TBlockAnswerPtr TMockedBlockTest::ProcessRequest(TStringBuf rawJsonSettings) {
        return ProcessRequest(std::make_unique<TTestProcessorInput>(rawJsonSettings));
    }

    TBlockAnswerPtr TMockedBlockTest::ProcessRequest(const NJson::TJsonValue& settings) {
        return ProcessRequest(std::make_unique<TTestProcessorInput>(settings));
    }

    TBlockAnswerPtr TMockedBlockTest::ProcessRequest(std::unique_ptr<TTestProcessorInput> input) {
        Y_ASSERT(input);
        TPrepareAnswerPtr prepareAnswer = DoPrepare(*input);
        for (const auto& otherBlockInput : input->HttpResponses()) {
            Y_ENSURE(prepareAnswer->HttpRequests().count(otherBlockInput.first),
                     TString() + "The http request is not filled for " + otherBlockInput.first);
        }

        input->SetPreprocessorDataFromAnswer(prepareAnswer);
        TProcessorAnswerPtr processorAnswer = DoProcessData(*input);

        TTestFormatterInput formatterInput(input->Settings());
        formatterInput.SetAllDataFromAnswer(processorAnswer);
        return DoFormatData(formatterInput);
    }

    TBlockAnswerPtr TMockedBlockTest::ProcessRequest(){
        return ProcessRequest(NJson::TJsonValue());
    }

    std::unique_ptr<TMockedBlockTest::TPrepareAnswerWaiter> TMockedBlockTest::DoPrepareAsync(TStringBuf rawJsonSettings) {
        return DoPrepareAsync(TTestPrepareInput(rawJsonSettings));
    }

    std::unique_ptr<TMockedBlockTest::TPrepareAnswerWaiter> TMockedBlockTest::DoPrepareAsync(const NJson::TJsonValue& settings) {
        return DoPrepareAsync(TTestPrepareInput(settings));
    }

    std::unique_ptr<TMockedBlockTest::TPrepareAnswerWaiter> TMockedBlockTest::DoPrepareAsync(const TTestPrepareInput& input) {
        std::unique_ptr<TPrepareAnswerWaiter> waiter;
        {
            auto answer = MakeIntrusive<TPrepareAnswer>(Block_->BlockName());
            waiter = std::make_unique<TPrepareAnswerWaiter>(this, answer);
            Block_->Prepare(input.MakeReal(Block_->BlockName()), answer);
        }
        return waiter;
    }

    std::unique_ptr<TMockedBlockTest::TPrepareAnswerWaiter> TMockedBlockTest::DoPrepareAsync() {
        return DoPrepareAsync(NJson::TJsonValue());
    }

    TPrepareAnswerPtr TMockedBlockTest::DoPrepare(TStringBuf rawJsonSettings) {
        return DoPrepareAsync(rawJsonSettings)->Wait();
    }

    TPrepareAnswerPtr TMockedBlockTest::DoPrepare(const NJson::TJsonValue& settings) {
        return DoPrepareAsync(settings)->Wait();
    }

    TPrepareAnswerPtr TMockedBlockTest::DoPrepare(const TTestPrepareInput& input) {
        return DoPrepareAsync(input)->Wait();
    }

    TPrepareAnswerPtr TMockedBlockTest::DoPrepare() {
        return DoPrepareAsync()->Wait();
    }

    std::unique_ptr<TMockedBlockTest::TProcessorAnswerWaiter> TMockedBlockTest::DoProcessDataAsync(TStringBuf rawJsonSettings) {
        return DoProcessDataAsync(TTestProcessorInput(rawJsonSettings));
    }

    std::unique_ptr<TMockedBlockTest::TProcessorAnswerWaiter> TMockedBlockTest::DoProcessDataAsync(const NJson::TJsonValue& settings) {
        return DoProcessDataAsync(TTestProcessorInput(settings));
    }

    std::unique_ptr<TMockedBlockTest::TProcessorAnswerWaiter> TMockedBlockTest::DoProcessDataAsync(const TTestProcessorInput& input) {
        std::unique_ptr<TProcessorAnswerWaiter> waiter;
        {
            auto answer = MakeIntrusive<TProcessorAnswer>(Block_->BlockName());
            waiter = std::make_unique<TProcessorAnswerWaiter>(this, answer);
            Block_->Process(input.MakeReal(Block_->BlockName()), answer);
        }
        return waiter;
    }

    std::unique_ptr<TMockedBlockTest::TProcessorAnswerWaiter> TMockedBlockTest::DoProcessDataAsync() {
        return DoProcessDataAsync(NJson::TJsonValue());
    }

    TProcessorAnswerPtr TMockedBlockTest::DoProcessData(TStringBuf rawJsonSettings) {
        return DoProcessDataAsync(rawJsonSettings)->Wait();
    }

    TProcessorAnswerPtr TMockedBlockTest::DoProcessData(const NJson::TJsonValue& settings) {
        return DoProcessDataAsync(settings)->Wait();
    }

    TProcessorAnswerPtr TMockedBlockTest::DoProcessData(const TTestProcessorInput& input) {
        return DoProcessDataAsync(input)->Wait();
    }

    TProcessorAnswerPtr TMockedBlockTest::DoProcessData() {
        return DoProcessDataAsync()->Wait();
    }

    std::unique_ptr<TMockedBlockTest::TFormatterAnswerWaiter> TMockedBlockTest::DoFormatDataAsync(TStringBuf rawJsonSettings) {
        return DoFormatDataAsync(TTestFormatterInput(rawJsonSettings));
    }

    std::unique_ptr<TMockedBlockTest::TFormatterAnswerWaiter> TMockedBlockTest::DoFormatDataAsync(const NJson::TJsonValue& settings) {
        return DoFormatDataAsync(TTestFormatterInput(settings));
    }

    std::unique_ptr<TMockedBlockTest::TFormatterAnswerWaiter> TMockedBlockTest::DoFormatDataAsync(const TTestFormatterInput& input) {
        std::unique_ptr<TFormatterAnswerWaiter> waiter;
        {
            auto answer = MakeIntrusive<TFormatterAnswer>(Block_->BlockName());
            waiter = std::make_unique<TFormatterAnswerWaiter>(this, answer);
            Block_->FormatData(input.MakeReal(Block_->BlockName()), answer);
        }
        return waiter;
    }

    std::unique_ptr<TMockedBlockTest::TFormatterAnswerWaiter> TMockedBlockTest::DoFormatDataAsync() {
        return DoFormatDataAsync(NJson::TJsonValue());
    }

    TFormatterAnswerPtr TMockedBlockTest::DoFormatData(TStringBuf rawJsonSettings) {
        return DoFormatDataAsync(rawJsonSettings)->Wait();
    }

    TFormatterAnswerPtr TMockedBlockTest::DoFormatData(const NJson::TJsonValue& settings) {
        return DoFormatDataAsync(settings)->Wait();
    }

    TFormatterAnswerPtr TMockedBlockTest::DoFormatData(const TTestFormatterInput& input) {
        return DoFormatDataAsync(input)->Wait();
    }

    TFormatterAnswerPtr TMockedBlockTest::DoFormatData() {
        return DoFormatDataAsync()->Wait();
    }

} // namespace NMordaBlocks
