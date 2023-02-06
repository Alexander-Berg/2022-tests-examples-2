#include <robot/mercury/library/qyt_reader/qyt_reader.h>
#include <robot/mercury/protos/shuffled_row.pb.h>
#include <util/random/mersenne.h>

namespace NMercury {

    using TQueueTable = NYT::NProtoApi::TTable<TShuffledRow>;
    using TRandomizer = TMersenne<ui32>;

    class TTabletData {
    public:
        explicit TTabletData(TQytTabletIndex tabletIndex);
        bool PushDataToTable(const TQueueTable& table);
        void MarkAsRead(ui64 index);
        void AssertAllRead() const;
    private:
        TQytTabletIndex TabletIndex;
        ui32 NextPushIndex = 0;
        TVector<bool> ReadFlags;
        TRandomizer Randomizer;
    };

    class TQytReaderTester {
    public:
        TQytReaderTester(TQueueTable queueTable);
        void Prepare();
        void Run();
        void Assert();
    private:
        void PushDataToTablets();
        void ReadThreadEntry(ui32 threadId);
    private:
        TQueueTable Table;
        TVector<TTabletData> Tablets;
        THolder<TQytReader<TShuffledRow>> QytReader;
        TMutex Mutex;
        TAtomic StopReadingTs = TInstant::Max().Seconds();
    };

}
