import psycopg2
import logging

print("Extracting data from OLTP")

def connection():
    return psycopg2.connect(
        dbname="pagila3",
        user="postgres",
        password="123456",
        host="host.docker.internal",
        # host="localhost",
        port="5432"
    )

def print_table_count(rows):
    print(f"\t\tOLTP : {rows[0]}")
    print(f"\t\tStaging : {rows[1]}")
    print(f"\t\tDW : {rows[2] if len(rows) > 2 else 'N/A'}")


def extract_customer(conn):
    # ------------------- Extract Data Customer -------------------
    print("Start extracting data from OLTP : Customer")
    #Create table Staging (jika belum ada)
    create_stg_customer = f"CREATE TABLE IF NOT EXISTS staging.stg_customer(customer_id INTEGER, first_name VARCHAR(45), last_name VARCHAR(45), email VARCHAR(50), batch_id VARCHAR(30), extract_time TIMESTAMP);"
    conn.execute(create_stg_customer)
    print("\tTable Staging Customer created successfully")

    #Cek Data Staging Customer            
    # stg_customer_check = f"SELECT COUNT(*) AS counter FROM staging.stg_customer"
    customer_check = f"SELECT (SELECT COUNT(*) FROM public.customer) AS source_count,(SELECT COUNT(*) FROM staging.stg_customer) AS extract_count, (SELECT COUNT(*) FROM dw.dim_customer) AS load_count;"
    conn.execute(customer_check)
    rows = conn.fetchone()            
    print(f"\tData Customer Before Extract")
    print_table_count(rows)

    if rows[1] == 0: 
        # Data Kosong (Balikan Query 0)       
        #Initial Extract (Dibatasi 100 record sekali input)
        print("\tStart Initial Extract Data Customer")   
        insert_stg_customer = "INSERT INTO staging.stg_customer SELECT customer_id, first_name, last_name, email, 'B001', CURRENT_TIMESTAMP FROM public.customer ORDER BY last_update LIMIT 100"
    else:
        #Data Sudah Ada (Balikan Query > 0)
        #Incremental Load 
        print("\tStart Incremental Extract Data Customer") 
        insert_stg_customer = "INSERT INTO staging.stg_customer(customer_id, first_name, last_name, email, batch_id, extract_time) SELECT c.customer_id, c.first_name, c.last_name, c.email, ('B' || LPAD((SUBSTRING((select batch_id from staging.stg_customer order by extract_time desc limit 1) FROM 2)::INT + 1)::TEXT, 3, '0')) as batch, CURRENT_TIMESTAMP FROM public.customer c LEFT JOIN staging.stg_customer sc USING(customer_id) WHERE sc.customer_id IS NULL ORDER BY c.last_update LIMIT 100;"
    conn.execute(insert_stg_customer)
    
    conn.execute(customer_check)
    rows = conn.fetchone()
    print_table_count(rows)

    print("Extracting data from OLTP : Customer Finished")
    # ------------------- Extract Data Customer -------------------

def extract_film(conn):
# ------------------- Extract Data Film -------------------
    print("Start extracting data from OLTP : Film")
    #Create table Staging (jika belum ada)
    create_stg_film = f"CREATE TABLE IF NOT EXISTS staging.stg_film (film_id INTEGER, title VARCHAR(255), rental_rate NUMERIC(4,2), batch_id VARCHAR(30), extract_time TIMESTAMP );"
    conn.execute(create_stg_film)
    print("\tTable Staging Film created successfully")

    #Cek Data Staging Film            
    # stg_film_check = f"SELECT COUNT(*) AS counter FROM staging.stg_film"
    film_check = f"SELECT (SELECT COUNT(*) FROM public.film) AS source_count,(SELECT COUNT(*) FROM staging.stg_film) AS extract_count, (SELECT COUNT(*) FROM dw.dim_film) AS load_count;"
    conn.execute(film_check)
    rows = conn.fetchone()            
    print(f"\tData Film Before Extract")
    print_table_count(rows)

    if rows[1] == 0: 
        # Data Kosong (Balikan Query 0)       
        #Initial Extract 
        print("\tStart Initial Extract Data Film")   
        insert_stg_film = "INSERT INTO staging.stg_film SELECT film_id, title, rental_rate, 'B001', CURRENT_TIMESTAMP FROM public.film ORDER BY last_update LIMIT 100;"
    else:
        #Data Sudah Ada (Balikan Query > 0)
        #Incremental Load 
        print("\tStart Incremental Extract Data Film") 
        insert_stg_film = "INSERT INTO staging.stg_film(film_id, title, rental_rate, batch_id, extract_time) SELECT f.film_id, f.title, f.rental_rate, ('B' || LPAD((SUBSTRING((select batch_id from staging.stg_film order by extract_time desc limit 1) FROM 2)::INT + 1)::TEXT, 3, '0')) as batch, CURRENT_TIMESTAMP FROM public.film f LEFT JOIN staging.stg_film sc USING(film_id) WHERE sc.film_id IS NULL ORDER BY f.last_update LIMIT 100"
    conn.execute(insert_stg_film)
    
    conn.execute(film_check)
    rows = conn.fetchone()
    print_table_count(rows)

    print("Extracting data from OLTP : Film Finished")
    # ------------------- Extract Data Film -------------------
            

