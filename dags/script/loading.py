import psycopg2
import logging

def connection():
    return psycopg2.connect(
        dbname="pagila3",
        user="postgres",
        password="123456",
        host="host.docker.internal", #running in docker container
        # host="localhost", #running in local machine
        port="5432"
    )

def print_table_count(rows):
    print(f"\t\tOLTP : {rows[0]}")
    print(f"\t\tStaging : {rows[1]}")
    print(f"\t\tDW : {rows[2] if len(rows) > 2 else 'N/A'}")

print("Loading data to Data Warehouse (DW)")

def load_customer(conn):
    # ------------------- Load data dim_customer -------------------
    print("Start loading data to DW : dim_customer")
    #Create table dim_customer (jika belum ada)
    create_dim_customer = """CREATE TABLE IF NOT EXISTS dw.dim_customer (
                            customer_key INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                            customer_id INTEGER NOT NULL UNIQUE,
                            first_name VARCHAR(45),
                            last_name VARCHAR(45),
                            full_name VARCHAR(100),
                            email VARCHAR(50));"""
    conn.execute(create_dim_customer)
    print("\tTable dim_customer created successfully")

    #Cek Data dw Customer            
    customer_check = """SELECT 
                            (SELECT COUNT(*) FROM public.customer) AS source_count,
                            (SELECT COUNT(*) FROM staging.stg_customer) AS extract_count, 
                            (SELECT COUNT(*) FROM dw.dim_customer) AS load_count;"""
    conn.execute(customer_check)
    rows = conn.fetchone()            
    print(f"\tData dim_customer Before Load")
    print_table_count(rows)

    if rows[2] == 0: 
        # Data Kosong (Balikan Query 0)       
        # Initial Load (Dibatasi 100 record sekali input)
        print("\tStart Initial Load dim_customer")   
        insert_dim_customer = """INSERT INTO dw.dim_customer (
                                        customer_id,
                                        first_name,
                                        last_name,
                                        full_name,
                                        email
                                    )
                                    SELECT
                                        customer_id,
                                        INITCAP(TRIM(first_name)),
                                        INITCAP(TRIM(last_name)),
                                        CONCAT_WS(
                                            ' ',
                                            INITCAP(TRIM(first_name)),
                                            INITCAP(TRIM(last_name))
                                        ),
                                        LOWER(TRIM(email))
                                    FROM staging.stg_customer
                                    ORDER BY extract_time LIMIT 100;""" 
    else:
        # Data Sudah Ada (Balikan Query > 0)
        # Incremental Load 
        print("\tStart Incremental Load dim_customer") 
        insert_dim_customer = """INSERT INTO dw.dim_customer (
                                    customer_id,
                                    first_name,
                                    last_name,
                                    full_name,
                                    email
                                )
                                SELECT
                                    customer_id,
                                    INITCAP(TRIM(aa.first_name)),
                                    INITCAP(TRIM(aa.last_name)),
                                    CONCAT_WS(
                                        ' ',
                                        INITCAP(TRIM(aa.first_name)),
                                        INITCAP(TRIM(aa.last_name))
                                    ),
                                    LOWER(TRIM(aa.email))
                                FROM staging.stg_customer aa
                                left join dw.dim_customer dc USING(customer_id)
                                where dc.customer_id is null
                                order by aa.extract_time limit 100
                                ON CONFLICT (customer_id) DO NOTHING;"""
    conn.execute(insert_dim_customer)
    
    conn.execute(customer_check)
    rows = conn.fetchone()
    print_table_count(rows)

    print("Loading data to Data Warehouse : Customer Finished")
    # ------------------- Loading data dim_customer -------------------
    

