#include "task.h"

TDuration TIME_LIMIT = TDuration::Days(30*120);

void GetTestUrlJoinReduce::Do(TReader* reader, TWriter* writer) {


    if(!reader->IsValid()){
        return;
    }

    if(reader->GetTableIndex() != 0){
        return;
    }

    const auto row = reader->GetRow();

    reader->Next();

    if(reader->IsValid()){


        const auto &rowFromSecondTable = reader->GetRow();
        TInstant lastCheck = TInstant::Seconds(rowFromSecondTable["Update_time"].AsInt64());

        if( (TInstant::Now() - lastCheck) > TIME_LIMIT){
            writer->AddRow(row);
        }

        } else {
            writer->AddRow(row);
        }

}

REGISTER_REDUCER(GetTestUrlJoinReduce);
