create table orders (
      id int AUTO_INCREMENT PRIMARY KEY,
      order_nr varchar(100) NOT NULL,
      courier_id int NOT NULL default -1,
      place_id int NOT NULL,
      courier_assigned_at timestamp NULL,
      payment_service varchar(100) NULL,
      status int default 0,
      is_asap bool default 1,
      arrived_to_customer_at timestamp NULL,
      call_center_confirmed_at timestamp NULL,
      place_confirmed_at timestamp NULL,
      created_at timestamp default now()
);

create table places (
      id int AUTO_INCREMENT PRIMARY KEY,
      address_street varchar(100) NOT NULL,
      brand_id int NOT NULL,
      region_id int default -1
);

create table couriers (
      id int AUTO_INCREMENT PRIMARY KEY,
      username varchar(100) NOT NULL
);

create table brands (
      id int AUTO_INCREMENT PRIMARY KEY,
      name varchar(100) NOT NULL
);

create table regions (
      id int AUTO_INCREMENT PRIMARY KEY,
      name varchar(100) NOT NULL
);

create table order_cancels (
      id int AUTO_INCREMENT PRIMARY KEY,
        order_id int NOT NULL,
        reason_id int
);

create table order_cancel_tasks (
      id int AUTO_INCREMENT PRIMARY KEY,
order_cancel_id int NOT NULL,
reaction_id int NOT NULL
);

create table order_cancel_reasons(
    id int,
    group_id int
);
