CREATE TABLE dois (
    id UUID PRIMARY KEY,
    doi TEXT NOT NULL, 
    published_date DATE NOT NULL,
    item_number INTEGER,
    publisher_place TEXT NOT NULL,
    std_designator TEXT NOT NULL,
    standards_body_acronym TEXT NOT NULL,
    depositor_name TEXT NOT NULL,
    registrant TEXT NOT NULL,
    publisher_name TEXT NOT NULL,
    standards_body_name TEXT NOT NULL,
    organization TEXT NOT NULL,
    title TEXT NOT NULL,
    resource_link TEXT NOT NULL,
    email_address TEXT NOT NULL,
    batch_id UUID NOT NULL,
    submitted_at TIMESTAMP NOT NULL,
    created_by TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_by TEXT NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    version INTEGER NOT NULL,

    UNIQUE(doi, std_designator)
);

CREATE INDEX doi_idx ON dois (doi);
CREATE INDEX title_idx ON dois (title);

CREATE TABLE dois_audit (
    id UUID NOT NULL,
    action TEXT NOT NULL check (action in ('INSERT','DELETE','UPDATE')),
    doi_old TEXT,
    doi_new TEXT NOT NULL, 
    published_date_old DATE,
    published_date_new DATE NOT NULL,
    item_number_old INTEGER,
    item_number_new INTEGER,
    publisher_place_old TEXT,
    publisher_place_new TEXT NOT NULL,
    std_designator_old TEXT,
    std_designator_new TEXT NOT NULL,
    standards_body_acronym_old TEXT,
    standards_body_acronym_new TEXT NOT NULL,
    depositor_name_old TEXT,
    depositor_name_new TEXT NOT NULL,
    registrant_old TEXT,
    registrant_new TEXT NOT NULL,
    publisher_name_old TEXT,
    publisher_name_new TEXT NOT NULL,
    standards_body_name_old TEXT,
    standards_body_name_new TEXT NOT NULL,
    organization_old TEXT,
    organization_new TEXT NOT NULL,
    title_old TEXT,
    title_new TEXT NOT NULL,
    resource_link_old TEXT,
    resource_link_new TEXT NOT NULL,
    email_address_old TEXT,
    email_address_new TEXT NOT NULL,
    batch_id_old UUID,
    batch_id_new UUID NOT NULL,
    submitted_at_old TIMESTAMP,
    submitted_at_new TIMESTAMP NOT NULL,
    created_by TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_by TEXT NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    version INTEGER NOT NULL,
    query text,
    PRIMARY KEY (id, version)
);


CREATE FUNCTION dois_audit_func() RETURNS trigger AS $body$
DECLARE
    v_old_data TEXT;
    v_new_data TEXT;
