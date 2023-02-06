#include <robot/rthub/impl/counters.h>

#include <library/cpp/testing/unittest/registar.h>
#include <library/cpp/protobuf/util/pb_io.h>

using namespace NRTHub;
using namespace NMonitoring;
using namespace NRobot;
using namespace std::chrono;

class TCountersTest: public TTestBase {
private:
    UNIT_TEST_SUITE(TCountersTest);
    UNIT_TEST(TestSimple);
    UNIT_TEST(TestApplyCustomStatisticsBeforeSharedCountersAtSerializeStage);
    UNIT_TEST(TestRandomSample);
    UNIT_TEST(CanUpdateManyCounters);
    UNIT_TEST(TestUpdateCountersWithoutMergeData);
    UNIT_TEST(TestProcessCounters);
    UNIT_TEST(TestCanUpdateTopLevelCounters);
    UNIT_TEST(TestApplyMergeStageWhenDataToMergeIsEmpty);
    UNIT_TEST(TestStripStaleCounters);
    UNIT_TEST(TestKeepAllSourceCounters);
    UNIT_TEST(TestDynamicCounters);
    UNIT_TEST_SUITE_END();

public:
    void TestSimple() {
        TRTHubCounters serverCounters;

        TRTHubCounters slave1Counters;
        TRTHubCounters slave2Counters;
        TRTHubCounters slave3Counters;

        {
            const auto started = TSteadyClock::Now();
            TDurationCounter::TScope scope(slave1Counters.Channels.GetOrCreateByName("WebPages").YqlTotalProcessDuration,
                                           started);
            scope.SetFinishedAt(started + 10ms);
        }
        {
            const auto started = TSteadyClock::Now();
            TDurationCounter::TScope scope(slave2Counters.Channels.GetOrCreateByName("WebPages").YqlTotalProcessDuration,
                                           started);
            scope.SetFinishedAt(started + 20ms);
        }
        {
            const auto started = TSteadyClock::Now();
            TDurationCounter::TScope scope(slave3Counters.Channels.GetOrCreateByName("WebPages").YqlTotalProcessDuration,
                                           started);
            scope.SetFinishedAt(started + 30ms);
        }

        TVector<TString> mergeData;
        mergeData.push_back(SerializeCountersState(slave1Counters));
        mergeData.push_back(SerializeCountersState(slave2Counters));
        mergeData.push_back(SerializeCountersState(slave3Counters));
        Merge(serverCounters, mergeData);

        const auto& serverCounter = serverCounters.Channels.GetOrCreateByName("WebPages")
                .GetCounter("YqlTotalProcessDuration", true);
        UNIT_ASSERT_VALUES_EQUAL(60000, serverCounter->Val());
    }

    void TestApplyCustomStatisticsBeforeSharedCountersAtSerializeStage() {
        TRTHubCounters serverCounters;

        TVector<TString> mergeData;
        {
            TRTHubCounters slaveCounters;
            {
                TSubscriberTopicCounters& slaveSubscriberCounters = slaveCounters.Subscribers.GetOrCreateByName("zora--pages");
                const auto now = TSteadyClock::Now();
                TDurationCounter::TScope scope(slaveSubscriberCounters.OnDataItemDuration, now);
                scope.SetFinishedAt(now + 10us);
            }
            mergeData.push_back(SerializeCountersState(slaveCounters));
        }
        {
            TRTHubCounters slaveCounters;
            {
                TSubscriberTopicCounters& slaveSubscriberCounters = slaveCounters.Subscribers.GetOrCreateByName("zora--pages");
                const auto now = TSteadyClock::Now();
                TDurationCounter::TScope scope(slaveSubscriberCounters.OnDataItemDuration, now);
                scope.SetFinishedAt(now + 100us);
            }
            mergeData.push_back(SerializeCountersState(slaveCounters));
        }

        Merge(serverCounters, mergeData);

        TDeprecatedCounter& serverCounter = *serverCounters.Subscribers.GetOrCreateByName("zora--pages").GetCounter("OnDataItemDuration", true);
        UNIT_ASSERT_VALUES_EQUAL(serverCounter.Val(), 110);
    }

    void TestRandomSample() {
        TRTHubCounters serverCounters;

        TVector<TString> mergeData;
        {
            TRTHubCounters slaveCounters;
            {
                TChannelCounters& slaveChannelCounters = slaveCounters.Channels.GetOrCreateByName("WebPages");
                slaveChannelCounters.InputCounters.GetOrCreateByName("zora--pages").InputMessageSize = 100;
            }
            mergeData.push_back(SerializeCountersState(slaveCounters));
        }
        {
            TRTHubCounters slaveCounters;
            {
                TChannelCounters& slaveChannelCounters = slaveCounters.Channels.GetOrCreateByName("WebPages");
                slaveChannelCounters.InputCounters.GetOrCreateByName("zora--pages").InputMessageSize = 200;
            }
            mergeData.push_back(SerializeCountersState(slaveCounters));
        }

        Merge(serverCounters, mergeData);

        TDeprecatedCounter& serverCounter = serverCounters.Channels.GetOrCreateByName("WebPages")
                .InputCounters.GetOrCreateByName("zora--pages").InputMessageSize;
        UNIT_ASSERT(serverCounter.Val() == 100 || serverCounter.Val() == 200);
    }

