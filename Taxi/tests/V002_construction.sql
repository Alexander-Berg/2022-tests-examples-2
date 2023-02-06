CREATE TABLE users (
    user_id uuid NOT NULL PRIMARY KEY DEFAULT(uuid_generate_v4()),
    link_id SERIAL NOT NULL UNIQUE,
    user_name text NOT NULL,
    auth_user_id text NOT NULL,
    auth_module_id text,
    UNIQUE(auth_user_id)
);

CREATE TABLE users_history (
    history_event_id BIGSERIAL PRIMARY KEY,
    history_user_id text NOT NULL,
    history_originator_id text,
    history_action text NOT NULL,
    history_timestamp integer NOT NULL,
    history_comment text,

    link_id INTEGER,
    user_id text,
    user_name text NOT NULL,
    auth_module_id text,
    auth_user_id text NOT NULL
);



    CREATE TABLE db_event_log (
        ctype TEXT,
        event TEXT,
        host TEXT,
        instant BIGINT,
        duration BIGINT,
        revision BIGINT,
        service TEXT
    );


CREATE TABLE tag_descriptions (
    name text PRIMARY KEY,
    class_name TEXT NOT NULL,
    tag_description_object TEXT,
    deprecated boolean DEFAULT(false),
    description text,
    explicit_unique_policy text,
    UNIQUE(name)
);

CREATE TABLE tag_descriptions_history (
    history_event_id BIGSERIAL PRIMARY KEY,
    history_user_id text NOT NULL,
    history_originator_id text,
    history_action text NOT NULL,
    history_timestamp integer NOT NULL,
    history_comment text,

    name text NOT NULL,
    class_name TEXT NOT NULL,
    tag_description_object TEXT,
    deprecated boolean,
    description text,
    explicit_unique_policy text
);


CREATE TABLE notifiers (
    revision BIGINT,
    name text NOT NULL PRIMARY KEY,
    meta text,
    type text NOT NULL
);

CREATE TABLE notifiers_history (
    history_event_id BIGSERIAL PRIMARY KEY,
    history_user_id text NOT NULL,
    history_originator_id text,
    history_action text NOT NULL,
    history_timestamp integer NOT NULL,
    history_comment text,

    revision BIGINT,
    name text NOT NULL,
    meta text,
    type text NOT NULL
);


CREATE TABLE employers (
    employer_id uuid PRIMARY KEY DEFAULT (uuid_generate_v4()),
    employer_code text NOT NULL UNIQUE,
    employer_meta text,
    employer_type text
);

CREATE TABLE employers_history (
    history_event_id BIGSERIAL PRIMARY KEY,
    history_user_id text NOT NULL,
    history_originator_id text,
    history_action text NOT NULL,
    history_timestamp integer NOT NULL,
    history_comment text,

    employer_id uuid NOT NULL,
    employer_code text NOT NULL,
    employer_meta text,
    employer_type text
);


CREATE TABLE external_orders (
    internal_order_id BIGSERIAL PRIMARY KEY,
    external_order_id TEXT,
    planner_id TEXT NOT NULL,
    operator_id TEXT NOT NULL,
    status TEXT NOT NULL,
    current_performer_info TEXT,
    current_certificate_code TEXT,
    current_order_hash TEXT,
    need_provide_data boolean default(false)

);

CREATE TABLE external_orders_history (
    history_event_id BIGSERIAL PRIMARY KEY,
    history_user_id text NOT NULL,
    history_originator_id text,
    history_action text NOT NULL,
    history_timestamp integer NOT NULL,
    history_comment text,

    internal_order_id BIGINT NOT NULL,
    external_order_id TEXT,
    planner_id TEXT NOT NULL,
    operator_id TEXT NOT NULL,
    status TEXT NOT NULL,
    current_performer_info TEXT,
    current_certificate_code TEXT,
    current_order_hash TEXT,
    need_provide_data boolean
);


CREATE TABLE stations (
    station_name text NOT NULL,
    station_id uuid PRIMARY KEY DEFAULT (uuid_generate_v4()),
    operator_id text NOT NULL,
    operator_station_id text NOT NULL,
    station_meta text,
    revision BIGSERIAL NOT NULL,
    enabled_in_platform boolean DEFAULT(true),
    need_synchronization boolean DEFAULT(true),
    UNIQUE (operator_id, operator_station_id)
);

CREATE TABLE stations_history (
    history_event_id BIGSERIAL PRIMARY KEY,
    history_user_id text NOT NULL,
    history_originator_id text,
    history_action text NOT NULL,
    history_timestamp integer NOT NULL,
    history_comment text,

    station_name text NOT NULL,
    station_id uuid NOT NULL,
    operator_id text,
    operator_station_id text,
    station_meta text,
    enabled_in_platform boolean,
    need_synchronization boolean,
    revision BIGINT
);

CREATE TABLE station_tags (
    tag_id uuid PRIMARY KEY DEFAULT (uuid_generate_v4()),
    object_id uuid NOT NULL,
    class_name text NOT NULL,
    tag_name text NOT NULL,
    internal_identifier text,
    tag_object text,
    comments text,
    FOREIGN KEY(object_id) REFERENCES "stations"(station_id),
    FOREIGN KEY(tag_name) REFERENCES "tag_descriptions"(name)
);

