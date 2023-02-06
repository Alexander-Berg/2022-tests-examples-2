#include "adapter_test.h"

#include <robot/library/oxygen/indexer/output/adapter/adapter.h>

#include <yweb/robot/kiwi/tuplelib/lib/object.h>

#include <library/cpp/testing/unittest/registar.h>

#include <util/system/env.h>
#include <util/generic/map.h>
#include <util/generic/hash.h>
#include <util/random/mersenne.h>
#include <util/random/random.h>
#include <util/string/cast.h>
#include <util/string/printf.h>

namespace {

using namespace NOxygen;

// Copy paste of search/memory/yndex.cpp::GenGarbageKey with small fixes.
TString GenGarbageKey(TMersenne<ui32>& random) {
    static const char alphabet[] = "abcdefghijklmnopqrstuvwxyz";
    static const ui32 frequency[] = {
        817,  149,  278,  425, 1270,
        223,  202,  609,  697,   15,
         77,  403,  241,  675,  751,
        193,   10,  599,  633,  906,
        276,   98,  236,   15,  197,
          7,
    }; // Average number of letters in 10000 letters of dictionary.
    const ui32 alphabetSize = 26;

    TString ret;
    for (int i = 0; i < 1024; i++) {
        int numberOfTerminators = (i > 1) ? (i - 1) * 4 : 0;
        ui32 order = (random.GenRand() >> 20);
        if ((order % (alphabetSize + numberOfTerminators)) > (alphabetSize - 1)) {
            break;
        } else {
            ui32 rand = random.GenRand() % 10000;
            ui32 j = 0;
            while (j + 1 < alphabetSize && rand >= frequency[j]) {
                rand -= frequency[j++];
            }
            ret += alphabet[j];
        }
    }
    return ret;
}

class TFakeProcessor : public ITupleProcessor {
private:
    enum EStatus {
        Initial,
        Started,
        Processed,
        Finished
    };

    const TTupleNameSet RequiredTuples;
    const TString PrefixMessage;
    EStatus Status;

    ui32 TmpDocId;
    const TDocIdMap* Map;

    TBuffer TuplesData;
    THashMap<TString, std::pair<size_t, size_t> > Tuples;

    void CheckStatus(EStatus goodStatus) {
        UNIT_ASSERT_EQUAL_C(Status, goodStatus, PrefixMessage + "The TTuplesAdapter has changed calls order!");
    }

public:
    TFakeProcessor(const TTupleNameSet& requiredTuples, const TString& prefixMessage)
        : RequiredTuples(requiredTuples)
        , PrefixMessage(prefixMessage)
        , Status(Initial)
        , TmpDocId((ui32)-1) // Any defined value
        , Map(nullptr) // Any defined value
    {
    }

    TString GetClassName() const override {
        return "TFakeProcessor";
    }

    TTuplesUsageInfo GetRequiredTuples() const override {
        return TTuplesUsageInfo(RequiredTuples);
    }

    void CheckInit() {
        CheckStatus(Initial);
    }
    void CheckStart() {
        CheckStatus(Started);
    }
    void CheckProcess(const TMap<TString, const TBuffer*>& messages, bool correct, ui32 tmpDocId) {
        EStatus goodStatus = correct ? Processed : Started;
        CheckStatus(goodStatus);
        Status = Started;
        if (!correct) {
            return;
        }
        for (THashMap<TString, std::pair<size_t, size_t> >::const_iterator it = Tuples.begin(); it != Tuples.end(); it++) {
            TMap<TString, const TBuffer*>::const_iterator cit = messages.find(it->first);
            UNIT_ASSERT_UNEQUAL_C(cit, messages.end(), PrefixMessage + "The TTuplesAdapter have added absent tuple!");
            const std::pair<size_t, size_t>& tupleInfo = it->second;
            const char* start = TuplesData.data() + tupleInfo.first;
            const size_t& length = tupleInfo.second;
            int res = TStringBuf{start, length}.compare(TStringBuf{cit->second->data(), cit->second->size()});
            UNIT_ASSERT_EQUAL_C(res, 0, PrefixMessage + "The TTuplesAdapter have changed value of tuple!");
        }
        TuplesData.Clear();
        Tuples.clear();
        UNIT_ASSERT_EQUAL_C(tmpDocId, TmpDocId, PrefixMessage + "The TTuplesAdapter must pass \"tmpDocId\" argument without change!");
    }
    void CheckFinish() {
        CheckStatus(Finished);
    }

    void Start() override {
        CheckStatus(Initial);
        Status = Started;
    }
    TFuture<TReturnObjectContext> Process(TObjectContext objectContext, ui32 tmpObjectId) override {
        CheckStatus(Started);
        TuplesData.Clear();
        for (const auto& tupleName : RequiredTuples) {
            UNIT_ASSERT_C(objectContext.Has(tupleName), PrefixMessage + "The TTuplesAdapter lost one of required tuples!");
            TStringBuf body = objectContext.Get<TStringBuf>(tupleName);
            Tuples[tupleName] = std::make_pair(TuplesData.size(), body.size());
            TuplesData.Append(body.data(), body.size());
        }
        TmpDocId = tmpObjectId;
        Status = Processed;
        return TReturnObjectContext::FutureOk;
    }
    void Finish(const TDocIdMap* map) override {
        CheckStatus(Started);
        Status = Finished;
        Map = map;
    }
};

bool isPercent(TMersenne<ui32> &mersenneRandom, size_t percent) {
    return mersenneRandom.GenRand() % 100 < percent;
}

} // namespace

