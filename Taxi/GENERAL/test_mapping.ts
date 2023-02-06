import { ScoredCategory, PlaceId } from "../definitions";
export type SaveMappingsRequest = {
    mappings: Mapping[];
};
export type RemoveMappingsForItemsRequest = {
    menu_items: string[];
};
export type Mapping = {
    scored_category: ScoredCategory;
    menu_item_id: string;
    place_id: PlaceId;
    rule_id: string;
};
