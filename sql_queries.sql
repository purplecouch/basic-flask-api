-- SQLite
SELECT 
CASE_NUMBER
, CASE_STATUS
, VISA_CLASS
, EMPLOYMENT_START_DATE
, EMPLOYMENT_END_DATE
, EMPLOYER_NAME
, EMPLOYER_BUSINESS_DBA
, EMPLOYER_ADDRESS
, EMPLOYER_CITY
, EMPLOYER_STATE
, EMPLOYER_POSTAL_CODE
, EMPLOYER_COUNTRY
, EMPLOYER_PROVINCE
, EMPLOYER_PHONE
, EMPLOYER_PHONE_EXT
, JOB_TITLE
, SOC_CODE
, SOC_NAME
, NAICS_CODE
, TOTAL_WORKERS
, FULL_TIME_POSITION
, PREVAILING_WAGE
, PW_UNIT_OF_PAY
, PW_WAGE_LEVEL
, PW_SOURCE
, PW_SOURCE_YEAR
, PW_SOURCE_OTHER
, WAGE_RATE_OF_PAY_FROM
, WAGE_RATE_OF_PAY_TO
, WAGE_UNIT_OF_PAY
, H1B_DEPENDENT
, WILLFUL_VIOLATOR
, SUPPORT_H1B
, LABOR_CON_AGREE
, PUBLIC_DISCLOSURE_LOCATION
, WORKSITE_CITY
, WORKSITE_COUNTY
, WORKSITE_STATE
, WORKSITE_POSTAL_CODE
, ORIGINAL_CERT_DATE
FROM `h1b_data` 
limit 10;

-- SQLite
SELECT 
PW_UNIT_OF_PAY, count(*)
FROM `h1b_data` 
group by PW_UNIT_OF_PAY;

SELECT 
WAGE_UNIT_OF_PAY, count(*)
FROM `h1b_data` 
group by WAGE_UNIT_OF_PAY;

SELECT 
FULL_TIME_POSITION, count(*)
FROM `h1b_data` 
group by FULL_TIME_POSITION;

--What are workers with a certain job title or job code getting paid in my company?
SELECT
EMPLOYER_NAME
,WORKSITE_CITY
,WORKSITE_STATE
,WORKSITE_POSTAL_CODE
,WAGE_RATE_OF_PAY_FROM
,WAGE_RATE_OF_PAY_TO
,SOC_CODE
,SOC_NAME
,JOB_TITLE
from 
h1b_data where CASE_STATUS = 'CERTIFIED' 
AND PW_UNIT_OF_PAY = 'Year' and WAGE_UNIT_OF_PAY = 'Year' and FULL_TIME_POSITION='Y'
AND SOC_CODE = '15-1132'
AND EMPLOYER_NAME = 'MICROSOFT CORPORATION'
AND WORKSITE_CITY = 'REDMOND'
ORDER BY WAGE_RATE_OF_PAY_FROM DESC;

select count(distinct WORKSITE_CITY) from h1b_data;



