--
-- Name: orders_0; Type: TABLE; Schema: public; Owner: taximeter
--

CREATE TABLE orders_0 (
    park_id character varying(32) NOT NULL,
    id character varying(32) NOT NULL,
    old_uuid character varying(48),
    number integer NOT NULL,
    number_group integer DEFAULT 0,
    clid bigint,
    agg_id character varying(32),
    agg_name character varying(128),
    status integer DEFAULT 0,
    address_from character varying(1024),
    address_to character varying(1024),
    route_points jsonb,
    driver_id character varying(32),
    driver_name character varying(128),
    driver_signal character varying(32),
    car_id character varying(32),
    car_name character varying(128),
    car_number character varying(16),
    car_franchise bit(1) DEFAULT B'0'::"bit",
    phone1 character varying(32),
    phone2 character varying(32),
    phone3 character varying(32),
    phone_addition bit(1) DEFAULT B'0'::"bit",
    phone_show bit(1) DEFAULT B'0'::"bit",
    rule_type_id character varying(32),
    rule_type_name character varying(32),
    rule_type_color character varying(9),
    rule_work_id character varying(32),
    rule_work_name character varying(64),
    tariff_id character varying(32),
    tariff_name character varying(128),
    tariff_discount character varying(32),
    tariff_type integer,
    provider integer DEFAULT 0,
    kind integer DEFAULT 0,
    categorys integer DEFAULT 0,
    requirements integer DEFAULT 0,
    payment integer DEFAULT 0,
    chair integer DEFAULT 0,
    date_create timestamp without time zone NOT NULL,
    date_booking timestamp without time zone NOT NULL,
    date_drive timestamp without time zone,
    date_waiting timestamp without time zone,
    date_calling timestamp without time zone,
    date_transporting timestamp without time zone,
    date_end timestamp without time zone,
    date_last_change timestamp without time zone,
    description character varying(512),
    description_canceled character varying(512),
    adv character varying(128),
    company_id character varying(32),
    company_name character varying(128),
    company_responsible character varying(128),
    company_passenger character varying(128),
    company_cost_center character varying(128),
    company_subdivision character varying(128),
    company_department character varying(128),
    company_comment_trip character varying(128),
    company_comment character varying(128),
    company_slip character varying(32),
    company_params bit(1) DEFAULT B'0'::"bit",
    card_paind bit(1) DEFAULT B'0'::"bit",
    user_id character varying(32),
    user_name character varying(128),
    client_id character varying(32),
    client_name character varying(128),
    client_cost_code character varying(64),
    cost_pay numeric(18,6) DEFAULT 0,
    cost_total numeric(18,6) DEFAULT 0,
    cost_sub numeric(18,6) DEFAULT 0,
    cost_commission numeric(18,6) DEFAULT 0,
    cost_discount numeric(18,6) DEFAULT 0,
    cost_cupon numeric(18,6) DEFAULT 0,
    cost_coupon_percent numeric(10,5),
    fixed_price jsonb,
    bill_json character varying(1024),
    bill_total_time numeric(18,6),
    bill_total_distance numeric(18,6),
    important bit(1) DEFAULT B'0'::"bit",
    sms bit(1) DEFAULT B'0'::"bit",
    closed_manually bit(1),
    csv_commission_cost numeric(18,6) DEFAULT 0,
    csv_commission_yandex numeric(18,6) DEFAULT 0,
    csv_commission_agg numeric(18,6),
    csv_commission_park numeric(18,6),
    csv_subsidy numeric(18,6) DEFAULT 0,
    csv_subsidy_no_commission numeric(18,6),
    csv_coupon_paid numeric(18,6) DEFAULT 0,
    csv_payments numeric(18,6) DEFAULT 0,
    csv_tips numeric(18,6) DEFAULT 0,
    price_corrections json,
    receipt jsonb,
    home_coord jsonb,
    cost_full numeric(18,6),
    subvention jsonb,
    pool jsonb,
    restored_id character varying(32)
);

