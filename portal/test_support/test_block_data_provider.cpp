#include "test_block_data_provider.h"

#include <portal/morda/blocks/core/session/session.h>

#include <util/stream/file.h>
#include <util/system/yassert.h>

#include <utility>

namespace NMordaBlocks {

    namespace NTest {

        class TTestBlockDataProvider::TSubscription : public IBlockDataProvider::ISubscription {
        public:
            TSubscription(TTestBlockDataProvider* provider, const TUri& dataId, IReceiver* receiver)
                : Provider_(provider)
                , DataId_(dataId)
                , Receiver_(receiver)
            {
                Provider_->SubscribeImpl(dataId, Receiver_);
            }

            TSubscription(TTestBlockDataProvider* provider, const TUri& dataId,
                          std::unique_ptr<IReceiver> receiver)
                : TSubscription(provider, dataId, receiver.get())
            {
                OwnedReceiver_= std::move(receiver);
            }

            ~TSubscription() override {
                Provider_->UnsubscribeImpl(DataId_, Receiver_);
            }

        private:
            TTestBlockDataProvider* Provider_;
            const TUri DataId_;
            std::unique_ptr<IReceiver> OwnedReceiver_;
            IReceiver* Receiver_;
        };

        TTestBlockDataProvider::TTestBlockDataProvider() = default;

        TTestBlockDataProvider::~TTestBlockDataProvider() = default;

        bool TTestBlockDataProvider::IsReady() const {
            return true;
        }

        void TTestBlockDataProvider::Start() {
            // Nothing.
        }

        void TTestBlockDataProvider::BeforeShutDown() {
            // Nothing.
        }
        void TTestBlockDataProvider::ShutDown() {
            // Nothing.
        }

        TString TTestBlockDataProvider::GetServiceName() const {
            return "TestBlockDataProvider";
        }

        std::unique_ptr<TTestBlockDataProvider::ISubscription>
        TTestBlockDataProvider::Subscribe(const TUri& dataId, IReceiver* receiver) {
            return std::make_unique<TSubscription>(this, dataId, receiver);
        }

        std::unique_ptr<TTestBlockDataProvider::ISubscription>
        TTestBlockDataProvider::Subscribe(const TUri& dataId, std::unique_ptr<IReceiver> receiver) {
            return std::make_unique<TSubscription>(this, dataId, std::move(receiver));
        }

        void TTestBlockDataProvider::SubscribeImpl(const TUri& uri, IReceiver* receiver) {
            Y_ASSERT(receiver);
            TSet<IReceiver*>& receivers = Subscriptions_[uri];
            Y_ASSERT(!receivers.contains(receiver));
            receivers.insert(receiver);
            SendDataIfNecessary(uri, receiver);
        }

        void TTestBlockDataProvider::UnsubscribeImpl(const TUri& uri, IReceiver* receiver) {
            Subscriptions_[uri].erase(receiver);
        }

        void TTestBlockDataProvider::SetData(const TUri& uri, TString data) {
            DataPerFile_[uri] = std::move(data);
            SendDataIfNecessary(uri);
        }

        void TTestBlockDataProvider::LoadDataFromFile(const TUri& uri, const TString& filePath) {
            SetData(uri, TFileInput(filePath).ReadAll());
        }

        void TTestBlockDataProvider::SendDataIfNecessary(const TUri& uri) {
            const auto dataIt = DataPerFile_.find(uri);
            if (dataIt == DataPerFile_.end())
                return;
            for (IReceiver* receiver : Subscriptions_[uri]) {
                std::unique_ptr<TSession> session;
                if (!TSession::HasCurrent())
                    session = std::make_unique<TSession>(true);
                receiver->OnDataLoaded(dataIt->second);
            }
        }

        void TTestBlockDataProvider::SendDataIfNecessary(const TUri& uri, IReceiver* receiver) {
            const auto dataIt = DataPerFile_.find(uri);
            if (dataIt == DataPerFile_.end())
                return;
            if (receiver) {
                std::unique_ptr<TSession> session;
                if (!TSession::HasCurrent())
                    session = std::make_unique<TSession>(true);
                receiver->OnDataLoaded(dataIt->second);
            }
        }

    } // namespace NTest

} // namespace NMordaBlocks