CREATE TABLE station_tags_history (
    history_event_id BIGSERIAL PRIMARY KEY,
    history_user_id text NOT NULL,
    history_originator_id text,
    history_action text NOT NULL,
    history_timestamp integer NOT NULL,
    history_comment text,

    tag_id uuid NOT NULL,
    object_id uuid NOT NULL,
    class_name text NOT NULL,
    tag_name text NOT NULL,
    internal_identifier text,
    tag_object text,
    comments text
);




CREATE TABLE request_offers (
    internal_offer_id uuid PRIMARY KEY DEFAULT (uuid_generate_v4()),
    user_request_data TEXT NOT NULL,
    expiration_instant BIGINT NOT NULL,
    offer_pack_id TEXT NOT NULL,
    pricing_data TEXT
);

CREATE TABLE request_offers_history (
    history_event_id BIGSERIAL PRIMARY KEY,
    history_user_id text NOT NULL,
    history_originator_id text,
    history_action text NOT NULL,
    history_timestamp integer NOT NULL,
    history_comment text,

    internal_offer_id uuid NOT NULL,
    user_request_data TEXT NOT NULL,
    expiration_instant BIGINT NOT NULL,
    offer_pack_id TEXT NOT NULL,
    pricing_data TEXT
);



  CREATE TABLE platform_notifications (
      history_event_id BIGSERIAL PRIMARY KEY,
      history_user_id text NOT NULL,
      history_originator_id text,
      history_action text NOT NULL,
      history_timestamp integer NOT NULL,
      history_comment text,

      operator_id text NOT NULL,
      operator_request_id text NOT NULL,
      notification_type text NOT NULL
  );



CREATE TABLE carriages (
    internal_carriage_id uuid PRIMARY KEY DEFAULT (uuid_generate_v4()),
    giving_operator_carriage_date BIGINT NOT NULL,
    giving_operator_id text NOT NULL,
    giving_operator_carriage_id text NOT NULL,
    station_id uuid,
    node_id uuid,

    taking_operator_id text NOT NULL,
    taking_operator_carriage_id text,
    public_output_id_status text,
    public_input_id_status text,
    performer_status text,

    public_output_id text,
    public_input_id text,
    performer text,
    FOREIGN KEY(station_id) REFERENCES "stations"(station_id)
);

CREATE TABLE carriages_history (
    history_event_id BIGSERIAL PRIMARY KEY,
    history_user_id text NOT NULL,
    history_originator_id text,
    history_action text NOT NULL,
    history_timestamp integer NOT NULL,
    history_comment text,

    internal_carriage_id uuid NOT NULL,
    giving_operator_carriage_date BIGINT NOT NULL,
    giving_operator_id text NOT NULL,
    giving_operator_carriage_id text NOT NULL,
    public_output_id_status text,
    public_input_id_status text,
    performer_status text,

    public_output_id text,
    public_input_id text,
    performer text,
    station_id uuid,
    node_id uuid,

    taking_operator_id text NOT NULL,
    taking_operator_carriage_id text
);

CREATE TABLE carriage_parcels (
    internal_parcel_id uuid PRIMARY KEY DEFAULT (uuid_generate_v4()),
    internal_carriage_id uuid NOT NULL,
    operator_request_id text NOT NULL,
    parcel_meta text,
    FOREIGN KEY(internal_carriage_id) REFERENCES "carriages"(internal_carriage_id)
);

CREATE TABLE carriage_parcels_history (
    history_event_id BIGSERIAL PRIMARY KEY,
    history_user_id text NOT NULL,
    history_originator_id text,
    history_action text NOT NULL,
    history_timestamp integer NOT NULL,
    history_comment text,

    internal_parcel_id uuid NOT NULL,
    internal_carriage_id uuid NOT NULL,
    operator_request_id text NOT NULL,
    parcel_meta text
);



CREATE TABLE waybill_planner_tasks (
    internal_task_id uuid PRIMARY KEY DEFAULT (uuid_generate_v4()),
    operator_id text NOT NULL,
    planner_id text NOT NULL,
    external_planner_task_id text NOT NULL,
    task_status text NOT NULL,
    current_message TEXT
);

CREATE TABLE waybill_planner_tasks_history (
    history_event_id BIGSERIAL PRIMARY KEY,
    history_user_id text NOT NULL,
    history_originator_id text,
    history_action text NOT NULL,
    history_timestamp integer NOT NULL,
    history_comment text,

    internal_task_id uuid NOT NULL,
    operator_id text NOT NULL,
    planner_id text NOT NULL,
    external_planner_task_id text NOT NULL,
    task_status text NOT NULL,
    current_message TEXT
);


CREATE TABLE requests (
    request_code text NOT NULL,
    request_id uuid PRIMARY KEY DEFAULT (uuid_generate_v4()),
    request_meta text,
    status text,
    employer_code text NOT NULL,
    decision_deadline integer NOT NULL,
    revision BIGSERIAL,
    created_at integer,
    comment text,
    priority integer,
    FOREIGN KEY(employer_code) REFERENCES "employers"(employer_code),
    UNIQUE(employer_code, request_code)
);

CREATE INDEX ON requests(request_code);

CREATE TABLE requests_history (
    history_event_id BIGSERIAL PRIMARY KEY,
    history_user_id text NOT NULL,
    history_originator_id text,
    history_action text NOT NULL,
    history_timestamp integer NOT NULL,
    history_comment text,

    request_code text NOT NULL,
    status text,
    request_id uuid NOT NULL,
    request_meta text,
    created_at integer,
    comment text,
    priority integer,
    decision_deadline integer NOT NULL,
    employer_code text NOT NULL,
    revision BIGINT
);

