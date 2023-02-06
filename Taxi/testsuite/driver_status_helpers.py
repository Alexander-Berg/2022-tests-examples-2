import flatbuffers

# pylint: disable=import-error
import driver_status.fbs.v2.statuses.Item as fbs_item
import driver_status.fbs.v2.statuses.List as fbs_list
import driver_status.fbs.v2.statuses.Status as fbs_status

STATUS_MAPPING = {
    'offline': fbs_status.Status.Offline,
    'online': fbs_status.Status.Online,
    'busy': fbs_status.Status.Busy,
}


def _serialize_driver_status_item(
        builder: flatbuffers.Builder, json_item: dict,
):
    park_id_bin = builder.CreateString(json_item['park_id'])
    driver_id_bin = builder.CreateString(json_item['driver_id'])

    fbs_item.ItemStart(builder)
    fbs_item.ItemAddParkId(builder, park_id_bin)
    fbs_item.ItemAddDriverId(builder, driver_id_bin)
    fbs_item.ItemAddStatus(builder, STATUS_MAPPING[json_item['status']])
    fbs_item.ItemAddUpdatedTs(builder, json_item['updated_ts'])
    return fbs_item.ItemEnd(builder)


def make_driver_status_response(json_response: dict) -> bytes:
    builder = flatbuffers.Builder(initialSize=1024)

    items_bin = [
        _serialize_driver_status_item(builder, json_item)
        for json_item in json_response['items']
    ]

    fbs_list.ListStartItemsVector(builder, len(items_bin))
    for item in items_bin:
        builder.PrependUOffsetTRelative(item)
    items = builder.EndVector(len(items_bin))

    fbs_list.ListStart(builder)
    fbs_list.ListAddRevision(builder, json_response['revision'])
    fbs_list.ListAddItems(builder, items)
    request = fbs_list.ListEnd(builder)

    builder.Finish(request)
    return bytes(builder.Output())
