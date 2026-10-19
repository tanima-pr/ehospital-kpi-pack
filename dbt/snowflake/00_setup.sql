-- One-time Snowflake setup for the eHospital dbt project (run as ACCOUNTADMIN).
-- Least privilege: dbt gets its own role, an X-Small auto-suspending warehouse, one database.
use role accountadmin;

create warehouse if not exists DBT_WH
  warehouse_size = 'XSMALL' auto_suspend = 60 auto_resume = true initially_suspended = true;

create database if not exists EHOSPITAL;
create schema   if not exists EHOSPITAL.ANALYTICS;

create role if not exists DBT_ROLE;
grant usage on warehouse DBT_WH to role DBT_ROLE;
grant usage on database EHOSPITAL to role DBT_ROLE;
grant all on schema EHOSPITAL.ANALYTICS to role DBT_ROLE;
grant create schema on database EHOSPITAL to role DBT_ROLE;
grant role DBT_ROLE to role SYSADMIN;   -- roll custom role up to SYSADMIN so admins can see its objects

-- Service user: key-pair auth only, no password.
create user if not exists DBT_USER type = service default_role = DBT_ROLE default_warehouse = DBT_WH;
grant role DBT_ROLE to user DBT_USER;
-- alter user DBT_USER set rsa_public_key = '<public key, one line>';