CREATE TABLE request_tags (
    tag_id uuid PRIMARY KEY DEFAULT (uuid_generate_v4()),
    object_id uuid NOT NULL,
    class_name text NOT NULL,
    tag_name text NOT NULL,
    internal_identifier text,
    tag_object text,
    comments text,
    FOREIGN KEY(object_id) REFERENCES "requests"(request_id),
    FOREIGN KEY(tag_name) REFERENCES "tag_descriptions"(name)
);

CREATE TABLE request_tags_history (
    history_event_id BIGSERIAL PRIMARY KEY,
    history_user_id text NOT NULL,
    history_originator_id text,
    history_action text NOT NULL,
    history_timestamp integer NOT NULL,
    history_comment text,

    tag_id uuid NOT NULL,
    object_id uuid NOT NULL,
    class_name text NOT NULL,
    tag_name text NOT NULL,
    internal_identifier text,
    tag_object text,
    comments text
);


CREATE TABLE rt_background_settings (
    bp_id uuid DEFAULT (uuid_generate_v4()) NOT NULL UNIQUE,
    bp_name TEXT NOT NULL UNIQUE,
    bp_type TEXT NOT NULL,
    bp_settings TEXT NOT NULL,
    bp_revision BIGSERIAL,
    bp_enabled BOOLEAN DEFAULT (false)
);

CREATE TABLE rt_background_settings_history (
    history_event_id SERIAL PRIMARY KEY,
    history_user_id text NOT NULL,
    history_action text NOT NULL,
    history_timestamp integer NOT NULL,
    history_comment text,
    history_originator_id text,

    bp_id uuid,
    bp_name TEXT NOT NULL,
    bp_type TEXT NOT NULL,
    bp_settings TEXT NOT NULL,
    bp_revision BIGINT,
    bp_enabled BOOLEAN NOT NULL
);

CREATE TABLE rt_background_state (
    bp_id uuid DEFAULT (uuid_generate_v4()) NOT NULL UNIQUE,
    bp_name TEXT NOT NULL UNIQUE,
    bp_type TEXT NOT NULL,
    bp_state TEXT NOT NULL,
    bp_last_execution INTEGER DEFAULT 0,
    bp_status TEXT DEFAULT 'NOT_STARTED'
);


CREATE TABLE server_settings (
    setting_key text NOT NULL,
    setting_subkey text DEFAULT '' NOT NULL,
    setting_value text NOT NULL
);

CREATE TABLE server_settings_history (
    history_event_id BIGSERIAL PRIMARY KEY,
    history_user_id text NOT NULL,
    history_originator_id text,
    history_action text NOT NULL,
    history_timestamp integer NOT NULL,
    history_comment text,

    setting_key text NOT NULL,
    setting_subkey text DEFAULT '' NOT NULL,
    setting_value text NOT NULL
);


CREATE TABLE contractor_profiles (
    internal_contractor_id uuid PRIMARY KEY DEFAULT (uuid_generate_v4()),
    profile_meta text,
    current_proposition_id TEXT NOT NULL,
    external_order_id TEXT,
    operator_id TEXT NOT NULL,
    operator_contractor_id text UNIQUE
);

CREATE TABLE contractor_profiles_history (
    history_event_id BIGSERIAL PRIMARY KEY,
    history_user_id text NOT NULL,
    history_originator_id text,
    history_action text NOT NULL,
    history_timestamp integer NOT NULL,
    history_comment text,

    internal_contractor_id uuid NOT NULL,
    profile_meta text,
    current_proposition_id TEXT NOT NULL,
    external_order_id TEXT,
    operator_id text NOT NULL,
    operator_contractor_id TEXT NOT NULL
);


CREATE TABLE planned_nodes (
    node_id uuid PRIMARY KEY DEFAULT (uuid_generate_v4()),
    node_meta text NOT NULL,
    request_id uuid NOT NULL,
    public_output_carriage_id text,
    need_output_electronic_certificate boolean,
    need_input_electronic_certificate boolean,

    FOREIGN KEY(request_id) REFERENCES "requests"(request_id)
);

CREATE TABLE planned_nodes_history (
    history_event_id BIGSERIAL PRIMARY KEY,
    history_user_id text NOT NULL,
    history_originator_id text,
    history_action text NOT NULL,
    history_timestamp integer NOT NULL,
    history_comment text,

    node_id uuid NOT NULL,
    node_meta text NOT NULL,
    request_id uuid NOT NULL,
    public_output_carriage_id text,
    need_output_electronic_certificate boolean,
    need_input_electronic_certificate boolean
);


CREATE TABLE resources (
    resource_id uuid PRIMARY KEY DEFAULT (uuid_generate_v4()),
    numeric_internal_resource_id BIGSERIAL NOT NULL,
    resource_code text,
    node_id uuid,
    transfer_id uuid,
    request_id uuid,
    class_name text,
    resource_meta text,
    current_layout_id uuid,
    FOREIGN KEY(request_id) REFERENCES "requests"(request_id)
);

