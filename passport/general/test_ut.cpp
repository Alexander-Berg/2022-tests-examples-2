#include <passport/infra/libs/cpp/logbroker/reader/reader.h>
#include <passport/infra/libs/cpp/logbroker/reader/impl/reader_impl.h>

#include <passport/infra/libs/cpp/logbroker/processing/reader_pool.h>

#include <kikimr/persqueue/sdk/deprecated/cpp/v2/persqueue.h>

#include <library/cpp/testing/unittest/registar.h>

#include <util/stream/file.h>

#include <vector>

using namespace NPassport::NLb;

template <>
void Out<NPassport::NLb::TChunk>(IOutputStream& o, const NPassport::NLb::TChunk& value) {
    o << "file -> " << value.Meta.File << Endl
      << "server -> " << value.Meta.Server << Endl
      << "ts -> " << value.Meta.CreateTime.ToString() << Endl
      << "data -> " << value.Data;
}

Y_UNIT_TEST_SUITE(LB) {
    static const TString TOPIC = "default-topic";
    static const TString DATA = "some_data\n";
    static const TString FILENAME = "some_file";
    static const TString SERVER = "some_server";
    static const size_t DATA_COUNT = 1000;

    ui16 GetPort() {
        TFileInput port("ydb_endpoint.txt");
        return IntFromString<ui16, 10>(port.ReadLine());
    }

    void WriteData() {
        NPersQueue::TPQLib pq;

        NPersQueue::TProducerSettings prodSets;
        prodSets.Topic = TOPIC;
        prodSets.SourceId = "qwerty";
        prodSets.Server.Address = "localhost";
        prodSets.Server.Port = GetPort();
        prodSets.ExtraAttrs.emplace("file", FILENAME);
        prodSets.ExtraAttrs.emplace("server", SERVER);

        THolder<NPersQueue::IProducer> prod = pq.CreateProducer(prodSets, new TLogger(9));
        NThreading::TFuture<NPersQueue::TProducerCreateResponse> fut = prod->Start(TDuration::Seconds(20));
        UNIT_ASSERT(fut.Wait(TDuration::Seconds(30)));
        UNIT_ASSERT_C(!fut.GetValueSync().Response.HasError(),
                      fut.GetValueSync().Response.GetError().GetDescription());

        size_t total = 0;
        for (size_t idx = 0; idx < DATA_COUNT; ++idx) {
            NThreading::TFuture<NPersQueue::TProducerCommitResponse> f = prod->Write(DATA);
            UNIT_ASSERT_C(f.Wait(TDuration::Seconds(60)), idx);

            UNIT_ASSERT_C(!f.GetValueSync().Response.HasError(),
                          f.GetValueSync().Response.GetError().GetDescription());
            total += DATA.size();
        }

        Cerr << "=== total bytes written: " << total << Endl;
    }

    Y_UNIT_TEST(test) {
        WriteData();

        TReaderSettings sets;
        sets.Topics = {TOPIC};
        sets.ClientId = "qwerty2";
        sets.ServerName = "localhost";
        sets.ServerPort = GetPort();

        std::atomic<size_t> total = 0;
        std::unique_ptr<TReaderThread> r = std::make_unique<TReaderThread>(sets);
        r->StartLoop([&total, &r](TData&& data, NThreading::TPromise<void>) -> void {
            for (const TTopicData& d : data.Messages) {
                Cerr << "=== rows read: " << d.Data.size() << Endl;
                if (!d.Topic.Contains(TOPIC)) {
                    Cerr << "=== topic is bad: " << d.Topic << Endl;
                    r->StopLoop();
                    break;
                }

                for (const TChunk& tmp : d.Data) {
                    if (tmp.Data != DATA ||
                        tmp.Meta.File != FILENAME ||
                        tmp.Meta.Server != SERVER ||
                        (TInstant::Now() > tmp.Meta.CreateTime + TDuration::Minutes(10)) ||
                        (TInstant::Now() < tmp.Meta.CreateTime - TDuration::Minutes(10)))
                    {
                        Cerr << "s='" << tmp << "'" << Endl;
                        r->StopLoop();
                        break;
                    }

                    total += tmp.Data.size();
                }

                if (total >= DATA_COUNT * DATA.size()) {
                    r->StopLoop();
                }
            }
        });

        for (int idx = 0; total < DATA_COUNT * DATA.size() && idx < 60; ++idx) {
            Cerr << "=== total bytes read: " << total.load() << Endl;
            Sleep(TDuration::Seconds(1));
        }
        r.reset();

        Cerr << "=== no time to wait" << Endl;

        UNIT_ASSERT_VALUES_EQUAL(total.load(), DATA_COUNT* DATA.size());
    }
}
