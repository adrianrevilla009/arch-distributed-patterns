create table orders(id serial primary key, item text not null);
create table outbox(id uuid primary key default gen_random_uuid(), aggregate_id text, type text, payload jsonb);
-- app does: begin; insert into orders ...; insert into outbox ...; commit;