CREATE TABLE resources_history (
    history_event_id BIGSERIAL PRIMARY KEY,
    history_user_id text NOT NULL,
    history_originator_id text,
    history_action text NOT NULL,
    history_timestamp integer NOT NULL,
    history_comment text,

    resource_id uuid,
    numeric_internal_resource_id BIGINT,
    resource_code text,
    node_id uuid,
    transfer_id uuid,
    request_id uuid,
    class_name text,
    resource_meta text,
    current_layout_id uuid
);

CREATE TABLE resource_tags (
    tag_id uuid PRIMARY KEY DEFAULT (uuid_generate_v4()),
    object_id uuid NOT NULL,
    class_name text NOT NULL,
    tag_name text NOT NULL,
    internal_identifier text,
    tag_object text,
    comments text,
    FOREIGN KEY(object_id) REFERENCES "resources"(resource_id),
    FOREIGN KEY(tag_name) REFERENCES "tag_descriptions"(name)
);

CREATE TABLE resource_tags_history (
    history_event_id BIGSERIAL PRIMARY KEY,
    history_user_id text NOT NULL,
    history_originator_id text,
    history_action text NOT NULL,
    history_timestamp integer NOT NULL,
    history_comment text,

    tag_id uuid NOT NULL,
    object_id uuid NOT NULL,
    class_name text NOT NULL,
    tag_name text NOT NULL,
    internal_identifier text,
    tag_object text,
    comments text
);


  CREATE TABLE resource_layouts (
      internal_layout_id uuid PRIMARY KEY DEFAULT(uuid_generate_v4()),
      layout_name TEXT,
      resource_id uuid NOT NULL,
      request_id uuid NOT NULL,

      FOREIGN KEY(request_id) REFERENCES "requests"(request_id),
      FOREIGN KEY(resource_id) REFERENCES "resources"(resource_id)
  );

  CREATE TABLE resource_layouts_history (
      history_event_id BIGSERIAL PRIMARY KEY,
      history_user_id text NOT NULL,
      history_originator_id text,
      history_action text NOT NULL,
      history_timestamp integer NOT NULL,
      history_comment text,
      order_id text,
      session_id uuid,
      sync_status text,

      internal_layout_id uuid NOT NULL,
      layout_name TEXT,
      resource_id uuid NOT NULL,
      request_id uuid NOT NULL
  );


  CREATE SEQUENCE resource_places_barcode_seq;

  CREATE TABLE resource_places (
      internal_place_id uuid PRIMARY KEY DEFAULT(uuid_generate_v4()),
      place_code TEXT NOT NULL,
      barcode TEXT,
      description TEXT,
      place_meta TEXT,
      resource_id uuid NOT NULL,
      request_id uuid NOT NULL,
      destination_node_id uuid,
      perform_instant integer,
      reservation_id uuid,
      transfer_id uuid,
      current_info text,

      FOREIGN KEY(request_id) REFERENCES "requests"(request_id),
      FOREIGN KEY(resource_id) REFERENCES "resources"(resource_id)
  );

  CREATE TABLE resource_places_history (
      history_event_id BIGSERIAL PRIMARY KEY,
      history_user_id text NOT NULL,
      history_originator_id text,
      history_action text NOT NULL,
      history_timestamp integer NOT NULL,
      history_comment text,

      internal_place_id uuid NOT NULL,
      place_code TEXT NOT NULL,
      barcode TEXT,
      description TEXT,
      place_meta TEXT,
      resource_id uuid NOT NULL,
      request_id uuid NOT NULL,
      destination_node_id uuid,
      perform_instant integer,
      reservation_id uuid,
      transfer_id uuid,
      current_info text
  );



  CREATE TABLE resource_items (
      internal_item_id uuid PRIMARY KEY DEFAULT(uuid_generate_v4()),
      vendor_id TEXT,
      resource_id uuid NOT NULL,
      request_id uuid NOT NULL,
      internal_place_id uuid,
      article TEXT NOT NULL,
      barcode TEXT,
      count INTEGER NOT NULL,
      refused_count INTEGER NOT NULL,
      name TEXT,
      marking_code TEXT,
      item_meta TEXT,

      FOREIGN KEY(request_id) REFERENCES "requests"(request_id),
      FOREIGN KEY(resource_id) REFERENCES "resources"(resource_id),
      FOREIGN KEY(internal_place_id) REFERENCES "resource_places"(internal_place_id),
      UNIQUE(article, request_id)
  );

  CREATE TABLE resource_items_history (
      history_event_id BIGSERIAL PRIMARY KEY,
      history_user_id text NOT NULL,
      history_originator_id text,
      history_action text NOT NULL,
      history_timestamp integer NOT NULL,
      history_comment text,
      order_id text,
      session_id uuid,
      sync_status text,

      internal_item_id uuid NOT NULL,
      vendor_id TEXT,
      resource_id uuid NOT NULL,
      request_id uuid NOT NULL,
      internal_place_id uuid,
      article TEXT,
      barcode TEXT,
      count INTEGER NOT NULL,
      refused_count INTEGER,
      name TEXT,
      marking_code TEXT,
      item_meta TEXT
  );


  CREATE TABLE resource_place_links (
      link_id BIGSERIAL PRIMARY KEY,
      owner_id uuid NOT NULL,
      slave_id uuid NOT NULL,

      FOREIGN KEY(owner_id) REFERENCES "resource_places"(internal_place_id),
      FOREIGN KEY(slave_id) REFERENCES "resource_items"(internal_item_id)
  );

  CREATE TABLE resource_place_links_history (
      history_event_id BIGSERIAL PRIMARY KEY,
      history_user_id text NOT NULL,
      history_originator_id text,
      history_action text NOT NULL,
      history_timestamp integer NOT NULL,
      history_comment text,

      link_id BIGINT NOT NULL,
      owner_id uuid NOT NULL,
      slave_id uuid NOT NULL
  );