    void CanUpdateManyCounters() {
        TRTHubCounters serverCounters;

        TVector<TString> mergeData;
        {
            TRTHubCounters slaveCounters;
            {
                TChannelCounters& slaveChannelCounters = slaveCounters.Channels.GetOrCreateByName("WebPages");
                slaveChannelCounters.InputCounters.GetOrCreateByName("zora--pages").TooBigInputMessagesCount = 10;
                {
                    const auto start = TSteadyClock::Now();
                    const auto duration = slaveChannelCounters.YqlTotalProcessDuration.Begin(start);
                    slaveChannelCounters.YqlTotalProcessDuration.End(duration, start + 20ms);
                }
            }
            mergeData.push_back(SerializeCountersState(slaveCounters));
        }
        {
            TRTHubCounters slaveCounters;
            {
                TChannelCounters& slaveChannelCounters = slaveCounters.Channels.GetOrCreateByName("WebPages");
                slaveChannelCounters.InputCounters.GetOrCreateByName("zora--pages").TooBigInputMessagesCount = 100;
                {
                    const auto start = TSteadyClock::Now();
                    const auto duration = slaveChannelCounters.YqlTotalProcessDuration.Begin(start);
                    slaveChannelCounters.YqlTotalProcessDuration.End(duration, start + 200ms);
                }
            }
            mergeData.push_back(SerializeCountersState(slaveCounters));
        }

        Merge(serverCounters, mergeData);

        TChannelCounters& serverChannelCounters = serverCounters.Channels.GetOrCreateByName("WebPages");
        UNIT_ASSERT_VALUES_EQUAL(serverChannelCounters.InputCounters.GetOrCreateByName("zora--pages").TooBigInputMessagesCount.Val(), 110);
        UNIT_ASSERT_VALUES_EQUAL(serverChannelCounters.GetCounter("YqlTotalProcessDuration")->Val(), 220000);
    }

    void TestUpdateCountersWithoutMergeData() {
        TRTHubCounters serverCounters;

        TVector<TString> mergeData;
        {
            TRTHubCounters slaveCounters;
            {
                TChannelCounters& slaveChannelCounters = slaveCounters.Channels.GetOrCreateByName("WebPages");
                slaveChannelCounters.InputCounters.GetOrCreateByName("zora--pages").TooBigInputMessagesCount = 10;
            }
            mergeData.push_back(SerializeCountersState(slaveCounters));
        }
        {
            TSubscriberTopicCounters& serverSubscriberCounters = serverCounters.Subscribers.GetOrCreateByName("zora--pages");
            const auto now = TSteadyClock::Now();
            TDurationCounter::TScope scope(serverSubscriberCounters.OnDataItemDuration, now);
            scope.SetFinishedAt(now + 456us);
        }

        Merge(serverCounters, mergeData);

        TChannelCounters& serverChannelCounters = serverCounters.Channels.GetOrCreateByName("WebPages");
        UNIT_ASSERT_VALUES_EQUAL(serverChannelCounters.InputCounters.GetOrCreateByName("zora--pages").TooBigInputMessagesCount.Val(), 10);

        TSubscriberTopicCounters& serverSubscriberCounters = serverCounters.Subscribers.GetOrCreateByName("zora--pages");
        UNIT_ASSERT_VALUES_EQUAL(serverSubscriberCounters.GetCounter("OnDataItemDuration", true)->Val(), 456);
    }

    void TestProcessCounters() {
        TRTHubCounters serverCounters;

        TVector<TString> mergeData;
        {
            TRTHubCounters slaveCounters;
            {
                TChannelCounters& channelCounters = slaveCounters.Channels.GetOrCreateByName("WebPages");
                const auto now = TSteadyClock::Now();
                channelCounters.Yql.Process.AddDuration(now, now + 10us, true);
            }
            mergeData.push_back(SerializeCountersState(slaveCounters));
        }
        {
            TRTHubCounters slaveCounters;
            {
                TChannelCounters& channelCounters = slaveCounters.Channels.GetOrCreateByName("WebPages");
                const auto now = TSteadyClock::Now();
                channelCounters.Yql.Process.AddDuration(now, now + 1000us, false);
            }
            mergeData.push_back(SerializeCountersState(slaveCounters));
        }

        Merge(serverCounters, mergeData);

        TChannelCounters& serverChannelCounters = serverCounters.Channels.GetOrCreateByName("WebPages");
        UNIT_ASSERT_VALUES_EQUAL(serverChannelCounters.GetCounter("ChannelYqlProcessAverage", true)->Val(), 505);
        UNIT_ASSERT_VALUES_EQUAL(serverChannelCounters.GetCounter("ChannelYqlProcessErrorsRate", true)->Val(), 1);
    }