namespace NOxygen {

using TAttrId = NKiwi::NTuples::TAttrId;
using TBranchId = NKiwi::NTuples::TBranchId;
using TTuple = NKiwi::NTuples::TTuple;
using TTupleHeader = NKiwi::NTuples::TTupleHeader;
using TTupleInfo = NKiwi::NTuples::TTupleInfo;
using TTupleTime = NKiwi::NTuples::TTupleTime;

void TTupleAdapterTester::DoPerformTest(ui32 seed) {
    TString seedMessage = Sprintf("(test seed = %lu) ", (long unsigned)seed);
    TMersenne<ui32> mersenneRandom(seed);

    // Generate names dict.
    size_t dictSize = mersenneRandom.GenRand() % 100 + 1;
    TTupleNameSet namesDict;
    for (size_t i = 0; i < dictSize; i++) {
        namesDict.insert(GenGarbageKey(mersenneRandom));
    }

    // Generate args.
    TTupleNameSet args;
    for (TTupleNameSet::const_iterator it = namesDict.begin(); it != namesDict.end(); it++) {
        if (mersenneRandom.GenRand() % (dictSize + 20) < 10) {
            args.insert(*it);
        }
    }
    TIntrusivePtr<TFakeProcessor> processor = new TFakeProcessor(args, seedMessage);

    // Init
    TAtomicSharedPtr<IThreadPool> taskPool = CreateThreadPool(1);
    TTupleAdapter adapter(taskPool, processor.Get());
    processor->CheckInit();

    // Start
    TStartContext startContext;
    adapter.Start(startContext);
    processor->CheckStart();

    size_t numObjects = mersenneRandom.GenRand() % 1000;
    ui32 tmpDocId = 0;
    TVector<TBuffer> buffers(namesDict.size());
    for (size_t i = 0; i < numObjects; i++) {
        size_t argsCount = 0;
        TObjectContext context = TObjectContext::Empty;
        TMap<TString, const TBuffer*> messages;
        bool goodObject = isPercent(mersenneRandom, 40); // 40% are good
        size_t numCorruptedTuples = mersenneRandom.GenRand() % 3;
        size_t bufferIndex = 0;
        for (TTupleNameSet::const_iterator it = namesDict.begin(); it != namesDict.end(); it++) {
            const TString& name = *it;
            bool isArg = args.find(*it) != args.end();
            bool canRemove = !goodObject || !isArg;
            if (canRemove && isPercent(mersenneRandom, 2)) { // 2% do not exist
                continue;
            } else {
                bool corrupted = canRemove && (mersenneRandom.GenRand() % (namesDict.size() + 1) < numCorruptedTuples);
                if (corrupted) {
                    numCorruptedTuples--;
                }
                size_t corruptionType = mersenneRandom.GenRand() % 2;
                // Generate message length.
                size_t len = mersenneRandom.GenRand() % 1000;
                // Create message.

                TBuffer& buffer = buffers[bufferIndex++];
                buffer.Clear();

                TBufferOutput message(buffer);
                // Fill message with random bytes. It is incorrect TKiwiObject, but TDumpInput must not look into data!
                while (len) {
                    ui32 randomBytes = mersenneRandom.GenRand();
                    size_t lenToWrite = Min<size_t>(len, sizeof(ui32));
                    message.Write(&randomBytes, lenToWrite);
                    len -= lenToWrite;
                }
                TTupleInfo info;
                info.SetStatusLabel(name);
                bool badStatus = corrupted && corruptionType == 0;
                NKwTupleMeta::EExecStatus execStatus = badStatus ? NKwTupleMeta::UDF_TIMEOUT : NKwTupleMeta::SUCCESS;
                info.SetStatusExecStatus(execStatus);
                info.SetStatusExecTimeMilliSec(1.);

                TTupleInfo* infoPtr = (corrupted && corruptionType == 1) ? nullptr : &info;

                context.AddTuple(/*attrId=*/0, /*branchId=*/0, /*timestamp=*/1345131657, buffer.data(), buffer.size(), infoPtr);
                if (!corrupted) {
                    messages[name] = &buffer;
                    argsCount += isArg;
                }
            }
        }
        bool correct = argsCount == args.size();
        adapter.WriteObject(context);
        processor->CheckProcess(messages, correct, tmpDocId);
        if (correct) {
            tmpDocId++;
        }
    }

    // Finish
    TFinishContext finishContext;
    adapter.Finish(finishContext);
    processor->CheckFinish();
}
TTupleAdapterTester::TTupleAdapterTester(bool randomSeed)
    : RandomSeed(randomSeed)
    , TestsNum(0)
{
    TString testsNum = GetEnv("TUPLE_DISPATCHER_RANDOM_TESTS_NUM");
    if (testsNum.size()) {
        TestsNum = FromString<size_t>(testsNum);
    }
}

void TTupleAdapterTester::PerformTest() {
    ui32 fixed_seeds[] = {1119325622};  // Add here any new seeds which caused problems in the "RandomSeedTest".
    size_t testsNum = RandomSeed ? TestsNum : Y_ARRAY_SIZE(fixed_seeds);

    for (size_t i = 0; i < testsNum; i++) {
        ui32 seed;
        if (RandomSeed) {
            seed = RandomNumber<ui32>();
        } else {
            seed = fixed_seeds[i];
        }
        DoPerformTest(seed);
    }
}

} // namespace NOxygen