CREATE TABLE requested_actions (
    action_id BIGSERIAL PRIMARY KEY,
    node_id uuid NOT NULL,
    requested_action_meta text,
    request_id uuid NOT NULL,
    action_status text NOT NULL,
    need_confirmation boolean,
    confirmation_code text,

    FOREIGN KEY(node_id) REFERENCES "planned_nodes"(node_id),
    FOREIGN KEY(request_id) REFERENCES "requests"(request_id)
);

CREATE TABLE requested_actions_history (
    history_event_id BIGSERIAL PRIMARY KEY,
    history_user_id text NOT NULL,
    history_originator_id text,
    history_action text NOT NULL,
    history_timestamp integer NOT NULL,
    history_comment text,

    action_id BIGINT NOT NULL,
    node_id uuid NOT NULL,
    requested_action_meta text,
    request_id uuid,
    action_status text,
    need_confirmation boolean,
    confirmation_code text
);


CREATE TABLE planned_transfers (
    transfer_id uuid PRIMARY KEY DEFAULT (uuid_generate_v4()),
    node_return_id uuid,
    node_from_id uuid NOT NULL,
    node_to_id uuid NOT NULL,
    action_from_id bigint NOT NULL,
    action_to_id bigint NOT NULL,
    resource_id uuid NOT NULL,
    request_id uuid NOT NULL,
    performer_id text,
    transfer_meta text,
    internal_place_id uuid NOT NULL,
    operator_id text,
    external_order_id text,
    status text NOT NULL,
    enabled boolean,
    waybill_planner_task_id uuid,
    generation_tag_id uuid,
    input_carriage_id uuid,
    output_carriage_id uuid,
    quota_id text,
    FOREIGN KEY(node_return_id) REFERENCES "planned_nodes"(node_id),
    FOREIGN KEY(node_from_id) REFERENCES "planned_nodes"(node_id),
    FOREIGN KEY(node_to_id) REFERENCES "planned_nodes"(node_id),
    FOREIGN KEY(action_from_id) REFERENCES "requested_actions"(action_id),
    FOREIGN KEY(action_to_id) REFERENCES "requested_actions"(action_id),
    FOREIGN KEY(request_id) REFERENCES "requests"(request_id),
    FOREIGN KEY(generation_tag_id) REFERENCES "station_tags"(tag_id),
    FOREIGN KEY(resource_id) REFERENCES "resources"(resource_id),
    FOREIGN KEY(internal_place_id) REFERENCES "resource_places"(internal_place_id),
    FOREIGN KEY(performer_id) REFERENCES "contractor_profiles"(operator_contractor_id),
    FOREIGN KEY(waybill_planner_task_id) REFERENCES "waybill_planner_tasks"(internal_task_id),
    FOREIGN KEY(input_carriage_id) REFERENCES "carriages"(internal_carriage_id),
    FOREIGN KEY(output_carriage_id) REFERENCES "carriages"(internal_carriage_id),
    CHECK (((operator_id IS NULL) = (external_order_id IS NULL)) OR ((NOT operator_id IS NULL) AND (external_order_id IS NULL)))
);

CREATE TABLE planned_transfers_history (
    history_event_id BIGSERIAL PRIMARY KEY,
    history_user_id text NOT NULL,
    history_originator_id text,
    history_action text NOT NULL,
    history_timestamp integer NOT NULL,
    history_comment text,

    node_return_id uuid,
    node_from_id uuid NOT NULL,
    node_to_id uuid NOT NULL,
    action_from_id bigint NOT NULL,
    action_to_id bigint NOT NULL,
    transfer_id uuid NOT NULL,
    resource_id uuid NOT NULL,
    request_id uuid NOT NULL,
    performer_id text,
    transfer_meta text,
    internal_place_id uuid,
    operator_id text,
    external_order_id text,
    status text,
    enabled boolean,
    waybill_planner_task_id uuid,
    generation_tag_id uuid,
    input_carriage_id uuid,
    output_carriage_id uuid,
    quota_id text
);


  CREATE TABLE node_reservations (
      reservation_id uuid PRIMARY KEY DEFAULT(uuid_generate_v4()),
      request_id uuid NOT NULL,
      resource_id uuid NOT NULL,
      node_id uuid NOT NULL,
      action_put_id BIGINT,
      action_take_id BIGINT,
      reserve_put_ts BIGINT NOT NULL,
      reserve_take_ts BIGINT NOT NULL,
      status text NOT NULL,
      reservation_meta text,
      operator_id text,
      external_order_id text,
      deploy_id text,
      internal_place_id uuid NOT NULL,
      input_carriage_id uuid,
      output_carriage_id uuid,
      FOREIGN KEY(request_id) REFERENCES "requests"(request_id),
      FOREIGN KEY(node_id) REFERENCES "planned_nodes"(node_id),
      FOREIGN KEY(action_put_id) REFERENCES "requested_actions"(action_id),
      FOREIGN KEY(action_take_id) REFERENCES "requested_actions"(action_id),
      FOREIGN KEY(internal_place_id) REFERENCES "resource_places"(internal_place_id),
      FOREIGN KEY(input_carriage_id) REFERENCES "carriages"(internal_carriage_id),
      FOREIGN KEY(output_carriage_id) REFERENCES "carriages"(internal_carriage_id),
      UNIQUE(action_put_id, action_take_id),
      CHECK (((operator_id IS NULL) = (external_order_id IS NULL)) OR ((NOT operator_id IS NULL) AND (external_order_id IS NULL)))
  );

  CREATE TABLE node_reservations_history (
      history_event_id BIGSERIAL PRIMARY KEY,
      history_user_id text NOT NULL,
      history_originator_id text,
      history_action text NOT NULL,
      history_timestamp integer NOT NULL,
      history_comment text,
      order_id text,
      session_id uuid,
      sync_status text,

      reservation_id uuid NOT NULL,
      request_id uuid NOT NULL,
      resource_id uuid NOT NULL,
      node_id uuid NOT NULL,
      action_put_id BIGINT,
      action_take_id BIGINT,
      reserve_put_ts BIGINT NOT NULL,
      reserve_take_ts BIGINT NOT NULL,
      status text NOT NULL,
      reservation_meta text,
      operator_id text,
      external_order_id text,
      deploy_id text,
      internal_place_id uuid,
      input_carriage_id uuid,
      output_carriage_id uuid
  );


  CREATE TABLE hard_planned_tasks (
      task_id uuid PRIMARY KEY DEFAULT(uuid_generate_v4())
  );

  CREATE TABLE hard_planned_tasks_history (
      history_event_id BIGSERIAL PRIMARY KEY,
      history_user_id text NOT NULL,
      history_originator_id text,
      history_action text NOT NULL,
      history_timestamp integer NOT NULL,
      history_comment text,

      task_id uuid NOT NULL
  );


