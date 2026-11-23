"""
The database loan.db consists of 5 tables:
   1. customers - table containing customer data
   2. loans - table containing loan data pertaining to customers
   3. credit - table containing credit and creditscore data pertaining to customers
   4. repayments - table containing loan repayment data pertaining to customers
   5. months - table containing month name and month ID data

You are required to make use of your knowledge in SQL to query the database object (saved as loan.db) and return the requested information.
Simply fill in the vacant space wrapped in triple quotes per question (each function represents a question)

NOTE:
The database will be reset when grading each section. Any changes made to the database in the previous `SQL` section can be ignored.
Each question in this section is isolated unless it is stated that questions are linked.
Remember to clean your data

"""


def question_1():
    """
    Make use of a JOIN to find the `AverageIncome` per `CustomerClass`
    """

    qry = """SELECT cr.CustomerClass, AVG(c.Income) AS AverageIncome FROM (SELECT DISTINCT * FROM customers) AS c INNER JOIN (SELECT DISTINCT * FROM credit) AS cr ON c.CustomerID = cr.CustomerID GROUP BY cr.CustomerClass ORDER BY cr.CustomerClass"""

    return qry


def question_2():
    """
    Make use of a JOIN to return a breakdown of the number of 'RejectedApplications' per 'Province'.
    Ensure consistent use of either the abbreviated or full version of each province, matching the format found in the customer table.
    """

    qry = """    
    SELECT
        CASE c.Region
                WHEN 'EasternCape'   THEN 'EC'
                WHEN 'FreeState'     THEN 'FS'
                WHEN 'Gauteng'       THEN 'GT'
                WHEN 'KwaZulu-Natal' THEN 'KZN'
                WHEN 'Limpopo'       THEN 'LP'
                WHEN 'Mpumalanga'    THEN 'MP'
                WHEN 'NorthernCape'  THEN 'NC'
                WHEN 'NorthWest'     THEN 'NW'
                WHEN 'WesternCape'   THEN 'WC'
                ELSE c.Region
            END AS Province,
        COUNT(*) AS RejectedApplications
    FROM (SELECT DISTINCT * FROM customers) AS c
    INNER JOIN (SELECT DISTINCT * FROM loans) AS l
        ON c.CustomerID = l.CustomerID
    WHERE l.ApprovalStatus = 'Rejected'
    GROUP BY Province
    ORDER BY Province
    """

    return qry


def question_3():
    """
    Making use of the `INSERT` function, create a new table called `financing` which will include the following columns:
    `CustomerID`,`Income`,`LoanAmount`,`LoanTerm`,`InterestRate`,`ApprovalStatus` and `CreditScore`

    Do not return the new table, just create it.
    """

    qry = """
    CREATE OR REPLACE TABLE financing (
        CustomerID     INTEGER,
        Income         INTEGER,
        LoanAmount     INTEGER,
        LoanTerm       INTEGER,
        InterestRate   FLOAT,
        ApprovalStatus VARCHAR,
        CreditScore    INTEGER
    );
    INSERT INTO financing
    SELECT DISTINCT
        c.CustomerID, c.Income,
        l.LoanAmount, l.LoanTerm, l.InterestRate, l.ApprovalStatus,
        cr.CreditScore
    FROM customers AS c
    INNER JOIN loans  AS l  ON c.CustomerID = l.CustomerID
    INNER JOIN credit AS cr ON c.CustomerID = cr.CustomerID;
    """

    return qry


# Question 4 and 5 are linked