    void TestCanUpdateTopLevelCounters() {
        TRTHubCounters serverCounters;
        Merge(serverCounters, TVector<TString>());
        UNIT_ASSERT(serverCounters.CountersCount.Val() > 0);
    }

    void TestApplyMergeStageWhenDataToMergeIsEmpty() {
        TRTHubCounters counters;

        TChannelOutputShardCounters& outputCounters = counters.ChannelOutputs
                .GetOrCreateByName("JupiterPageExport")
                .GetOrCreateByName("rthub--jupiter");
        const auto now = TSteadyClock::Now();
        outputCounters.Send.AddDuration(now, now + 10us, true);

        Merge(counters, TVector<TString>());

        UNIT_ASSERT_VALUES_EQUAL(outputCounters.GetCounter("SendMax")->Val(), 10);
    }

    void TestStripStaleCounters() {
        TRTHubCounters serverCounters;

        TCountersMerger merger(serverCounters, 1);
        {
            TRTHubCounters slaveCounters;
            slaveCounters.Channels.GetOrCreateByName("WebPages").SlowestMessageDurationMillis = 10;
            merger.AddState(SerializeCountersState(slaveCounters), 0);
        }
        {
            TRTHubCounters slaveCounters;
            slaveCounters.Channels.GetOrCreateByName("WebPages").SlowestMessageDurationMillis = 20;
            merger.AddState(SerializeCountersState(slaveCounters), 0);
        }
        merger.Merge();

        UNIT_ASSERT_VALUES_EQUAL(serverCounters.Channels.GetOrCreateByName("WebPages").SlowestMessageDurationMillis, 20);
    }

    void TestKeepAllSourceCounters() {
        TRTHubCounters serverCounters;

        TCountersMerger merger(serverCounters, 1);
        {
            TRTHubCounters slaveCounters;
            {
                TChannelCounters& channelCounters = slaveCounters.Channels.GetOrCreateByName("WebPages");
                const auto now = TSteadyClock::Now();
                channelCounters.Yql.Process.AddDuration(now, now + 10us, true);
            }
            merger.AddState(SerializeCountersState(slaveCounters), 0);
        }
        {
            TRTHubCounters slaveCounters;
            {
                TChannelCounters& channelCounters = slaveCounters.Channels.GetOrCreateByName("WebPages");
                const auto now = TSteadyClock::Now();
                channelCounters.Yql.Process.AddDuration(now, now + 1000us, false);
            }
            merger.AddState(SerializeCountersState(slaveCounters), 0);
        }

        merger.Merge();

        TChannelCounters& serverChannelCounters = serverCounters.Channels.GetOrCreateByName("WebPages");
        UNIT_ASSERT_VALUES_EQUAL(serverChannelCounters.GetCounter("ChannelYqlProcessAverage", true)->Val(), 505);
        UNIT_ASSERT_VALUES_EQUAL(serverChannelCounters.GetCounter("ChannelYqlProcessErrorsRate", true)->Val(), 1);
    }

    void TestDynamicCounters() {
        TRTHubCounters serverCounters;

        TCountersMerger merger(serverCounters, 1);
        {
            TRTHubCounters slaveCounters;
            {
                TDeprecatedCounter& counter = slaveCounters.CreateCounter("Timeouts", true, ECountersMergeScheme::Sum, 1.0, true);
                counter = 10;
            }
            merger.AddState(SerializeCountersState(slaveCounters), 0);
        }
        {
            TRTHubCounters slaveCounters;
            {
                TDeprecatedCounter& counter = slaveCounters.CreateCounter("Timeouts", true, ECountersMergeScheme::Sum, 1.0, true);
                counter = 20;
            }
            merger.AddState(SerializeCountersState(slaveCounters), 0);
        }

        merger.Merge();

        UNIT_ASSERT_VALUES_EQUAL(serverCounters.GetCounter("Timeouts", true)->Val(), 30);
    }

private:
    void Merge(TCountersGroup& counters, const TVector<TString>& data) {
        TCountersMerger merger(counters, data.size());
        for (size_t i = 0; i < data.size(); ++i) {
            merger.AddState(data[i], i);
        }
        merger.Merge();
    }
};

UNIT_TEST_SUITE_REGISTRATION(TCountersTest);
