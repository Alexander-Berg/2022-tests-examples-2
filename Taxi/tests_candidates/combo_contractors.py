# pylint: disable=import-error
import datetime


import combo_contractors.fbs.Contractor as Contractor
import combo_contractors.fbs.ContractorList as ContractorList
import flatbuffers


def fbs_combo_contractors(data, time):
    timestamp = int(seconds_since_epoch(time))
    builder = flatbuffers.Builder(0)
    contractors = []
    for contractor in data:
        contractors.append(_fbs_combo_contractor(builder, contractor))
    ContractorList.ContractorListStartListVector(builder, len(contractors))
    for contractor in contractors:
        builder.PrependUOffsetTRelative(contractor)
    contractors = builder.EndVector(len(contractors))
    ContractorList.ContractorListStart(builder)
    ContractorList.ContractorListAddTimestamp(builder, timestamp)
    ContractorList.ContractorListAddList(builder, contractors)
    obj = ContractorList.ContractorListEnd(builder)
    builder.Finish(obj)
    return bytes(builder.Output())


def seconds_since_epoch(timestamp):
    epoch = datetime.datetime.utcfromtimestamp(0)
    return (timestamp - epoch).total_seconds()


def _fbs_combo_contractor(builder, contractor):
    dbid_uuid = builder.CreateString(contractor['dbid_uuid'])
    Contractor.ContractorStart(builder)
    Contractor.ContractorAddDbidUuid(builder, dbid_uuid)
    return Contractor.ContractorEnd(builder)