def extract_store(conn):
    # ------------------- Extract Data Store -------------------
    print("Start extracting data from OLTP : Store")
    #Create table Staging (jika belum ada)
    create_stg_store = f"CREATE TABLE IF NOT EXISTS staging.stg_store (store_id INTEGER, store_name VARCHAR(50), batch_id VARCHAR(30), extract_time TIMESTAMP );"
    conn.execute(create_stg_store)
    print("\tTable Staging Store created successfully")

    #Cek Data Staging Store            
    # stg_store_check = f"SELECT COUNT(*) AS counter FROM staging.stg_store"
    store_check = f"SELECT (SELECT COUNT(*) FROM public.store) AS source_count,(SELECT COUNT(*) FROM staging.stg_store) AS extract_count, (SELECT COUNT(*) FROM dw.dim_store) AS load_count;"
    conn.execute(store_check)
    rows = conn.fetchone()            
    print(f"\tData Store Before Extract")
    print_table_count(rows)

    if rows[1] == 0: 
        # Data Kosong (Balikan Query 0)       
        #Initial Extract 
        print("\tStart Initial Extract Data Store")   
        insert_stg_store = "INSERT INTO staging.stg_store SELECT s.store_id, a.address, 'B001', CURRENT_TIMESTAMP FROM public.store s join public.address a using(address_id) ORDER BY a.last_update LIMIT 100;"
    else:
        #Data Sudah Ada (Balikan Query > 0)
        #Incremental Load 
        print("\tStart Incremental Extract Data Store") 
        insert_stg_store = "INSERT INTO staging.stg_store(store_id, store_name, batch_id, extract_time) SELECT s.store_id, a.address, ('B' || LPAD((SUBSTRING((select batch_id from staging.stg_store order by extract_time desc limit 1) FROM 2)::INT + 1)::TEXT, 3, '0')) as batch, CURRENT_TIMESTAMP FROM public.store s JOIN public.address a USING(address_id) LEFT JOIN staging.stg_store sc USING(store_id) WHERE sc.store_id IS NULL ORDER BY s.last_update LIMIT 100;"
    conn.execute(insert_stg_store)
    
    conn.execute(store_check)
    rows = conn.fetchone()
    print_table_count(rows)

    print("Extracting data from OLTP : Store Finished")
    # ------------------- Extract Data Store -------------------


def extract_inventory(conn):
    # ------------------- Extract Data Inventory  -------------------
    print("Start extracting data from OLTP : Inventory")
    #Create table Staging (jika belum ada)
    create_stg_inventory = f"CREATE TABLE IF NOT EXISTS staging.stg_inventory (inventory_id INTEGER, film_id INTEGER, store_id INTEGER, batch_id VARCHAR(30), extract_time TIMESTAMP);"
    conn.execute(create_stg_inventory)
    print("\tTable Staging Inventory created successfully")

    #Cek Data Staging create_stg_inventory            
    # stg_inventory_check = f"SELECT COUNT(*) AS counter FROM staging.stg_inventory"
    inventory_check = f"SELECT (SELECT COUNT(*) FROM public.inventory) AS source_count,(SELECT COUNT(*) FROM staging.stg_inventory) AS extract_count;"
    conn.execute(inventory_check)
    rows = conn.fetchone()            
    print(f"\tData Inventory Before Extract")
    print_table_count(rows)

    if rows[1] == 0: 
        # Data Kosong (Balikan Query 0)       
        #Initial Extract 
        print("\tStart Initial Extract Data Inventory")   
        insert_stg_inventory = "INSERT INTO staging.stg_inventory SELECT inventory_id, film_id, store_id, 'B001', CURRENT_TIMESTAMP FROM public.inventory ORDER BY last_update LIMIT 100"
    else:
        #Data Sudah Ada (Balikan Query > 0)
        #Incremental Load 
        print("\tStart Incremental Extract Data Inventory") 
        insert_stg_inventory = "INSERT INTO staging.stg_inventory(inventory_id, film_id, store_id, batch_id, extract_time) SELECT i.inventory_id, i.film_id, i.store_id, ('B' || LPAD((SUBSTRING((select batch_id from staging.stg_rental order by extract_time desc limit 1) FROM 2)::INT + 1)::TEXT, 3, '0')) as batch, CURRENT_TIMESTAMP FROM public.inventory i LEFT JOIN staging.stg_inventory sc USING(inventory_id) WHERE sc.inventory_id IS NULL ORDER BY i.last_update LIMIT 100"
    conn.execute(insert_stg_inventory)
    
    conn.execute(inventory_check)
    rows = conn.fetchone()
    print_table_count(rows)

    print("Extracting data from OLTP : Inventory Finished")
    # ------------------- Extract Data Inventory -------------------
            