def load_film(conn):
    # ------------------- Load data dim_film -------------------
    print("Start loading data to DW : dim_film")
    #Create table dim_film (jika belum ada)
    create_dim_film = """CREATE TABLE IF NOT EXISTS dw.dim_film (
                            film_key INTEGER
                                GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                            film_id INTEGER NOT NULL UNIQUE,
                            title VARCHAR(255),
                            rental_rate NUMERIC(4,2)
                        );"""
    conn.execute(create_dim_film)
    print("\tTable dim_film created successfully")

    #Cek Data dw Film            
    film_check = """SELECT 
                            (SELECT COUNT(*) FROM public.film) AS source_count,
                            (SELECT COUNT(*) FROM staging.stg_film) AS extract_count, 
                            (SELECT COUNT(*) FROM dw.dim_film) AS load_count;"""
    conn.execute(film_check)
    rows = conn.fetchone()            
    print(f"\tData dim_film Before Load")
    print_table_count(rows)

    if rows[2] == 0: 
        # Data Kosong (Balikan Query 0)       
        # Initial Load (Dibatasi 100 record sekali input)
        print("\tStart Initial Load dim_film")   
        insert_dim_film = """INSERT INTO dw.dim_film (
                                    film_id,
                                    title,
                                    rental_rate
                                )
                                SELECT
                                    film_id,
                                    TRIM(title),
                                    rental_rate
                                FROM staging.stg_film
                                ORDER BY extract_time LIMIT 100;"""  
    else:
        # Data Sudah Ada (Balikan Query > 0)
        # Incremental Load 
        print("\tStart Incremental Load dim_film") 
        insert_dim_film = """INSERT INTO dw.dim_film (
                                    film_id,
                                    title,
                                    rental_rate
                                )
                                SELECT
                                    aa.film_id,
                                    TRIM(aa.title),
                                    aa.rental_rate
                                FROM staging.stg_film aa
                                left join dw.dim_film dc USING(film_id)
                                where dc.film_id is null
                                order by aa.extract_time limit 100
                                ON CONFLICT (film_id) DO NOTHING;"""
    conn.execute(insert_dim_film)
    
    conn.execute(film_check)
    rows = conn.fetchone()
    print_table_count(rows)

    print("Loading data to Data Warehouse : Film Finished")
    # ------------------- Loading data dim_film -------------------


def load_store(conn):
    # ------------------- Load data dim_store -------------------
    print("Start loading data to DW : dim_store")
    #Create table dim_store (jika belum ada)
    create_dim_store = """CREATE TABLE IF NOT EXISTS dw.dim_store (
                            store_key INTEGER
                                GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                            store_name VARCHAR(100)
                            );"""
    conn.execute(create_dim_store)
    print("\tTable dim_store created successfully")

    #Cek Data dw Store            
    store_check = """SELECT 
                            (SELECT COUNT(*) FROM public.store) AS source_count,
                            (SELECT COUNT(*) FROM staging.stg_store) AS extract_count, 
                            (SELECT COUNT(*) FROM dw.dim_store) AS load_count;"""
    conn.execute(store_check)
    rows = conn.fetchone()            
    print(f"\tData dim_store Before Load")
    print_table_count(rows)

    if rows[2] == 0: 
        # Data Kosong (Balikan Query 0)       
        # Initial Load (Dibatasi 100 record sekali input)
        print("\tStart Initial Load dim_store")
        insert_dim_store = """INSERT INTO dw.dim_store (
                                    store_id,
                                    store_address
                                )
                                SELECT
                                    s.store_id,
                                    TRIM(s.store_name)
                                FROM staging.stg_store s
                                ORDER BY extract_time LIMIT 100;"""  
    else:
        # Data Sudah Ada (Balikan Query > 0)
        # Incremental Load 
        print("\tStart Incremental Load dim_store") 
        insert_dim_store = """INSERT INTO dw.dim_store (
                                    store_id,
                                    store_address
                                )
                                SELECT
                                    s.store_id,
                                    TRIM(s.store_name)
                                FROM staging.stg_store s
                                LEFT JOIN dw.dim_store dc USING(store_id)
                                WHERE dc.store_id IS NULL
                                ORDER BY s.extract_time LIMIT 100
                                ON CONFLICT (store_id) DO NOTHING;"""
    conn.execute(insert_dim_store)

    conn.execute(store_check)
    rows = conn.fetchone()
    print_table_count(rows)

    print("Loading data to Data Warehouse : Store Finished")
    # ------------------- Loading data dim_store -------------------
    
    
