CREATE TABLE IF NOT EXISTS public.auth_user (
id SERIAL PRIMARY KEY,
username TEXT);

CREATE TABLE IF NOT EXISTS public.compendium_customuser (
    user_ptr_id INTEGER,
    piece boolean
);

CREATE TABLE IF NOT EXISTS public.compendium_reserves (
    user_id INTEGER,
    "limit" float,
    now_bo float
);


INSERT INTO public.auth_user VALUES (1,'liambaev');
INSERT INTO public.compendium_customuser VALUES (1,true);
INSERT INTO public.compendium_reserves VALUES (1,1234,4321);
