# Libraries
import sqlite3
import logging
import datetime

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class GuardianDatabase:
    def __init__(self):
        """
        Constructor for the GuardianDatabase class.
        Initializes the database connection and cursor as None.
        These will be set when the 'connect' method is called.
        """
        # Initialize the database connection attribute to None.
        self.__connection = None
        
        # Initialize the database cursor attribute to None.
        self.__cursor = None

    def connect(self):
        """
        Establishes a connection to the SQLite database and initializes a cursor for database operations.
        """
        # Connect to the SQLite database; 'guardian_database.db' will be created if it doesn't exist
        self.__connection = sqlite3.connect('guardian_database.db')
        
        # Create a cursor object using the connection; this cursor is used to execute SQL queries
        self.__cursor = self.__connection.cursor()


    def close(self):
        """
        Closes the database cursor and connection to ensure no memory leaks or unwanted open connections.
        """
        # Close the cursor; this prevents further SQL operations using this cursor
        self.__cursor.close()
        
        # Close the database connection; this releases the database resources
        self.__connection.close()

    
    def initialize_database(self):
        """
        Initializes the database by setting up the required tables.
        If the tables already exist, this method ensures they are not created again.
        """

        # Connect to the database before any operations.
        self.connect()
        
        try:
            # Start transaction
            self.__cursor.execute('BEGIN TRANSACTION;')
        
            # Create the DWH_D_GUARDIAN table
            self.__cursor.execute('''
                CREATE TABLE IF NOT EXISTS DWH_D_GUARDIAN (
                    ID_D_GUARDIAN INTEGER PRIMARY KEY AUTOINCREMENT,
                    TXT_URL TEXT NOT NULL,
                    TXT_CATEGORY TEXT NULL,
                    TXT_HEADLINE TEXT NULL,
                    TXT_AUTHOR TEXT NULL,
                    TXT_TEXT TEXT NULL,
                    DAT_VALID_FROM DATETIME NOT NULL,
                    DAT_VALID_TO DATETIME,
                    BOOL_IS_CURRENT BOOLEAN
                )
            ''')

            # Create the DWH_D_DATE table
            self.__cursor.execute('''
                CREATE TABLE IF NOT EXISTS DWH_D_DATE (
                    ID_D_DATE DATE,
                    YEAR INTEGER,
                    QUARTER INTEGER,
                    MONTH INTEGER,
                    DAY INTEGER,
                    WEEKDAY_NAME TEXT,
                    IS_WEEKEND BOOLEAN
                )
            ''')

            # Check if there's already data in DWH_D_DATE
            self.__cursor.execute("SELECT COUNT(*) FROM DWH_D_DATE;")
            count = self.__cursor.fetchone()[0]

            # If the table is empty, proceed with insertion
            if count == 0:
                start_date = datetime.date(2023, 1, 1)
                end_date = datetime.date(2030, 12, 31)
                current_date = start_date

                while current_date <= end_date:
                    year = current_date.year
                    month = current_date.month
                    day = current_date.day
                    weekday_name = current_date.strftime('%A')
                    is_weekend = 1 if weekday_name in ['Saturday', 'Sunday'] else 0
                    quarter = (month - 1) // 3 + 1  # Calculate the quarter
                    
                    self.__cursor.execute('''
                        INSERT INTO DWH_D_DATE (ID_D_DATE, YEAR, QUARTER, MONTH, DAY, WEEKDAY_NAME, IS_WEEKEND)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (current_date, year, quarter, month, day, weekday_name, is_weekend))
                    
                    current_date += datetime.timedelta(days=1)

            # Create the DWH_FT_GUARDIAN table
            self.__cursor.execute('''
                CREATE TABLE IF NOT EXISTS DWH_FT_GUARDIAN (
                    ID_D_GUARDIAN INTEGER NOT NULL,
                    ID_D_DATE DATE NOT NULL
                )
            ''')

            # Create the DTM_V_FT_GUARDIAN view
            self.__cursor.execute('''
                CREATE VIEW IF NOT EXISTS DTM_V_FT_GUARDIAN AS
                SELECT 
                    ft."ID_D_GUARDIAN"          AS "ID Guardian"
                    ,ft."ID_D_DATE"             AS "ID Date"
                FROM DWH_FT_GUARDIAN AS ft
                WHERE ft."ID_D_GUARDIAN" IN (SELECT d."ID_D_GUARDIAN" FROM DWH_D_GUARDIAN AS d WHERE d.BOOL_IS_CURRENT = 1);
            ''')

            # Create DTM_V_D_GUARDIAN view
            self.__cursor.execute('''
                CREATE VIEW IF NOT EXISTS DTM_V_D_GUARDIAN AS
                SELECT 
                    d."ID_D_GUARDIAN"           AS "ID Guardian"
                    ,d."TXT_URL"                AS "URL"
                    ,d."TXT_CATEGORY"           AS "Category"
                    ,d."TXT_HEADLINE"           AS "Headline"
                    ,d."TXT_AUTHOR"             AS "Author"
                    ,d."TXT_TEXT"               AS "Text"
                FROM DWH_D_GUARDIAN AS d
                WHERE d.ID_D_GUARDIAN IN (SELECT ft."ID Guardian" FROM DTM_V_FT_GUARDIAN AS ft);
            ''')

            # Create DTM_V_D_DATE view
            self.__cursor.execute('''
                CREATE VIEW IF NOT EXISTS DTM_V_D_DATE AS
                SELECT
                    d."ID_D_DATE"               AS "ID Date"
                    ,d."YEAR"                   AS "Year"
                    ,d."QUARTER"                AS "Quarter"
                    ,d."MONTH"                  AS "Month"
                    ,d."DAY"                    AS "Day"
                    ,d."WEEKDAY_NAME"           AS "Weekday Name"
                    ,d."IS_WEEKEND"             AS "Is Weekend"
                FROM DWH_D_DATE AS d
                WHERE
                    d.ID_D_DATE >= (SELECT MIN(ft."ID Date") FROM DTM_V_FT_GUARDIAN AS ft)
                    AND d.ID_D_DATE <= (SELECT MAX(ft."ID Date") FROM DTM_V_FT_GUARDIAN AS ft);
            ''')

            # Commit transaction
            self.__cursor.execute('COMMIT;')
        except sqlite3.Error as e:
            # Rollback if there's an error
            self.__connection.rollback()
            print(f"SQLite error: {e}")
        finally:
            # Always close the connection at the end
            self.close()
    
    def load(self, dataframe):
        """
        Loads data from the provided dataframe into the database.

        Parameters:
        - dataframe (pandas.DataFrame): The dataframe containing the data to be loaded.

        Note: 
        The data is loaded into a table named 'LND_GUARDIAN'. If the table already exists, 
        the existing data will be replaced by the new data from the dataframe.
        """

        # Connect to the database before loading the data.
        self.connect()
        
        try:
            # Insert data from the dataframe into the LND_GUARDIAN table
            dataframe.to_sql('LND_GUARDIAN', self.__connection, if_exists='replace', index=True)
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
        finally:
            # Always close the connection at the end
            self.close()
    
    def transform(self):
        """
        This method transforms data by connecting to the database, 
        making the necessary changes, and updating records.
        """
        
        # Connect to the database before loading the data.
        self.connect()

        try:
            # Start transaction
            self.__cursor.execute('BEGIN TRANSACTION;')

            # Get the count before changes
            self.__cursor.execute('SELECT COUNT(*) FROM DWH_D_GUARDIAN WHERE BOOL_IS_CURRENT = 1;')
            initial_count = self.__cursor.fetchone()[0]

            # Step 1: Expire records that have actual changes
            self.__cursor.execute('''
                UPDATE DWH_D_GUARDIAN
                SET DAT_VALID_TO = CURRENT_TIMESTAMP, BOOL_IS_CURRENT = 0
                WHERE
                    TXT_URL IN (
                        SELECT
                            dwh.TXT_URL
                        FROM DWH_D_GUARDIAN AS dwh
                        JOIN LND_GUARDIAN AS lnd
                            ON dwh.TXT_URL = lnd."index"
                        WHERE
                            dwh.TXT_CATEGORY != lnd."category"
                            OR dwh.TXT_HEADLINE != lnd."headline"
                            OR dwh.TXT_AUTHOR != lnd."author"
                            OR dwh.TXT_TEXT != lnd."text"
                    )
                    AND BOOL_IS_CURRENT = 1;
            ''')

            # Step 2: Insert new or changed records from the landing table to dimension table
            self.__cursor.execute('''
                INSERT INTO DWH_D_GUARDIAN
                (
                    TXT_URL
                    ,TXT_CATEGORY
                    ,TXT_HEADLINE
                    ,TXT_AUTHOR
                    ,TXT_TEXT
                    ,DAT_VALID_FROM
                    ,DAT_VALID_TO
                    ,BOOL_IS_CURRENT
                )
                SELECT
                    lnd."index"             AS TXT_URL
                    ,lnd."category"         AS TXT_CATEGORY
                    ,lnd."headline"         AS TXT_HEADLINE
                    ,lnd."author"           AS TXT_AUTHOR
                    ,lnd."text"             AS TXT_TEXT
                    ,CURRENT_TIMESTAMP      AS DAT_VALID_FROM
                    ,NULL                   AS DAT_VALID_TO
                    ,1                      AS BOOL_IS_CURRENT
                FROM LND_GUARDIAN AS lnd
                LEFT JOIN DWH_D_GUARDIAN dwh
                    ON lnd."index" = dwh.TXT_URL
                    AND dwh.BOOL_IS_CURRENT = 1
                WHERE
                    dwh.TXT_URL IS NULL 
                    OR dwh.TXT_CATEGORY != lnd."category"
                    OR dwh.TXT_HEADLINE != lnd."headline"
                    OR dwh.TXT_AUTHOR != lnd."author"
                    OR dwh.TXT_TEXT != lnd."text";
            ''')

            # Step 3: Insert new records from the landing table to dimension table
            self.__cursor.execute('''
                INSERT OR IGNORE INTO DWH_FT_GUARDIAN (ID_D_GUARDIAN, ID_D_DATE)
                SELECT
                    dwh."ID_D_GUARDIAN"
                    ,date(lnd."date")
                FROM DWH_D_GUARDIAN AS dwh
                INNER JOIN LND_GUARDIAN AS lnd
                    ON dwh.TXT_URL = lnd."index"
                WHERE
                    BOOL_IS_CURRENT = 1
                    AND NOT EXISTS (SELECT 1 FROM DWH_FT_GUARDIAN ft WHERE ft.ID_D_GUARDIAN = dwh.ID_D_GUARDIAN);
            ''')

            # Get the count after changes
            self.__cursor.execute('SELECT COUNT(*) FROM DWH_D_GUARDIAN WHERE BOOL_IS_CURRENT = 1;')
            final_count = self.__cursor.fetchone()[0]

            # Calculate the difference
            new_records_count = final_count - initial_count

            logging.info(f"{new_records_count} new records added to DWH_D_GUARDIAN!")

            # Commit transaction
            self.__cursor.execute('COMMIT;')
        except sqlite3.Error as e:
            # Rollback if there's an error
            self.__connection.rollback()
            print(f"SQLite error: {e}")
        finally:
            # Always close the connection at the end
            self.close()
    
    def has_data(self) -> bool:
        """
        Checks if the DWH_D_GUARDIAN table has any data.

        Returns:
        - bool: True if the table has data, False otherwise.

        This method connects to the database, retrieves a count of the records in the
        DWH_D_GUARDIAN table, and then determines if the table is empty based on that count.
        """

        # Connect to the database before loading the data.
        self.connect()

        try:
            count = self.__cursor.execute("SELECT COUNT(*) FROM DWH_D_GUARDIAN;").fetchone()[0]
            return count > 0
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
            return False  # Return a default value
        finally:
            self.close()