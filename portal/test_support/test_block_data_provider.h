#pragma once

#include <portal/morda/blocks/services/data_provider/block_data_provider.h>


#include <util/generic/map.h>
#include <util/generic/set.h>

#include <utility>

namespace NMordaBlocks {
    namespace NTest {

        class TTestBlockDataProvider : public IBlockDataProvider {
        public:
            TTestBlockDataProvider();
            ~TTestBlockDataProvider() override;

            // IBlockDataProvider overrides:
            std::unique_ptr<ISubscription> Subscribe(const TUri& dataId,
                                                     IReceiver* receiver) override;
            std::unique_ptr<ISubscription> Subscribe(const TUri& dataId,
                                                     std::unique_ptr<IReceiver> receiver) override;

            void SetData(const TUri& uri, TString data);
            void LoadDataFromFile(const TUri& uri,const TString& filePath);

            // IService overrides:
            bool IsReady() const override;
            void Start() override;
            void BeforeShutDown() override;
            void ShutDown() override;
            TString GetServiceName() const override;

        private:
            class TSubscription;
            void SendDataIfNecessary(const TUri& uri);
            void SendDataIfNecessary(const TUri& uri, IReceiver* receiver);
            void SubscribeImpl(const TUri& dataId, IReceiver* receiver);
            void UnsubscribeImpl(const TUri& dataId, IReceiver* receiver);

            TMap<TUri, TSet<IReceiver*>> Subscriptions_;
            TMap<TString, TString> DataPerFile_;
        };

    } // namespace NTest

} // namespace NMordaBlocks
