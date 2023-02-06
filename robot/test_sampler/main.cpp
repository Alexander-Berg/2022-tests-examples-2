#include <ads/bsyeti/big_rt/lib/consuming_system/consuming_system.h>
#include <ads/bsyeti/big_rt/lib/supplier/supplier.h>
#include <ads/bsyeti/big_rt/lib/processing/shard_processor/stateless/processor.h>

#include <ads/bsyeti/big_rt/lib/utility/logging/logging.h>
#include <ads/bsyeti/big_rt/lib/queue/qyt/queue.h>
#include <ads/bsyeti/libs/pb_arg_entry_point/entry_point.h>
#include <ads/bsyeti/libs/tpqlib_bridges/tpqlib_bridges.h>

#include <kernel/yt/dynamic/client.h>
#include <robot/mirror/tools/test_sampler/proto/config.pb.h>
#include <yt/yt/core/misc/shutdown.h>

using namespace NBigRT;

namespace {
    class TWorkerProcessor : public TStatelessShardProcessor {
    public:
        TWorkerProcessor(TStatelessShardProcessor::TConstructionArgs args, TString path, TString cluster)
            : TStatelessShardProcessor(args),
            Queue(path, NYT::NApi::CreateClient(cluster)),
            ShardsCnt(Queue.GetShardCount().Get().ValueOrThrow()) {}
    
    private:
        TVector<TYtQueue::TWriteRow> RowsToWrite;
        TYtQueue Queue;
        ui64 ShardsCnt;

    private:
        void Process(TString dataSource, TMessageBatch messageBatch) final {
            Y_UNUSED(dataSource);
            for (auto& message : messageBatch.Messages) {
                if (!message.Unpack())
                    continue;
                
                RowsToWrite.push_back({
                    .Shard = RandomNumber(ShardsCnt),
                    .CompressedRow = message.Data
                });
            }
        }

        NYT::TFuture<TPrepareForAsyncWriteResult> PrepareForAsyncWrite() final {
            auto rows = std::move(RowsToWrite);
            RowsToWrite.clear();
            return NYT::MakeFuture<TPrepareForAsyncWriteResult>({
                .AsyncWriter = [this, &rows](NYT::NApi::ITransactionPtr tx) {
                    Queue.Write(tx, std::move(rows));
                }
            });
        }
    };

    void Run(const TSamplerConfig &config, NBSYeti::TStopToken stopToken) {
        const auto ytClientPool = NYTEx::CreateTransactionKeeper(TDuration::Zero());
        auto inflightLimiter = NYT::New<TInflightLimiter>(config.GetMaxInflightBytes());

        NBSYeti::TTvmManagerPtr tvmManager{config.HasTvmConfig() ? NBSYeti::CreateTvmManager(config.GetTvmConfig()) : NBSYeti::TTvmManagerPtr{}};
        NPersQueue::TPQLibSettings lbPqLibSettings;
        lbPqLibSettings.ThreadsCount = 20;
        lbPqLibSettings.GRpcThreads = 20;
        lbPqLibSettings.ChannelCreationTimeout = TDuration::Seconds(10);
        lbPqLibSettings.DefaultLogger = new TTPQLibGlobalLogBridge();
        NPersQueue::TPQLib lbPqLib(lbPqLibSettings);

        const auto service = CreateConsumingSystem({
            .Config = config.GetConsumer(),
            .SuppliersProvider = CreateSupplierFactoriesProvider({
                .ConfigsRepeated = config.GetSuppliers(),
                .TvmManager = tvmManager,
                .LbPqLib = &lbPqLib,
            }),
            .YtClients = ytClientPool,
            .ShardsProcessor = [ytClientPool, inflightLimiter, &config](TConsumingSystem::IConsumer &consumer) {
                TWorkerProcessor {
                    TStatelessShardProcessor::TConstructionArgs {
                        .Consumer = consumer,
                        .Config = config.GetShardProcessorConfig(),
                        .TransactionKeeper = ytClientPool,
                        .InflightLimiter = inflightLimiter,
                    },
                    config.GetYtPath(),
                    config.GetYtCluster()
                }.Run();
            }
        });
        service->Run();

        stopToken.Wait();

        service->Stop().Get();
    }
        
    int Main(const TSamplerConfig& config, NBSYeti::TStopToken stopToken) {
        DoInitThreadAwareGlobalLog(config.GetGlobalLog(), static_cast<ELogPriority>(config.GetGlobalLogVerbosity()));
        DoInitYtLog(config.GetYtLog(), config.GetYtLogVerbosity());

        Run(config, stopToken);

        NYT::Shutdown();
        return 0;
    }

} // namespace

int main(int argc, const char *argv[]) {
    return TPbArgEntryPoint::RunPbArgMain(&Main, argc, argv);
}