def question_4():
    """
    Using a `CROSS JOIN` and the `months` table, create a new table called `timeline` that sumarises Repayments per customer per month.
    Columns should be: `CustomerID`, `MonthName`, `NumberOfRepayments`, `AmountTotal`.
    Repayments should only occur between 6am and 6pm London Time.
    Null values to be filled with 0.

    Hint: there should be 12x CustomerID = 1.
    """

    qry = """
        CREATE OR REPLACE TABLE timeline AS
    WITH london_repayments AS (
        SELECT
            CustomerID,
            Amount,
            timezone(
                'Europe/London',
                timezone(
                    CASE TimeZone
                        WHEN 'PST' THEN 'America/Los_Angeles'
                        WHEN 'PNT' THEN 'America/Phoenix'
                        WHEN 'CST' THEN 'America/Chicago'
                        WHEN 'IST' THEN 'Asia/Kolkata'
                        WHEN 'JST' THEN 'Asia/Tokyo'
                        WHEN 'CET' THEN 'CET'
                        WHEN 'EET' THEN 'EET'
                        WHEN 'GMT' THEN 'GMT'
                        ELSE 'UTC'
                    END,
                    RepaymentDate
                )
            ) AS LondonTime
        FROM repayments
    ),
    monthly AS (
        SELECT
            CustomerID,
            month(LondonTime) AS MonthID,
            COUNT(*)          AS NumberOfRepayments,
            SUM(Amount)       AS AmountTotal
        FROM london_repayments
        WHERE hour(LondonTime) >= 6 AND hour(LondonTime) < 18
        GROUP BY CustomerID, month(LondonTime)
    )
    SELECT
        c.CustomerID,
        m.MonthName,
        COALESCE(r.NumberOfRepayments, 0) AS NumberOfRepayments,
        COALESCE(r.AmountTotal, 0)        AS AmountTotal
    FROM (SELECT DISTINCT CustomerID FROM customers) AS c
    CROSS JOIN months AS m
    LEFT JOIN monthly AS r
        ON r.CustomerID = c.CustomerID
       AND r.MonthID    = m.MonthID
    ORDER BY c.CustomerID, m.MonthID;
    """

    return qry


def question_5():
    """
    Make use of conditional aggregation to pivot the `timeline` table such that the columns are as follows:
    `CustomerID`, `JanuaryRepayments`, `JanuaryTotal`,...,`DecemberRepayments`, `DecemberTotal`,...etc
    MonthRepayments columns (e.g JanuaryRepayments) should be integers

    Hint: there should be 1x CustomerID = 1
    """

    qry = """
    SELECT
        CustomerID,
        CAST(SUM(CASE WHEN MonthName = 'January' THEN NumberOfRepayments ELSE 0 END) AS INTEGER) AS JanuaryRepayments,
        SUM(CASE WHEN MonthName = 'January' THEN AmountTotal ELSE 0 END) AS JanuaryTotal,
        CAST(SUM(CASE WHEN MonthName = 'February' THEN NumberOfRepayments ELSE 0 END) AS INTEGER) AS FebruaryRepayments,
        SUM(CASE WHEN MonthName = 'February' THEN AmountTotal ELSE 0 END) AS FebruaryTotal,
        CAST(SUM(CASE WHEN MonthName = 'March' THEN NumberOfRepayments ELSE 0 END) AS INTEGER) AS MarchRepayments,
        SUM(CASE WHEN MonthName = 'March' THEN AmountTotal ELSE 0 END) AS MarchTotal,
        CAST(SUM(CASE WHEN MonthName = 'April' THEN NumberOfRepayments ELSE 0 END) AS INTEGER) AS AprilRepayments,
        SUM(CASE WHEN MonthName = 'April' THEN AmountTotal ELSE 0 END) AS AprilTotal,
        CAST(SUM(CASE WHEN MonthName = 'May' THEN NumberOfRepayments ELSE 0 END) AS INTEGER) AS MayRepayments,
        SUM(CASE WHEN MonthName = 'May' THEN AmountTotal ELSE 0 END) AS MayTotal,
        CAST(SUM(CASE WHEN MonthName = 'June' THEN NumberOfRepayments ELSE 0 END) AS INTEGER) AS JuneRepayments,
        SUM(CASE WHEN MonthName = 'June' THEN AmountTotal ELSE 0 END) AS JuneTotal,
        CAST(SUM(CASE WHEN MonthName = 'July' THEN NumberOfRepayments ELSE 0 END) AS INTEGER) AS JulyRepayments,
        SUM(CASE WHEN MonthName = 'July' THEN AmountTotal ELSE 0 END) AS JulyTotal,
        CAST(SUM(CASE WHEN MonthName = 'August' THEN NumberOfRepayments ELSE 0 END) AS INTEGER) AS AugustRepayments,
        SUM(CASE WHEN MonthName = 'August' THEN AmountTotal ELSE 0 END) AS AugustTotal,
        CAST(SUM(CASE WHEN MonthName = 'September' THEN NumberOfRepayments ELSE 0 END) AS INTEGER) AS SeptemberRepayments,
        SUM(CASE WHEN MonthName = 'September' THEN AmountTotal ELSE 0 END) AS SeptemberTotal,
        CAST(SUM(CASE WHEN MonthName = 'October' THEN NumberOfRepayments ELSE 0 END) AS INTEGER) AS OctoberRepayments,
        SUM(CASE WHEN MonthName = 'October' THEN AmountTotal ELSE 0 END) AS OctoberTotal,
        CAST(SUM(CASE WHEN MonthName = 'November' THEN NumberOfRepayments ELSE 0 END) AS INTEGER) AS NovemberRepayments,
        SUM(CASE WHEN MonthName = 'November' THEN AmountTotal ELSE 0 END) AS NovemberTotal,
        CAST(SUM(CASE WHEN MonthName = 'December' THEN NumberOfRepayments ELSE 0 END) AS INTEGER) AS DecemberRepayments,
        SUM(CASE WHEN MonthName = 'December' THEN AmountTotal ELSE 0 END) AS DecemberTotal
    FROM timeline
    GROUP BY CustomerID
    ORDER BY CustomerID
    """

    return qry


