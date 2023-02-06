#pragma once

class GetTestUrlJoinReduce
        : public IReducer<TTableReader<TNode>, TTableWriter<TNode>>
{

    public:
    void Do(TReader* reader, TWriter* writer);


};