--
-- Name: orders_0 orders_0_pkey; Type: CONSTRAINT; Schema: public; Owner: taximeter
--

ALTER TABLE ONLY orders_0
    ADD CONSTRAINT orders_0_pkey PRIMARY KEY (park_id, id);


--
-- Name: idx_orders_0_date_booking_park_id; Type: INDEX; Schema: public; Owner: taximeter
--

CREATE INDEX idx_orders_0_date_booking_park_id ON orders_0 USING btree (date_booking DESC, park_id);


--
-- Name: idx_orders_0_date_create; Type: INDEX; Schema: public; Owner: taximeter
--

CREATE INDEX idx_orders_0_date_create ON orders_0 USING btree (date_create DESC);


--
-- Name: idx_orders_0_date_end; Type: INDEX; Schema: public; Owner: taximeter
--

CREATE INDEX idx_orders_0_date_end ON orders_0 USING btree (date_end DESC);


--
-- Name: idx_orders_0_date_last_change; Type: INDEX; Schema: public; Owner: taximeter
--

CREATE INDEX idx_orders_0_date_last_change ON orders_0 USING btree (date_last_change DESC) WHERE (date_last_change IS NOT NULL);


--
-- Name: idx_orders_0_driver_signal; Type: INDEX; Schema: public; Owner: taximeter
--

CREATE INDEX idx_orders_0_driver_signal ON orders_0 USING btree (driver_signal);


--
-- Name: idx_orders_0_number; Type: INDEX; Schema: public; Owner: taximeter
--

CREATE INDEX idx_orders_0_number ON orders_0 USING btree (number DESC);


--
-- Name: idx_orders_0_old_uuid; Type: INDEX; Schema: public; Owner: taximeter
--

CREATE INDEX idx_orders_0_old_uuid ON orders_0 USING btree (old_uuid) WHERE (old_uuid IS NOT NULL);


--
-- Name: idx_orders_0_park_id_driver_id_date_booking; Type: INDEX; Schema: public; Owner: taximeter
--

CREATE INDEX idx_orders_0_park_id_driver_id_date_booking ON orders_0 USING btree (park_id, driver_id, date_booking DESC);


--
-- Name: idx_orders_0_payment; Type: INDEX; Schema: public; Owner: taximeter
--

CREATE INDEX idx_orders_0_payment ON orders_0 USING btree (payment);


--
-- Name: idx_orders_0_phone1; Type: INDEX; Schema: public; Owner: taximeter
--

CREATE INDEX idx_orders_0_phone1 ON orders_0 USING btree (phone1) WHERE (phone1 IS NOT NULL);


--
-- Name: idx_orders_0_phone2; Type: INDEX; Schema: public; Owner: taximeter
--

CREATE INDEX idx_orders_0_phone2 ON orders_0 USING btree (phone2) WHERE (phone2 IS NOT NULL);


--
-- Name: idx_orders_0_phone3; Type: INDEX; Schema: public; Owner: taximeter
--

CREATE INDEX idx_orders_0_phone3 ON orders_0 USING btree (phone3) WHERE (phone3 IS NOT NULL);


--
-- Name: idx_orders_0_provider; Type: INDEX; Schema: public; Owner: taximeter
--

CREATE INDEX idx_orders_0_provider ON orders_0 USING btree (provider);


--
-- Name: idx_orders_0_rule_type_id; Type: INDEX; Schema: public; Owner: taximeter
--

CREATE INDEX idx_orders_0_rule_type_id ON orders_0 USING btree (rule_type_id);


--
-- Name: idx_orders_0_rule_work_id; Type: INDEX; Schema: public; Owner: taximeter
--

CREATE INDEX idx_orders_0_rule_work_id ON orders_0 USING btree (rule_work_id) WHERE (rule_work_id IS NOT NULL);