BEGIN
    if (TG_OP = 'UPDATE') then
        insert into dois_audit (id,action,doi_old,doi_new,published_date_old,published_date_new,item_number_old,item_number_new,publisher_place_old,publisher_place_new,std_designator_old,std_designator_new,standards_body_acronym_old,standards_body_acronym_new,depositor_name_old,depositor_name_new,registrant_old,registrant_new,publisher_name_old,publisher_name_new,standards_body_name_old,standards_body_name_new,organization_old,organization_new,title_old,title_new,resource_link_old,resource_link_new,email_address_old,email_address_new,batch_id_old,batch_id_new,submitted_at_old,submitted_at_new,created_by,created_at,updated_by,updated_at,version,query)
        values (
            NEW.id,
            TG_OP,
            OLD.doi,
            NEW.doi,
            OLD.published_date,
            NEW.published_date,
            OLD.item_number,
            NEW.item_number,
            OLD.publisher_place,
            NEW.publisher_place,
            OLD.std_designator,
            NEW.std_designator,
            OLD.standards_body_acronym,
            NEW.standards_body_acronym,
            OLD.depositor_name,
            NEW.depositor_name,
            OLD.registrant,
            NEW.registrant,
            OLD.publisher_name,
            NEW.publisher_name,
            OLD.standards_body_name,
            NEW.standards_body_name,
            OLD.organization,
            NEW.organization,
            OLD.title,
            NEW.title,
            OLD.resource_link,
            NEW.resource_link,
            OLD.email_address,
            NEW.email_address,
            OLD.batch_id,
            NEW.batch_id,
            OLD.submitted_at,
            NEW.submitted_at,
            NEW.created_by,
            NEW.created_at,
            NEW.updated_by,
            NEW.updated_at,
            NEW.version,
            current_query());

        RETURN NEW;
    elsif (TG_OP = 'DELETE') then
        insert into dois_audit (id,action,doi_old,doi_new,published_date_old,published_date_new,item_number_old,item_number_new,publisher_place_old,publisher_place_new,std_designator_old,std_designator_new,standards_body_acronym_old,standards_body_acronym_new,depositor_name_old,depositor_name_new,registrant_old,registrant_new,publisher_name_old,publisher_name_new,standards_body_name_old,standards_body_name_new,organization_old,organization_new,title_old,title_new,resource_link_old,resource_link_new,email_address_old,email_address_new,batch_id_old,batch_id_new,submitted_at_old,submitted_at_new,created_by,created_at,updated_by,updated_at,version,query)
        values (
            OLD.id,
            TG_OP,
            OLD.doi,
            OLD.doi,
            OLD.published_date,
            OLD.published_date,
            OLD.item_number,
            OLD.item_number,
            OLD.publisher_place,
            OLD.publisher_place,
            OLD.std_designator,
            OLD.std_designator,
            OLD.standards_body_acronym,
            OLD.standards_body_acronym,
            OLD.depositor_name,
            OLD.depositor_name,
            OLD.registrant,
            OLD.registrant,
            OLD.publisher_name,
            OLD.publisher_name,
            OLD.standards_body_name,
            OLD.standards_body_name,
            OLD.organization,
            OLD.organization,
            OLD.title,
            OLD.title,
            OLD.resource_link,
            OLD.resource_link,
            OLD.email_address,
            OLD.email_address,
            OLD.batch_id,
            OLD.batch_id,
            OLD.submitted_at,
            OLD.submitted_at,
            OLD.created_by,
            OLD.created_at,
            OLD.updated_by,
            OLD.updated_at,
            OLD.version + 1,
            current_query());
        RETURN OLD;
    elsif (TG_OP = 'INSERT') then
        insert into dois_audit (id,action,doi_old,doi_new,published_date_old,published_date_new,item_number_old,item_number_new,publisher_place_old,publisher_place_new,std_designator_old,std_designator_new,standards_body_acronym_old,standards_body_acronym_new,depositor_name_old,depositor_name_new,registrant_old,registrant_new,publisher_name_old,publisher_name_new,standards_body_name_old,standards_body_name_new,organization_old,organization_new,title_old,title_new,resource_link_old,resource_link_new,email_address_old,email_address_new,batch_id_old,batch_id_new,submitted_at_old,submitted_at_new,created_by,created_at,updated_by,updated_at,version,query)
        values (
            NEW.id,
            TG_OP,
            NULL,
            NEW.doi,
            NULL,
            NEW.published_date,
            NULL,
            NEW.item_number,
            NULL,
            NEW.publisher_place,
            NULL,
            NEW.std_designator,
            NULL,
            NEW.standards_body_acronym,
            NULL,
            NEW.depositor_name,
            NULL,
            NEW.registrant,
            NULL,
            NEW.publisher_name,
            NULL,
            NEW.standards_body_name,
            NULL,
            NEW.organization,
            NULL,
            NEW.title,
            NULL,
            NEW.resource_link,
            NULL,
            NEW.email_address,
            NULL,
            NEW.batch_id,
            NULL,
            NEW.submitted_at,
            NEW.created_by,
            NEW.created_at,
            NEW.updated_by,
            NEW.updated_at,
            NEW.version,
            current_query());
        RETURN NEW;
    else
        RAISE WARNING '[DOIS_AUDIT_FUNC] - Other action occurred: %, at %',TG_OP,now();
        RETURN NULL;
    end if;

EXCEPTION
    WHEN data_exception THEN
        RAISE WARNING '[DOIS_AUDIT_FUNC] - UDF ERROR [DATA EXCEPTION] - SQLSTATE: %, SQLERRM: %',SQLSTATE,SQLERRM;
        RETURN NULL;
    WHEN unique_violation THEN
        RAISE WARNING '[DOIS_AUDIT_FUNC] - UDF ERROR [UNIQUE] - SQLSTATE: %, SQLERRM: %',SQLSTATE,SQLERRM;
        RETURN NULL;
    WHEN others THEN
        RAISE WARNING '[DOIS_AUDIT_FUNC] - UDF ERROR [OTHER] - SQLSTATE: %, SQLERRM: %',SQLSTATE,SQLERRM;
        RETURN NULL;
END;
$body$
LANGUAGE plpgsql;


CREATE TRIGGER dois_audit_trigger
AFTER INSERT OR UPDATE OR DELETE ON dois
FOR EACH ROW EXECUTE PROCEDURE dois_audit_func();
