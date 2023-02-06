import {getDomIdFromEntityId} from 'client/lib/dom-id-converter';
import {MapEntity} from 'client/store/entities/types';

export const managerZonesDomId = [
    getDomIdFromEntityId(MapEntity.ZONE_DRAFTS, '4'),
    getDomIdFromEntityId(MapEntity.ZONE_DRAFTS, '5'),
    getDomIdFromEntityId(MapEntity.ZONE_DRAFTS, '6')
];

export const wmsStoresDomId = [getDomIdFromEntityId(MapEntity.WMS_STORES, '8')];

export const managerPointsDomId = [getDomIdFromEntityId(MapEntity.POINT_DRAFTS, '1')];
