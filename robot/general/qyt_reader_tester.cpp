#include "qyt_reader_tester.h"
#include <util/generic/utility.h>

namespace NMercury {

    namespace {
        NLogging::TMLogger MLogger("TQytReaderTester");

        constexpr auto TabletsCount = 50;
        constexpr auto SkippedTablet = TQytTabletIndex(3);

        TVector<TQytTabletIndex> GenerateTabletRange(ui32 size, ui32 firstElement = 0) {
            auto result = TVector<TQytTabletIndex>(Reserve(size));
            auto currentTabletIndex = TQytTabletIndex(firstElement);
            for (ui32 i = 0; i < size; ++i) {
                result.push_back(currentTabletIndex);
                ++currentTabletIndex.Value;
            }
            return result;
        }

        TVector<TShuffledRow> GenerateTabletRows(TQytTabletIndex tabletIndex, ui64 rowCount) {
            auto result = TVector<TShuffledRow>(rowCount);
            for (auto& shuffledRow : result) {
                shuffledRow.SetTabletIndex(tabletIndex.Value);
                shuffledRow.SetData("test data");
            }
            return result;
        }

        TQytReaderConfig GetTestQytReaderConfig() {
            auto result = TQytReaderConfig();
            result.MutableCommitterConfig()->SetTabletTrimInterval(1000000);
            result.MutableCommitterConfig()->SetTabletTrimThreshold(3000);
            result.MutableQytTabletQueueConfig()->SetStarvingTabletCooldownMs(2000);
            return result;
        }

        TMaybe<ui64> ReadFirstRowIndex(const TQueueTable& table, TQytTabletIndex tabletIndex) {
            const auto readQuery = Sprintf("* FROM [$(this)] WHERE [$tablet_index] = %u LIMIT 1", tabletIndex.Value);
            const auto rows = table.SelectRows(readQuery).Rowset;
            return rows.empty() ? Nothing() : TMaybe<ui64>(rows.front().GetRowIndex());
        }
    }

    TTabletData::TTabletData(TQytTabletIndex tabletIndex)
        : TabletIndex(tabletIndex)
        , Randomizer(tabletIndex.Value)
    {
        if (TabletIndex != SkippedTablet) {
            ReadFlags.resize(Randomizer.Uniform(50000, 100000));
        }

        MLOG_INFO("Created tablet %v with row count %v", TabletIndex.Value, ReadFlags.size());
    }

    bool TTabletData::PushDataToTable(const TQueueTable& table) {
        if (NextPushIndex >= ReadFlags.size()) {
            return false;
        }

        const ui32 remainingCount = ReadFlags.size() - NextPushIndex;
        const ui32 pushCount = Min(Randomizer.Uniform(100, 5000), remainingCount);
        table.WriteRows(GenerateTabletRows(TabletIndex, pushCount));
        MLOG_INFO("Pushed %v rows to tablet %v", pushCount, TabletIndex.Value);
        NextPushIndex += pushCount;
        return true;
    }

    void TTabletData::MarkAsRead(ui64 index) {
        Y_ENSURE(index < ReadFlags.size(), "Read non existing row index " << index << " from tablet " << TabletIndex.Value);
        Y_ENSURE(!ReadFlags[index], "Row " << index << " is read twice from tablet " << TabletIndex.Value);
        ReadFlags[index] = true;
    }

    void TTabletData::AssertAllRead() const {
        for (ui64 index = 0; index < ReadFlags.size(); ++index) {
            Y_ENSURE(ReadFlags[index], "Row index " << index << " is not read in tablet " << TabletIndex.Value);
        }
    }

    TQytReaderTester::TQytReaderTester(TQueueTable queueTable)
        : Table(std::move(queueTable))
        , Tablets(Reserve(TabletsCount))
    {
        for (ui32 tabletIndex = 0; tabletIndex < TabletsCount; ++tabletIndex) {
            Tablets.push_back(TTabletData(TQytTabletIndex(tabletIndex)));
        }
    }

