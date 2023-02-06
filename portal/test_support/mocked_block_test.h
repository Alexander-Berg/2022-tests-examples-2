#pragma once

#include "block_part_test.h"
#include "test_block_input.h"

#include <portal/morda/blocks/common/block_base.h>
#include <portal/morda/blocks/common/block_answer.h>

#include <memory>

namespace NMordaBlocks {
    class TBlockBase;

    class TMockedBlockTest: public TBlockPartTest {
    public:
        class TAnswerWaiter: public TNonCopyable {
        public:
            TAnswerWaiter(TBlockPartTest* test, TIntrusivePtr<TBlockAnswerBase> answer)
                : Test_(test)
                , Answer_(answer) {
            }
            ~TAnswerWaiter() = default;

        protected:
            TIntrusivePtr<TBlockAnswerBase> WaitBase();

        private:
            TBlockPartTest* Test_;
            TIntrusivePtr<TBlockAnswerBase> Answer_;
        };

        class TPrepareAnswerWaiter: public TAnswerWaiter{
        public:
            using TAnswerWaiter::TAnswerWaiter;

            TPrepareAnswerPtr Wait() {
                return static_cast<TPrepareAnswer*>(WaitBase().Get());
            }
        };

        class TProcessorAnswerWaiter : public TAnswerWaiter {
        public:
            using TAnswerWaiter::TAnswerWaiter;

            TProcessorAnswerPtr Wait() {
                return static_cast<TProcessorAnswer*>(WaitBase().Get());
            }
        };

        class TFormatterAnswerWaiter : public TAnswerWaiter {
        public:
            using TAnswerWaiter::TAnswerWaiter;

            TFormatterAnswerPtr Wait() {
                return static_cast<TFormatterAnswer*>(WaitBase().Get());
            }
        };

        TMockedBlockTest();

        ~TMockedBlockTest() override;

        void SetUp() override;

        void AssignBlock(std::unique_ptr<TBlockBase> block);

        TBlockAnswerPtr ProcessRequest(TStringBuf rawJsonSettings);
        TBlockAnswerPtr ProcessRequest(const NJson::TJsonValue& settings);
        TBlockAnswerPtr ProcessRequest(std::unique_ptr<TTestProcessorInput> input);
        TBlockAnswerPtr ProcessRequest();

        std::unique_ptr<TPrepareAnswerWaiter> DoPrepareAsync(TStringBuf rawJsonSettings);
        std::unique_ptr<TPrepareAnswerWaiter> DoPrepareAsync(const NJson::TJsonValue& settings);
        std::unique_ptr<TPrepareAnswerWaiter> DoPrepareAsync(const TTestPrepareInput& input);
        std::unique_ptr<TPrepareAnswerWaiter> DoPrepareAsync();

        TPrepareAnswerPtr DoPrepare(TStringBuf rawJsonSettings);
        TPrepareAnswerPtr DoPrepare(const NJson::TJsonValue& settings);
        TPrepareAnswerPtr DoPrepare(const TTestPrepareInput& input);
        TPrepareAnswerPtr DoPrepare();

        std::unique_ptr<TProcessorAnswerWaiter> DoProcessDataAsync(TStringBuf rawJsonSettings);
        std::unique_ptr<TProcessorAnswerWaiter> DoProcessDataAsync(const NJson::TJsonValue& settings);
        std::unique_ptr<TProcessorAnswerWaiter> DoProcessDataAsync(const TTestProcessorInput& input);
        std::unique_ptr<TProcessorAnswerWaiter> DoProcessDataAsync();

        TProcessorAnswerPtr DoProcessData(TStringBuf rawJsonSettings);
        TProcessorAnswerPtr DoProcessData(const NJson::TJsonValue& settings);
        TProcessorAnswerPtr DoProcessData(const TTestProcessorInput& input);
        TProcessorAnswerPtr DoProcessData();

        std::unique_ptr<TFormatterAnswerWaiter> DoFormatDataAsync(TStringBuf rawJsonSettings);
        std::unique_ptr<TFormatterAnswerWaiter> DoFormatDataAsync(const NJson::TJsonValue& settings);
        std::unique_ptr<TFormatterAnswerWaiter> DoFormatDataAsync(const TTestFormatterInput& input);
        std::unique_ptr<TFormatterAnswerWaiter> DoFormatDataAsync();

        TFormatterAnswerPtr DoFormatData(TStringBuf rawJsonSettings);
        TFormatterAnswerPtr DoFormatData(const NJson::TJsonValue& settings);
        TFormatterAnswerPtr DoFormatData(const TTestFormatterInput& input);
        TFormatterAnswerPtr DoFormatData();

        TBlockBase* GetBlock() {
            return Block_.get();
        }

    private:
        std::unique_ptr<TBlockBase> Block_;
        bool BlockStarted_ = false;
    };

} // namespace NMordaBlocks