def extract_rental(conn):
    # ------------------- Extract Data Rental  -------------------
    print("Start extracting data from OLTP : Rental")
    #Create table Staging (jika belum ada)
    create_stg_rental = f"CREATE TABLE IF NOT EXISTS staging.stg_rental (rental_id INTEGER, inventory_id INTEGER, batch_id VARCHAR(30), extract_time TIMESTAMP);"
    conn.execute(create_stg_rental)
    print("\tTable Staging Rental created successfully")

    #Cek Data Staging create_stg_rental            
    # stg_rental_check = f"SELECT COUNT(*) AS counter FROM staging.stg_rental"
    rental_check = f"SELECT (SELECT COUNT(*) FROM public.rental) AS source_count,(SELECT COUNT(*) FROM staging.stg_rental) AS extract_count;"
    conn.execute(rental_check)
    rows = conn.fetchone()            
    print(f"\tData Rental Before Extract")
    print_table_count(rows)

    if rows[1] == 0: 
        # Data Kosong (Balikan Query 0)       
        #Initial Extract 
        print("\tStart Initial Extract Data Rental")   
        insert_stg_rental = "INSERT INTO staging.stg_rental SELECT rental_id, inventory_id, 'B001', CURRENT_TIMESTAMP FROM public.rental ORDER BY last_update LIMIT 100;"
    else:
        #Data Sudah Ada (Balikan Query > 0)
        #Incremental Load 
        print("\tStart Incremental Extract Data Rental") 
        insert_stg_rental = "INSERT INTO staging.stg_rental(rental_id, inventory_id, batch_id, extract_time) SELECT r.rental_id, r.inventory_id, ('B' || LPAD((SUBSTRING((select batch_id from staging.stg_rental order by extract_time desc limit 1) FROM 2)::INT + 1)::TEXT, 3, '0')) as batch, CURRENT_TIMESTAMP FROM public.rental r LEFT JOIN staging.stg_rental sc USING(rental_id) WHERE sc.rental_id IS NULL ORDER BY r.last_update LIMIT 100"
    conn.execute(insert_stg_rental)
    
    conn.execute(rental_check)
    rows = conn.fetchone()
    print_table_count(rows)

    print("Extracting data from OLTP : Rental Finished")
    # ------------------- Extract Data Rental -------------------
            
def extract_payment(conn):
    # ------------------- Extract Data Payment  -------------------
    print("Start extracting data from OLTP : Payment")
    #Create table Staging (jika belum ada)
    create_stg_payment = f"CREATE TABLE IF NOT EXISTS staging.stg_payment (payment_id INTEGER, customer_id INTEGER, rental_id INTEGER, amount NUMERIC(5,2), payment_date TIMESTAMP, batch_id VARCHAR(30), extract_time TIMESTAMP);"
    conn.execute(create_stg_payment)
    print("\tTable Staging Payment created successfully")

    #Cek Data Staging create_stg_payment            
    # stg_payment = f"SELECT COUNT(*) AS counter FROM staging.stg_payment"
    payment_check = f"SELECT (SELECT COUNT(*) FROM public.payment) AS source_count,(SELECT COUNT(*) FROM staging.stg_payment) AS extract_count,(SELECT COUNT(*) FROM dw.fact_payment) AS fact_payment_count;"
    conn.execute(payment_check)
    rows = conn.fetchone()            
    print(f"\tData Payment Before Extract")
    print_table_count(rows)

    if rows[1] == 0: 
        # Data Kosong (Balikan Query 0)       
        #Initial Extract 
        print("\tStart Initial Extract Data Payment")   
        insert_stg_payment = "INSERT INTO staging.stg_payment SELECT payment_id, customer_id, rental_id, amount, payment_date, 'B001', CURRENT_TIMESTAMP FROM public.payment ORDER BY payment_date LIMIT 100;"
    else:
        #Data Sudah Ada (Balikan Query > 0)
        #Incremental Load 
        print("\tStart Incremental Extract Data Payment") 
        insert_stg_payment = "INSERT INTO staging.stg_payment(payment_id, customer_id, rental_id, amount, payment_date, batch_id, extract_time) SELECT p.payment_id, p.customer_id, p.rental_id, p.amount, p.payment_date, ('B' || LPAD((SUBSTRING((select batch_id from staging.stg_payment order by extract_time desc limit 1) FROM 2)::INT + 1)::TEXT, 3, '0')) as batch, CURRENT_TIMESTAMP FROM public.payment p LEFT JOIN staging.stg_payment sc USING(payment_id) WHERE sc.payment_id IS NULL ORDER BY p.payment_date  LIMIT 100"
    conn.execute(insert_stg_payment)
    
    conn.execute(payment_check)
    rows = conn.fetchone()
    print_table_count(rows)

    print("Extracting data from OLTP : Payment Finished")
    # ------------------- Extract Data Payment -------------------


def run_extract():
    db = connection()

    try:
        with db.cursor() as conn:
            extract_customer(conn)
            extract_film(conn)
            extract_store(conn)
            extract_inventory(conn)
            extract_rental(conn)
            extract_payment(conn)
        db.commit()
    except Exception as e:
        print("Error while extracting data from OLTP")
        logging.error(e)

# run_extract()