def load_date(conn):
    # ------------------- Load data dim_date -------------------
    print("Start loading data to DW : dim_date")
    #Create table dim_date (jika belum ada)
    create_dim_date = """CREATE TABLE IF NOT EXISTS dw.dim_date (
                            date_key INTEGER PRIMARY KEY,
                            full_date DATE NOT NULL UNIQUE,
                            day INTEGER,
                            month INTEGER,
                            quarter INTEGER,
                            year INTEGER
                        );"""
    conn.execute(create_dim_date)
    print("\tTable dim_date created successfully")

    #Cek Data dw Date            
    date_check = """SELECT COUNT(*) AS load_count FROM dw.dim_date;"""
    conn.execute(date_check)
    rows = conn.fetchone()     
    print(f"\tData dim_date Before Load : ", rows[0])

    if rows[0] == 0: 
        # Data Kosong (Balikan Query 0)       
        # Initial Load (Dibatasi 100 record sekali input)
        print("\tStart Initial Load dim_date")
        insert_dim_date = """INSERT INTO dw.dim_date (
                            date_key,
                            full_date,
                            day,
                            month,
                            quarter,
                            year
                        )
                        SELECT DISTINCT
                            TO_CHAR(payment_date, 'YYYYMMDD')::INTEGER as date_key,
                            payment_date::DATE as full_date,
                            EXTRACT(DAY FROM payment_date)::INTEGER as day,
                            EXTRACT(MONTH FROM payment_date)::INTEGER as month,
                            EXTRACT(QUARTER FROM payment_date)::INTEGER as quarter,
                            EXTRACT(YEAR FROM payment_date)::INTEGER as year
                        FROM staging.stg_payment
                        WHERE payment_date IS NOT NULL
                        ORDER BY full_date LIMIT 100;"""  
    else:
        # Data Sudah Ada (Balikan Query > 0)
        # Incremental Load 
        print("\tStart Incremental Load dim_date") 
        insert_dim_date = """INSERT INTO dw.dim_date (
                            date_key,
                            full_date,
                            day,
                            month,
                            quarter,
                            year
                        )
                        SELECT DISTINCT
                            TO_CHAR(payment_date, 'YYYYMMDD')::INTEGER as date_key,
                            payment_date::DATE as full_date,
                            EXTRACT(DAY FROM payment_date)::INTEGER as day,
                            EXTRACT(MONTH FROM payment_date)::INTEGER as month,
                            EXTRACT(QUARTER FROM payment_date)::INTEGER as quarter,
                            EXTRACT(YEAR FROM payment_date)::INTEGER as year
                        FROM staging.stg_payment s
                        LEFT JOIN dw.dim_date dc ON s.payment_date = dc.full_date
                        WHERE dc.full_date IS NULL
                        ORDER BY full_date LIMIT 100
                        ON CONFLICT (full_date) DO NOTHING;"""
    conn.execute(insert_dim_date)

    conn.execute(date_check)
    rows = conn.fetchone()
    print(f"\tData dim_date After Load : ", rows[0])

    print("Loading data to Data Warehouse : Date Finished")
    # ------------------- Loading data dim_date -------------------
    
    
