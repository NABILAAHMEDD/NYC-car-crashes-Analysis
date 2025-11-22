-- MySQL Table Creation Script for NYC Car Crashes Data (OPTIMIZED)
-- Only includes columns actually used by the application

-- Drop table if exists (for re-running script)
DROP TABLE IF EXISTS crashes;

-- Create the crashes table with only used columns
CREATE TABLE crashes (
    COLLISION_ID BIGINT,
    CRASH_DATE DATETIME,
    PERSON_ID VARCHAR(50),
    PERSON_TYPE VARCHAR(50),
    PERSON_INJURY VARCHAR(50),
    BOROUGH VARCHAR(50),
    LATITUDE FLOAT,
    LONGITUDE FLOAT,
    `NUMBER OF PERSONS INJURED` INT,
    `NUMBER OF PERSONS KILLED` INT,
    `CONTRIBUTING FACTOR VEHICLE 1` VARCHAR(200),
    `VEHICLE TYPE CODE 1` VARCHAR(100),
    HOUR INT,
    DAY INT,
    season VARCHAR(20),
    SAFETY_USED INT,
    YEAR INT GENERATED ALWAYS AS (YEAR(CRASH_DATE)) STORED  -- Computed column for year
);

-- Create indexes for better query performance
CREATE INDEX IX_COLLISION_ID ON crashes(COLLISION_ID);
CREATE INDEX IX_CRASH_DATE ON crashes(CRASH_DATE);
CREATE INDEX IX_YEAR ON crashes(YEAR);
CREATE INDEX IX_BOROUGH ON crashes(BOROUGH);
CREATE INDEX IX_PERSON_TYPE ON crashes(PERSON_TYPE);
CREATE INDEX IX_LAT_LON ON crashes(LATITUDE, LONGITUDE);

SELECT 'Table created successfully!' as Status;

