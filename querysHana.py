# SQL queries
# Farm Ready
query_farms = """
SELECT WERKS, NAME1
FROM SAPHANADB.T001W
WHERE MANDT = '120' 
AND NAME2 NOT LIKE '%NO USAR%' 
AND NAME1 NOT LIKE '%NO USAR%'
"""

# Warehouse Ready
query_warehouse = """
SELECT LGORT, LGOBE, T001L.WERKS
FROM SAPHANADB.T001L 
INNER JOIN SAPHANADB.T001W ON T001L.WERKS = T001W.WERKS
WHERE T001W.MANDT = '120' 
AND T001L.WERKS >= '4000'
AND T001W.NAME1 NOT LIKE '%NO USAR%' 
AND T001L.LGOBE NOT LIKE '%NO USAR%'
"""
# Performing the reading against the temporary table
query_warehouse_temp = """
SELECT 
    temp_warehouse."LGORT" as id_sap,
	temp_warehouse."LGOBE" as galpon,
	granjas.id "granjaIdId"
FROM 
    temp_warehouse
INNER JOIN 
    granjas ON temp_warehouse.id_sap = granjas.id_sap
"""    


# Purchase Orders in Process
query_purchase_orders = """
SELECT EKPO1.EBELN AS "orden_compra"
    , EKPO1.UNIQUEID AS "id_sap"
    , EKKO.LIFNR AS "proveedorIdId"
    , EKPO1.WERKS AS "granjaIdId"
    , COALESCE(EKPO1.MENGE, 0) AS "cant_machos" -- Replace NULL with 0 for cant_machos
    , COALESCE(EKPO2.MENGE, 0) AS "cant_hembras" -- Replace NULL with 0 for cant_hembras
FROM SAPHANADB.EKPO EKPO1
LEFT JOIN SAPHANADB.EKPO EKPO2
  ON EKPO1.EBELN = EKPO2.EBELN
  AND EKPO1.AEDAT = EKPO2.AEDAT
  AND EKPO2.MATNR = '000000000000110000' -- Material number for hembras
INNER JOIN SAPHANADB.T001L ON EKPO1.LGORT = T001L.LGORT
INNER JOIN SAPHANADB.T001W ON EKPO1.WERKS = T001W.WERKS
INNER JOIN SAPHANADB.EKKO ON EKPO1.EBELN = EKKO.EBELN -- Join with EKKO to get LIFNR
WHERE T001W.NAME1 NOT LIKE '%NO USAR%' 
  AND T001L.LGOBE NOT LIKE '%NO USAR%'
  AND EKPO1.MATNR = '000000000000110001' -- Material number for machos
GROUP BY EKPO1.EBELN, EKPO1.UNIQUEID, EKKO.LIFNR, EKPO1.WERKS, EKPO1.MENGE, EKPO2.MENGE
"""


# Purchase Orders in Process Temporary table
query_purchase_orders_temp = """
SELECT 
    a.orden_compra,
    a.id_sap,
	a.cant_hembras,
	a.cant_machos,
    p.id,
    g.id
FROM 
    temp_crias_ordenes_recepcion a
INNER JOIN 
    proveedores p ON a."proveedorIdId" = p.id_sap
INNER JOIN 
    granjas g ON a."granjaIdId" = g.id_sap;
"""     

# Purchase Orders in Process
query_purchase_orders_history = """
SELECT *
FROM SAPHANADB.EKBE
WHERE EBELN = '4500011936'
LIMIT 100
"""

# Purchase Orders in Process
query_transport = """
SELECT LIFNR, NAME1
FROM SAPHANADB.LFA1
"""