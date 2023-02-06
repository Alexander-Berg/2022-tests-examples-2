#include "hyperworker_test_base.h"

#include "host_record.h"
#include "test_transaction.h"
#include "worker_test_base.h"
#include "url_record.h"
#include "ut_common.h"

#include <robot/samovar/algo/globaldata/globaldata.h>
#include <robot/samovar/algo/misc/basetime.h>
#include <robot/samovar/protos/ut.pb.h>

using namespace NSamovar;

using THyperWorkerCreator = std::function<NSamovar::THyperWorkerPtr()>;

namespace {

    struct TUtil: TSamovarWorkerTestBase {
        using TSamovarWorkerTestBase::ReadTestData;
        using TSamovarWorkerTestBase::CheckResult;
    };

    class THyperWorkerTest {
    public:
        using THosts = THashMap<THostKey, THostRecordPtr>;
        using TTestData = NSamovarTest::TTestData;

        THyperWorkerTest(THyperWorkerCreator ctor, const TTestData& input)
            : CreateWorker(std::move(ctor))
            , Input(input)
            , Hosts(CreateHosts(Input))
        {
        }

        TTestData Run() {
            return CombineGlobals(CombineHosts(CombineUrls(Input)));
        }

    private:
        static THashMap<THostKey, THostRecordPtr> CreateHosts(const TTestData& tables) {
            THashMap<THostKey, THostRecordPtr> ret;
            for (auto&& row : tables.GetHostDataTable()) {
                auto host = TryDeserialize(row);
                Y_ASSERT(host);
                ret[THostKey::CreateFromProto(row)] = std::move(host);
            }
            return ret;
        }

        TTestData CombineUrls(const TTestData& input) {
            auto urls = input.GetUrlDataTable();

            TTestData output = input;
            output.MutableUrlDataTable()->Clear();
            TTestTransaction tx(output);

            auto worker = CreateWorker();

            const THostRecord* host = nullptr;

            auto finishHost = [&]() {
                const TString data = worker->FinishHost(*host);
                if (!data) {
                    return;
                }

                auto& row = *output.MutableHostCombinatorTable()->Add();
                host->GetKey().ToProto(row);
                row.SetWorkerName(worker->GetName());
                row.SetData(data);
            };

            worker->Start();

            TMaybe<THostKey> prevHostKey;

            std::sort(urls.begin(), urls.end(),
                [](const NSamovarTest::TUrlDataRow& lhs, const NSamovarTest::TUrlDataRow& rhs) {
                    return TUrlKey::CreateFromProto(lhs) < TUrlKey::CreateFromProto(rhs);
                }
            );

            for (const auto& urlRow : urls) {
                TUrlRecordPtr url = TryDeserialize(urlRow);
                UNIT_ASSERT(url);

                const auto hostKey = url->GetKey().AsHostKey();

                if (!prevHostKey || *prevHostKey != hostKey) {
                    if (host) {
                        finishHost();
                    }

                    if (auto* ptr = Hosts.FindPtr(hostKey)) {
                        Y_ENSURE(ptr); // FIXME
                        host = &**ptr;
                    }

                    if (host) {
                        if (!worker->HostCondition(*host)) {
                            host = nullptr;
                        } else {
                            worker->StartHost(*host);
                        }
                    }
                }
                prevHostKey = hostKey;

                if (!host) {
                    continue;
                }

                url->Bind(*host);

                if (worker->UrlCondition(*url, *host)) {
                    auto& removed = tx.CurrentUrlRecordRemoved;
                    removed = false;
                    worker->DoPushUrl(*url, *host, tx); // FIXME What to do with DoPushUrlStable?
                    if (!removed) {
                        output.MutableUrlDataTable()->Add()->CopyFrom(AsRowProto(*url));
                    }
                }
            }

            if (host) {
                finishHost();
            }

            {
                const TString data = worker->Finish();
                if (worker->IsGlobalCombinator()) {
                    auto& row = *output.MutableGlobalCombinatorTable()->Add();
                    row.SetWorkerName(worker->GetName());
                    row.SetData(data);
                }
            }

            return output;
        }