CREATE TABLE instructions (
    instruction_id uuid NOT NULL PRIMARY KEY DEFAULT(uuid_generate_v4()),
    request_id uuid NOT NULL,
    resource_id uuid NOT NULL,
    node_id uuid NOT NULL,
    action_id bigint,

    FOREIGN KEY(resource_id) REFERENCES "resources"(resource_id),
    FOREIGN KEY(request_id) REFERENCES "requests"(request_id),
    FOREIGN KEY(node_id) REFERENCES "planned_nodes"(node_id),
    FOREIGN KEY(action_id) REFERENCES "requested_actions"(action_id),
    UNIQUE(resource_id, node_id)
);

CREATE TABLE instructions_history (
    history_event_id BIGSERIAL PRIMARY KEY,
    history_user_id text NOT NULL,
    history_originator_id text,
    history_action text NOT NULL,
    history_timestamp integer NOT NULL,
    history_comment text,

    instruction_id uuid NOT NULL,
    request_id uuid NOT NULL,
    resource_id uuid NOT NULL,
    node_id uuid NOT NULL,
    action_id bigint
);

CREATE TABLE instruction_items (
    instruction_item_id uuid NOT NULL PRIMARY KEY DEFAULT(uuid_generate_v4()),
    instruction_id uuid NOT NULL,
    request_id uuid NOT NULL,

    instruction_sequential_index integer NOT NULL,
    item_meta text,
    class_name text,

    FOREIGN KEY(request_id) REFERENCES "requests"(request_id),
    FOREIGN KEY(instruction_id) REFERENCES "instructions"(instruction_id)
);

CREATE TABLE instruction_items_history (
    history_event_id BIGSERIAL PRIMARY KEY,
    history_user_id text NOT NULL,
    history_originator_id text,
    history_action text NOT NULL,
    history_timestamp integer NOT NULL,
    history_comment text,

    instruction_item_id uuid NOT NULL,
    instruction_id uuid NOT NULL,
    request_id uuid NOT NULL,

    instruction_sequential_index integer NOT NULL,
    item_meta text,
    class_name text
);


CREATE TABLE route_propositions (
      proposition_id uuid PRIMARY KEY DEFAULT (uuid_generate_v4()),
      plan_route_meta text,
      proposition_meta text,
      created_at integer NOT NULL,
      proposition_price float NOT NULL,
      class_name text NOT NULL,
      contractor_id text UNIQUE,
      order_id text UNIQUE,
      session_id uuid,
      drop_contractors_count integer,
      sync_status text DEFAULT('new'),
      FOREIGN KEY(session_id) REFERENCES "contractor_profiles"(internal_contractor_id)
  );

  CREATE TABLE route_propositions_history (
      history_event_id BIGSERIAL PRIMARY KEY,
      history_user_id text NOT NULL,
      history_originator_id text,
      history_action text NOT NULL,
      history_timestamp integer NOT NULL,
      history_comment text,
      order_id text,
      session_id uuid,
      sync_status text,


      proposition_id uuid NOT NULL,
      plan_route_meta text,
      proposition_meta text,
      created_at integer NOT NULL,
      proposition_price float NOT NULL,
      class_name text NOT NULL,
      contractor_id text,
      drop_contractors_count integer
  );


CREATE TABLE rejections (
    rejection_id uuid PRIMARY KEY DEFAULT (uuid_generate_v4()),
    contractor_id text NOT NULL,
    transfer_id uuid,
    proposition_id uuid,
    operator_id text NOT NULL,
    supply_type text,
    FOREIGN KEY(transfer_id) REFERENCES "planned_transfers"(transfer_id)
);