# QUESTION 6 and 7 are linked, Do not be concerned with timezones or repayment times for these question.


def question_6():
    """
    The `customers` table was created by merging two separate tables: one containing data for male customers and the other for female customers.
    Due to an error, the data in the age columns were misaligned in both original tables, resulting in a shift of two places upwards in
    relation to the corresponding CustomerID.

    Create a table called `corrected_customers` with columns: `CustomerID`, `Age`, `CorrectedAge`, `Gender`
    Utilize a window function to correct this mistake in the new `CorrectedAge` column.
    Null values can be input manually - i.e. values that overflow should loop to the top of each gender.

    Also return a result set for this table (ie SELECT * FROM corrected_customers)
    """

    qry = """
    CREATE OR REPLACE TABLE corrected_customers AS
    WITH base AS (
        SELECT DISTINCT CustomerID, Age, Gender FROM customers
    ),
    numbered AS (
        SELECT
            CustomerID, Age, Gender,
            LAG(Age, 2)  OVER (PARTITION BY Gender ORDER BY CustomerID) AS LaggedAge,
            ROW_NUMBER() OVER (PARTITION BY Gender ORDER BY CustomerID) AS rn,
            COUNT(*)     OVER (PARTITION BY Gender)                     AS n
        FROM base
    )
    SELECT
        a.CustomerID,
        a.Age,
        COALESCE(a.LaggedAge, b.Age) AS CorrectedAge,
        a.Gender
    FROM numbered AS a
    LEFT JOIN numbered AS b
        ON  b.Gender = a.Gender
        AND a.rn <= 2
        AND b.rn = a.n - 2 + a.rn
    ORDER BY a.CustomerID;
    SELECT * FROM corrected_customers;
    """

    return qry


def question_7():
    """
    Create a column in corrected_customers called 'AgeCategory' that categorizes customers by age.
    Age categories should be as follows:
        - `Teen`: CorrectedAge < 20
        - `Young Adult`: 20 <= CorrectedAge < 30
        - `Adult`: 30 <= CorrectedAge < 60
        - `Pensioner`: CorrectedAge >= 60

    Make use of a windows function to assign a rank to each customer based on the total number of repayments per age group. Add this into a "Rank" column.
    The ranking should not skip numbers in the sequence, even when there are ties, i.e. 1,2,2,2,3,4 not 1,2,2,2,5,6
    Customers with no repayments should be included as 0 in the result.

    Return columns: `CustomerID`, `Age`, `CorrectedAge`, `Gender`, `AgeCategory`, `Rank`
    """

    qry = """
        ALTER TABLE corrected_customers ADD COLUMN IF NOT EXISTS AgeCategory VARCHAR;

    UPDATE corrected_customers
    SET AgeCategory = CASE
        WHEN CorrectedAge < 20 THEN 'Teen'
        WHEN CorrectedAge < 30 THEN 'Young Adult'
        WHEN CorrectedAge < 60 THEN 'Adult'
        ELSE 'Pensioner'
    END;

    SELECT
        cc.CustomerID,
        cc.Age,
        cc.CorrectedAge,
        cc.Gender,
        cc.AgeCategory,
        DENSE_RANK() OVER (
            PARTITION BY cc.AgeCategory
            ORDER BY COALESCE(r.NumberOfRepayments, 0) DESC
        ) AS "Rank"
    FROM corrected_customers AS cc
    LEFT JOIN (
        SELECT CustomerID, COUNT(*) AS NumberOfRepayments
        FROM repayments
        GROUP BY CustomerID
    ) AS r
        ON r.CustomerID = cc.CustomerID
    ORDER BY cc.AgeCategory, "Rank", cc.CustomerID;
    """

    return qry
