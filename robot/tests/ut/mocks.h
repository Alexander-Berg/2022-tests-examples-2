#pragma once

#include <robot/rthub/impl/channel.h>
#include <robot/rthub/impl/channel_output.h>
#include <robot/rthub/impl/channels_pool.h>

namespace NRTHub {
    struct TMockChannelExecutor final: public IChannelExecutor {
        TFuture<TVector<TIoOperation>> Submit(TIncomingMessage&& message) noexcept override;

        struct TSubmittedMessage {
            TIncomingMessage IncomingMessage;
            TPromise<TVector<TIoOperation>> Promise;

            TStringBuf AsString() const;
        };

        void CompleteAll();

        void CompleteAll(const TVector<TString>& expected);

        void CheckAll(const TVector<TString>& expected) const;

        TVector<TSubmittedMessage> SubmittedMessages;
    };
}