CREATE TABLE rejections_history (
    history_event_id BIGSERIAL PRIMARY KEY,
    history_user_id text NOT NULL,
    history_originator_id text,
    history_action text NOT NULL,
    history_timestamp integer NOT NULL,
    history_comment text,

    rejection_id uuid NOT NULL,
    transfer_id uuid,
    proposition_id uuid,
    contractor_id text NOT NULL,
    operator_id text NOT NULL,
    supply_type text
);


CREATE TABLE planned_actions (
    action_id BIGINT PRIMARY KEY,
    operator_contractor_id text,
    requested_action text NOT NULL,
    request_id uuid NOT NULL,
    resource_id uuid NOT NULL,
    internal_place_id uuid NOT NULL,
    basic_plan text,
    transfer_id uuid NOT NULL,
    node_id uuid NOT NULL,
    notified text,
    execution_idx integer NOT NULL,
    internal_contractor_id uuid,

    FOREIGN KEY(operator_contractor_id) REFERENCES "contractor_profiles"(operator_contractor_id),
    FOREIGN KEY(internal_contractor_id) REFERENCES "contractor_profiles"(internal_contractor_id),
    FOREIGN KEY(node_id) REFERENCES "planned_nodes"(node_id),
    FOREIGN KEY(internal_place_id) REFERENCES "resource_places"(internal_place_id),
    FOREIGN KEY(action_id) REFERENCES "requested_actions"(action_id),
    FOREIGN KEY(transfer_id) REFERENCES "planned_transfers"(transfer_id),
    FOREIGN KEY(resource_id) REFERENCES "resources"(resource_id),
    FOREIGN KEY(request_id) REFERENCES "requests"(request_id)
);

CREATE TABLE planned_actions_history (
    history_event_id BIGSERIAL PRIMARY KEY,
    history_user_id text NOT NULL,
    history_originator_id text,
    history_action text NOT NULL,
    history_timestamp integer NOT NULL,
    history_comment text,

    action_id BIGINT NOT NULL,
    operator_contractor_id text,
    internal_contractor_id uuid,
    transfer_id uuid NOT NULL,
    requested_action text NOT NULL,
    request_id uuid NOT NULL,
    resource_id uuid NOT NULL,
    internal_place_id uuid NOT NULL,
    node_id uuid NOT NULL,
    notified text,
    basic_plan text,
    execution_idx integer NOT NULL
);


CREATE TABLE taxi_orders (
    order_id text PRIMARY KEY,
    version BIGSERIAL,
    order_meta text
);

CREATE TABLE taxi_orders_history (
    history_event_id BIGSERIAL PRIMARY KEY,
    history_user_id text NOT NULL,
    history_originator_id text,
    history_action text NOT NULL,
    history_timestamp integer NOT NULL,
    history_comment text,

    version BIGINT NOT NULL,
    order_id text NOT NULL,
    order_meta text
);

CREATE TABLE checkpoints (
    occurred_at integer NOT NULL,
    request_id text NOT NULL,
    checkpoint integer NOT NULL
);

CREATE TABLE interlayer_couriers (
    courier_id text PRIMARY KEY,
    depot_id text NOT NULL,
    json_data text NOT NULL
);

CREATE TABLE interlayer_routes (
    id text PRIMARY KEY,
    depot text NOT NULL,
    quality text NOT NULL,
    settlement_date text NOT NULL,
    status text NOT NULL,
    status_updated integer NOT NULL,
    routeq_id text,
    estimate integer,
    message text
);


  CREATE TABLE operator_events_history (
      history_event_id BIGSERIAL PRIMARY KEY,
      history_user_id text NOT NULL,
      history_originator_id text,
      history_action text NOT NULL,
      history_timestamp integer NOT NULL,
      history_comment text,

      event_status text NOT NULL,
      operator_id text NOT NULL,
      external_order_id text NOT NULL,
      external_place_id text,
      event_instant BIGINT NOT NULL,
      event_meta text,
      class_name text NOT NULL,
      operator_event_type text,
      operator_initiator text,
      operator_comment text,
      initiator text,
      deferred_instant integer,
      idempotency_token text UNIQUE
  );


  CREATE TABLE operator_commands (
      internal_command_id BIGSERIAL PRIMARY KEY,
      class_name text NOT NULL,
      operator_id text NOT NULL,
      external_order_id text NOT NULL,
      command_meta text,
      initiator text NOT NULL,
      comment text,
      last_operator_reply text,
      last_operator_reply_instant BIGINT,
      common_command_meta text,
      command_hash_id text NOT NULL
  );

  CREATE TABLE operator_commands_history (
      history_event_id BIGSERIAL PRIMARY KEY,
      history_user_id text NOT NULL,
      history_originator_id text,
      history_action text NOT NULL,
      history_timestamp integer NOT NULL,
      history_comment text,

      internal_command_id BIGINT NOT NULL,
      class_name text NOT NULL,
      operator_id text NOT NULL,
      external_order_id text NOT NULL,
      command_meta text,
      initiator text NOT NULL,
      comment text,
      last_operator_reply text,
      last_operator_reply_instant BIGINT,
      common_command_meta text,
      command_hash_id text NOT NULL
  );


CREATE TABLE events_storage (
    id BIGSERIAL PRIMARY KEY,
    event text NOT NULL,
    flow text NOT NULL,
    key text NOT NULL,
    timestamp integer NOT NULL
);

