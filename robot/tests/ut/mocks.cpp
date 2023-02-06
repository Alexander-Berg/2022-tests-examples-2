#include "mocks.h"
#include <library/cpp/testing/unittest/registar.h>

namespace NRTHub {
    TFuture<TVector<TIoOperation>> TMockChannelExecutor::Submit(TIncomingMessage&& message) noexcept {
        TSubmittedMessage submittedMessage{
            std::move(message),
            NewPromise<TVector<TIoOperation>>()};
        SubmittedMessages.push_back(std::move(submittedMessage));
        return SubmittedMessages.back().Promise.GetFuture();
    }

    void TMockChannelExecutor::CompleteAll() {
        TVector<TIoOperation> emptyOperations;
        while (!SubmittedMessages.empty()) {
            TSubmittedMessage& message = SubmittedMessages.back();
            message.Promise.SetValue(emptyOperations);
            SubmittedMessages.pop_back();
        }
    }

    void TMockChannelExecutor::CompleteAll(const TVector<TString>& expected) {
        CheckAll(expected);
        CompleteAll();
    }

    void TMockChannelExecutor::CheckAll(const TVector<TString>& expected) const {
        UNIT_ASSERT_VALUES_EQUAL(expected.size(), SubmittedMessages.size());
        for (size_t i = 0; i < SubmittedMessages.size(); ++i) {
            UNIT_ASSERT_VALUES_EQUAL(expected[i], SubmittedMessages[i].AsString());
        }
    }

    TStringBuf TMockChannelExecutor::TSubmittedMessage::AsString() const {
        const TBuffer& buffer = IncomingMessage.Batch->at(IncomingMessage.BatchIndex);
        return {buffer.Data(), buffer.Size()};
    }
}