    void TQytReaderTester::Prepare() {
        Table.Reshard(TabletsCount);
        Table.Mount();
        QytReader = MakeHolder<TQytReader<TShuffledRow>>(Table, GetTestQytReaderConfig(), TQytReaderCounters());
    }

    void TQytReaderTester::Run() {
        constexpr auto firstTabletsPortion = 17;
        QytReader->UpdateOwnedTablets(GenerateTabletRange(firstTabletsPortion), {});
        QytReader->UpdateOwnedTablets(GenerateTabletRange(TabletsCount - firstTabletsPortion, firstTabletsPortion), {SkippedTablet});

        const auto thread1 = SystemThreadFactory()->Run([this]() { ReadThreadEntry(1); });
        const auto thread2 = SystemThreadFactory()->Run([this]() { ReadThreadEntry(2); });
        const auto thread3 = SystemThreadFactory()->Run([this]() { ReadThreadEntry(3); });

        PushDataToTablets();

        thread1->Join();
        thread2->Join();
        thread3->Join();
    }

    void TQytReaderTester::Assert() {
        for (ui32 tabletIndex = 0; tabletIndex < Tablets.size(); ++tabletIndex) {
            Tablets[tabletIndex].AssertAllRead();

            const auto rowIndexInTable = ReadFirstRowIndex(Table, TQytTabletIndex(tabletIndex)).GetOrElse(1);
            Y_ENSURE(rowIndexInTable > 0, "Tablet " << tabletIndex << " was not trimmed");
        }
    }

    void TQytReaderTester::PushDataToTablets() {
        auto nonFinishedTablets = GenerateTabletRange(TabletsCount);

        auto randomizer = TRandomizer(424253);
        while (!nonFinishedTablets.empty()) {
            const auto& tabletIndex = nonFinishedTablets[randomizer.Uniform(nonFinishedTablets.size())];
            if (!Tablets[tabletIndex.Value].PushDataToTable(Table)) {
                nonFinishedTablets.erase(&tabletIndex);
            }
            Sleep(TDuration::MilliSeconds(10));
        }

        const auto tabletCooldownMs = GetTestQytReaderConfig().GetQytTabletQueueConfig().GetStarvingTabletCooldownMs();
        AtomicSet(StopReadingTs, TInstant::Now().MilliSeconds() + tabletCooldownMs);
    }

    void TQytReaderTester::ReadThreadEntry(ui32 threadId) {
        TVector<TQytReadConfirmation> confirmations;
        TVector<TShuffledRow> data;

        auto commit = [&]() {
            QytReader->Commit(confirmations);
            TGuard<TMutex> lock(Mutex);
            for (const auto& shuffledRow : data) {
                Tablets[shuffledRow.GetTabletIndex()].MarkAsRead(shuffledRow.GetRowIndex());
            }
        };

        auto randomizer = TRandomizer(threadId);
        while (true) {
            const auto startTime = TInstant::Now();
            const auto deadline = startTime + TDuration::Seconds(10);
            try {
                const auto readResult = QytReader->Read(randomizer.Uniform(100, 500), deadline);
                confirmations.push_back(readResult.Confirmation);
                data.insert(data.end(), readResult.Data.cbegin(), readResult.Data.cend());
            } catch (const TQytNoAvailableTabletsException&) {
                if (TInstant::MilliSeconds(AtomicGet(StopReadingTs)) < startTime) {
                    break;
                }
                Sleep(TDuration::Seconds(1));
                continue;
            }

            if (randomizer.Uniform(5) == 0) {
                if (randomizer.Uniform(2) == 0) {
                    commit();
                } else {
                    QytReader->Rollback(confirmations);
                }

                confirmations.clear();
                data.clear();
            }
        }

        commit();
        MLOG_INFO("Thread %v has finished", threadId);
    }

}