CREATE TABLE events_storage_history (
    history_event_id BIGSERIAL PRIMARY KEY,
    history_user_id text NOT NULL,
    history_originator_id text,
    history_action text NOT NULL,
    history_timestamp integer NOT NULL,
    history_comment text,

    id integer NOT NULL,
    event text NOT NULL,
    flow text NOT NULL,
    key text NOT NULL,
    timestamp integer NOT NULL
);


CREATE TABLE courier_advice_calculation_log (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE,
    distance REAL,
    time INTEGER,
    travel_mode TEXT,
    courier_busy BOOLEAN,
    courier_id TEXT,
    dispatch_proposition_id UUID,
    transfer_id UUID,
    shift_id TEXT
);


CREATE TABLE courier_proposition_taxi_id_log (
    id BIGSERIAL PRIMARY KEY,
    dispatch_proposition_id UUID,
    taxi_order_id TEXT
);


CREATE TABLE supply_estimator_experiments (
    id SERIAL PRIMARY KEY,
    segment_id TEXT NOT NULL,
    experiment_name TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    result TEXT NOT NULL
);


CREATE TABLE planner_action_context (
      action_id bigint PRIMARY KEY,
      meta text
  );



CREATE TABLE billing_account (
    id uuid PRIMARY KEY DEFAULT(uuid_generate_v4()),
    payment_policy TEXT NOT NULL,
    policy_meta TEXT NOT NULL
);

CREATE TABLE billing_account_history (
    history_event_id BIGSERIAL PRIMARY KEY,
    history_user_id text NOT NULL,
    history_originator_id text,
    history_action text NOT NULL,
    history_timestamp integer NOT NULL,
    history_comment text,

    id uuid NOT NULL,
    policy_meta TEXT NOT NULL,
    payment_policy TEXT NOT NULL
);

CREATE TABLE payment_history (
    history_event_id BIGSERIAL PRIMARY KEY,
    history_user_id text NOT NULL,
    history_originator_id text,
    history_action text NOT NULL,
    history_timestamp integer NOT NULL,
    history_comment text,

    id uuid DEFAULT(uuid_generate_v4()),
    request_id text NOT NULL,
    status text NOT NULL,
    corp_client_id text NOT NULL,
    account_id text NOT NULL,
    account_type text NOT NULL,
    amount integer NOT NULL,
    currency text NOT NULL,
    operation_instant integer NOT NULL,
    order_meta text,
    billing_doc_id text,
    payment_method text,
    version integer,
    refund BOOLEAN,
    prepaid BOOLEAN,
    comment text
);

CREATE TABLE user_accounts (
    id uuid PRIMARY KEY DEFAULT(uuid_generate_v4()),
    user_id uuid NOT NULL REFERENCES employers(employer_id),
    account_id uuid NOT NULL REFERENCES billing_account(id)
);

CREATE TABLE user_accounts_history (
    history_event_id BIGSERIAL PRIMARY KEY,
    history_user_id text NOT NULL,
    history_originator_id text,
    history_action text NOT NULL,
    history_timestamp integer NOT NULL,
    history_comment text,

    id uuid NOT NULL,
    user_id uuid NOT NULL,
    account_id uuid NOT NULL
);



CREATE TABLE geoarea_tags (
    tag_id uuid PRIMARY KEY DEFAULT(uuid_generate_v4()),
    object_id text NOT NULL,
    class_name text NOT NULL,
    tag_name text NOT NULL REFERENCES tag_descriptions(name),
    internal_identifier text,
    tag_object text,
    comments text
);

CREATE TABLE geoarea_tags_history (
    history_event_id BIGSERIAL PRIMARY KEY,
    history_user_id text NOT NULL,
    history_originator_id text,
    history_action text NOT NULL,
    history_timestamp integer NOT NULL,
    history_comment text,

    tag_id uuid,
    object_id text,
    class_name text NOT NULL,
    tag_name text NOT NULL,
    internal_identifier text,
    tag_object text,
    comments text
);



CREATE TABLE emulation_results (
    cargo_claim_id text PRIMARY KEY,
    courier_id text NOT NULL,
    logistic_group text NOT NULL,
    delivery_completed_at integer,
    delivery_started_at integer,
    courier_back_at integer
);

CREATE INDEX ON emulation_results (logistic_group);


  CREATE TABLE request_compilations (
      history_event_id BIGSERIAL PRIMARY KEY,
      history_user_id text NOT NULL,
      history_originator_id text,
      history_action text NOT NULL,
      history_timestamp integer NOT NULL,
      history_comment text,

      request_id text NOT NULL,
      request_code text NOT NULL,
      employer_code text NOT NULL,
      request_status text,
      created_at integer,
      delivery_date integer,
      delivery_policy text,
      operator_id text,
      recipient_phone_pd_id text,
      data text NOT NULL
  );


CREATE TABLE procaas_messages_history (
    history_event_id BIGSERIAL PRIMARY KEY,
    history_user_id text NOT NULL,
    history_originator_id text,
    history_action text NOT NULL,
    history_timestamp integer NOT NULL,
    history_comment text,
    
    scope TEXT NOT NULL,
    queue TEXT NOT NULL,
    item_id TEXT NOT NULL,
    kwargs TEXT NOT NULL,
    idempotency_token TEXT
);
CREATE INDEX ON procaas_messages_history(history_timestamp);