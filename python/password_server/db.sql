-- SEQUENCE: public.password_id_seq

-- DROP SEQUENCE IF EXISTS public.password_id_seq;

CREATE SEQUENCE IF NOT EXISTS public.password_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 2147483647
    CACHE 1
    OWNED BY password.id;

ALTER SEQUENCE public.password_id_seq
    OWNER TO postgres;
    
    
    
-- Table: public.password

-- DROP TABLE IF EXISTS public.password;

CREATE TABLE IF NOT EXISTS public.password
(
    id integer NOT NULL DEFAULT nextval('password_id_seq'::regclass),
    password character varying(50) COLLATE pg_catalog."default" NOT NULL,
    source character varying(50) COLLATE pg_catalog."default" NOT NULL
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.password
    OWNER to postgres;
-- Index: ind_pass_source_pass

-- DROP INDEX IF EXISTS public.ind_pass_source_pass;

CREATE UNIQUE INDEX IF NOT EXISTS ind_pass_source_pass
    ON public.password USING btree
    (source COLLATE pg_catalog."default" ASC NULLS LAST, password COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;
    
    
    





-- DROP SEQUENCE IF EXISTS public.used_id_seq;

CREATE SEQUENCE IF NOT EXISTS public.used_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 2147483647
    CACHE 1;

ALTER SEQUENCE public.used_id_seq
    OWNER TO postgres;
    
CREATE TABLE IF NOT EXISTS public.USED
(
    id integer NOT NULL DEFAULT nextval('used_id_seq'::regclass),
    password character varying(50) NOT NULL,
    target character varying(50) NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS ind_used_target_pass
    ON USED(target, password)
;








