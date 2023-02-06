ALTER TABLE eats_compensations_matrix.compensation_packs
    ADD COLUMN IF NOT EXISTS delivery_class INTEGER NOT NULL DEFAULT 255;

comment on column eats_compensations_matrix.compensation_packs.delivery_class is 'Классы доставки, к которым применим пак компенсаций';