def load_fact_payment(conn):
    # ------------------- Load data fact_payment -------------------
    print("Start loading data to DW : fact_payment")
    #Create table fact_payment (jika belum ada)
    create_fact_payment = """CREATE TABLE IF NOT EXISTS dw.fact_payment (
                                payment_id INTEGER PRIMARY KEY,
                                date_key INTEGER NOT NULL,
                                customer_key INTEGER NOT NULL,
                                film_key INTEGER NOT NULL,
                                store_key INTEGER NOT NULL,
                                revenue_amount NUMERIC(10,2) NOT NULL,
                                FOREIGN KEY (date_key)
                                    REFERENCES dw.dim_date(date_key),
                                FOREIGN KEY (customer_key)
                                    REFERENCES dw.dim_customer(customer_key),
                                FOREIGN KEY (film_key)
                                    REFERENCES dw.dim_film(film_key),
                                FOREIGN KEY (store_key)
                                    REFERENCES dw.dim_store(store_key)
                            );"""
    conn.execute(create_fact_payment)
    print("\tTable fact_payment created successfully")

    #Cek Data Fact Payment            
    payment_check = """SELECT (SELECT COUNT(*) FROM public.payment) AS source_count,
                        (SELECT COUNT(*) FROM staging.stg_payment) AS extract_count,
                        (SELECT COUNT(*) FROM dw.fact_payment) AS fact_payment_count;"""
    conn.execute(payment_check)
    rows = conn.fetchone()            
    print(f"\tData Payment Before Load")
    print_table_count(rows)

    if rows[2] == 0: 
        # Data Kosong (Balikan Query 0)       
        # Initial Load (Dibatasi 100 record sekali input)
        print("\tStart Initial Load fact_payment")
        insert_fact_payment = """INSERT INTO dw.fact_payment (
                                    payment_id,
                                    date_key,
                                    customer_key,
                                    film_key,
                                    store_key,
                                    revenue_amount
                                )
                                SELECT
                                    p.payment_id,
                                    d.date_key,
                                    c.customer_key,
                                    f.film_key,
                                    s.store_key,
                                    p.amount
                                FROM staging.stg_payment p
                                JOIN staging.stg_rental r
                                    ON p.rental_id = r.rental_id
                                JOIN staging.stg_inventory i
                                    ON r.inventory_id = i.inventory_id
                                JOIN dw.dim_date d
                                    ON p.payment_date::DATE = d.full_date
                                JOIN dw.dim_customer c
                                    ON p.customer_id = c.customer_id
                                JOIN dw.dim_film f
                                    ON i.film_id = f.film_id
                                JOIN dw.dim_store s
                                    ON i.store_id = s.store_id
                                ORDER BY p.extract_time LIMIT 100;"""  
    else:
        # Data Sudah Ada (Balikan Query > 0)
        # Incremental Load 
        print("\tStart Incremental Load fact_payment") 
        insert_fact_payment = """INSERT INTO dw.fact_payment (
                                    payment_id,
                                    date_key,
                                    customer_key,
                                    film_key,
                                    store_key,
                                    revenue_amount
                                )
                                SELECT
                                    p.payment_id,
                                    d.date_key,
                                    c.customer_key,
                                    f.film_key,
                                    s.store_key,
                                    p.amount
                                FROM staging.stg_payment p
                                JOIN staging.stg_rental r
                                    ON p.rental_id = r.rental_id
                                JOIN staging.stg_inventory i
                                    ON r.inventory_id = i.inventory_id
                                JOIN dw.dim_date d
                                    ON p.payment_date::DATE = d.full_date
                                JOIN dw.dim_customer c
                                    ON p.customer_id = c.customer_id
                                JOIN dw.dim_film f
                                    ON i.film_id = f.film_id
                                JOIN dw.dim_store s
                                    ON i.store_id = s.store_id
                                LEFT JOIN dw.fact_payment fp using(payment_id)
                                WHERE fp.payment_id IS NULL
                                ORDER BY p.extract_time LIMIT 100
                                ON CONFLICT (full_date) DO NOTHING;"""
    conn.execute(insert_fact_payment)

    conn.execute(payment_check)
    rows = conn.fetchone()
    print_table_count(rows)

    print("Loading data to Data Warehouse : Fact Payment Finished")
    # ------------------- Loading data fact_payment -------------------
def run_loading():
    db = connection()

    try:
        with db.cursor() as conn:
            load_customer(conn)
            load_film(conn)
            load_store(conn)
            load_date(conn)
            load_fact_payment(conn)
        db.commit()
    except Exception as e:
        print("Error while Loading to DW")
        logging.error(e)
        
# run_loading()