        TTestData CombineHosts(const TTestData& input) {
            using namespace NSamovarSchema;

            auto combinators = input.GetHostCombinatorTable();
            std::sort(combinators.begin(), combinators.end(),
                [](const NSamovarSchema::TBoilerReduceHostCombinatorRow& lhs, const NSamovarSchema::TBoilerReduceHostCombinatorRow& rhs) {
                    return std::make_tuple(lhs.GetHostHash(), lhs.GetWorkerName()) < std::make_tuple(rhs.GetHostHash(), rhs.GetWorkerName());
                }
            );

            TTestData output = input;
            TTestTransaction tx(output);

            auto worker = CreateWorker();

            TMaybe<THostKey> prevHostKey;
            const THostRecord* host = nullptr;
            NSamovarData::TPushData hostPush;

            for (const auto& row : combinators) {
                Y_ENSURE(row.GetWorkerName() == worker->GetName());

                const auto hostKey = THostKey{row.GetHostHash()};

                if (!prevHostKey || *prevHostKey != hostKey) {
                    if (host) {
                        worker->FinishCombineHost(*host, tx, hostPush);
                        if (hostPush.HasData()) {
                            tx.WritePush(std::move(hostPush));
                        }
                    }

                    if (auto* ptr = Hosts.FindPtr(hostKey)) {
                        Y_ENSURE(ptr); // FIXME
                        host = &**ptr;
                    }

                    if (host) {
                        hostPush = host->CreateEmptyPush();
                        worker->StartCombineHost(*host);
                    }
                }
                prevHostKey = hostKey;

                if (!host) {
                    continue;
                }

                worker->PushHostCombineData(*host, row.GetData());
            }

            if (host) {
                worker->FinishCombineHost(*host, tx, hostPush);
                if (hostPush.HasData()) {
                    tx.WritePush(std::move(hostPush));
                }
            }

            return output;
        }

        TTestData CombineGlobals(const TTestData& input) {
            using namespace NSamovarSchema;

            auto combinators = input.GetGlobalCombinatorTable();
            std::sort(combinators.begin(), combinators.end(),
                [](const NSamovarSchema::TBoilerReduceGlobalCombinatorRow& lhs, const NSamovarSchema::TBoilerReduceGlobalCombinatorRow& rhs) {
                    return lhs.GetWorkerName() < rhs.GetWorkerName();
                }
            );

            TTestData output = input;
            TTestTransaction tx(output);

            auto worker = CreateWorker();

            if (!worker->IsGlobalCombinator()) {
                return output;
            }

            THolder<IGlobalDataBase> globalData(worker->CreateGlobalData());
            globalData->Start(); // FIXME Only if has rows?

            for (const auto& row : combinators) {
                Y_ENSURE(row.GetWorkerName() == worker->GetName());

                globalData->PushData(row.GetData());
            }

            const TString data = globalData->Finish();
            if (data) {
                auto& row = *output.MutableGlobalDataTable()->Add();
                row.SetWorkerName(worker->GetName());
                row.MutableData()->SetData(data);
            }

            return output;
        }

    private:
        THyperWorkerCreator CreateWorker;
        const TTestData& Input;
        THosts Hosts;
    };

}

namespace NSamovarTest {
    void RunHyperWorkerTest(const TString& inputStr, const TString& expected, THyperWorkerCreator ctor) {
        const auto input = TUtil::ReadTestData(inputStr);

        if (input.HasTestTime()) {
            SetTestTime(input.GetTestTime());
        }

        const auto got = THyperWorkerTest(std::move(ctor), input).Run();
        //Cerr << got.DebugString() << '\n';
        TUtil::CheckResult(expected, got);
    }
}
