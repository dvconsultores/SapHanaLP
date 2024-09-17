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
  AND EKPO1.AEDAT >= TO_CHAR(CURRENT_DATE, 'YYYY') || '0101'
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


# Equipment
query_transfer_orders = """
SELECT *
FROM SAPHANADB.EKPO EKPO1 --LIMIT 100
WHERE AEDAT >= TO_CHAR(CURRENT_DATE, 'YYYY') || '0101'
--JOIN MSEG ON MKPF.MBLNR = MSEG.MBLNR
--WHERE MSEG.BWART IN ('301', '311')
--ORDER BY MKPF.BUDAT DESC;
"""

# 000000000000120000
query_transfer_orders = """
SELECT EKPO1.EBELN AS "orden_compra",
       EKPO1.UNIQUEID AS "id_sap",
       EKKO.LIFNR AS "proveedorIdId",
       EKPO1.WERKS AS "granjaIdId",
       MCHA.CHARG AS "lote", -- Lote from MCHA
       COALESCE(EKPO1.MENGE, 0) AS "cant",
       EKPO1.AEDAT
FROM SAPHANADB.EKPO EKPO1
INNER JOIN SAPHANADB.T001L ON EKPO1.LGORT = T001L.LGORT
INNER JOIN SAPHANADB.T001W ON EKPO1.WERKS = T001W.WERKS
INNER JOIN SAPHANADB.EKKO ON EKPO1.EBELN = EKKO.EBELN
LEFT JOIN SAPHANADB.MCHA ON EKPO1.MATNR = MCHA.MATNR -- Join with MCHA for batch (lote)
WHERE T001W.NAME1 NOT LIKE '%NO USAR%'
  AND T001L.LGOBE NOT LIKE '%NO USAR%'
  AND EKPO1.AEDAT >= TO_CHAR(CURRENT_DATE, 'YYYY') || '0101'
  AND EKPO1.MATNR = '000000000000120000'
GROUP BY EKPO1.EBELN, EKPO1.UNIQUEID, EKKO.LIFNR, EKPO1.WERKS, MCHA.CHARG, EKPO1.MENGE, EKPO1.AEDAT;
"""

# General consultation
# query_general = """
# SELECT
#     MKPF.MBLNR AS "Número de Documento",
#     MKPF.BUDAT AS "Fecha del Documento",
#     MKPF.USNAM AS "Usuario",
#     MSEG.MATNR AS "Código de Material",
#     MSEG.WERKS AS "Centro",
#     MSEG.LGORT AS "Almacén",
#     MSEG.MENGE AS "Cantidad",
#     MSEG.MEINS AS "Unidad de Medida",
#     MSEG.BWART AS "Tipo de Movimiento",
#     MSEG.CHARG AS "Lote",
#     MSEG.SGTXT AS "Texto del Movimiento"
# FROM
#     SAPHANADB.MSEG
# JOIN
#     SAPHANADB.MKPF ON MSEG.MBLNR = MKPF.MBLNR
#     AND MSEG.MJAHR = MKPF.MJAHR
# WHERE
#     -- MSEG.MATNR = '000000000123456789'  -- Reemplaza con el código de material específico
#     MKPF.BUDAT BETWEEN '20240719' AND '20241231'  -- Rango de fechas
#     --AND MSEG.WERKS = '4089'  -- Reemplaza con el centro específico
# ORDER BY
#     MKPF.BUDAT DESC;
# """

query_general = """
SELECT 
    MATDOC.BUDAT AS "Fecha",
    MATDOC.MATNR AS "Código de Material",
    MAKT.MAKTX AS "Descripción de Material",
    MATDOC.MENGE AS "Cantidad Despachada",
    MATDOC.WERKS AS "Centro",
    MATDOC.LGORT AS "Almacén",
    MATDOC.BWART AS "Tipo de Movimiento",
    MATDOC.BUKRS AS "Centro de Entrega"  -- Agregado BURKS
FROM 
    SAPHANADB.MATDOC
INNER JOIN 
    SAPHANADB.MAKT ON MATDOC.MATNR = MAKT.MATNR
WHERE 
    MATDOC.BWART = '641'  -- Tipo de movimiento 641
    AND MATDOC.WERKS = '4089'  -- Centro desde el cual se despachó
    AND MATDOC.MATNR = '000000000000105025'
    AND MATDOC.BUDAT >= '20240712'
ORDER BY 
    MATDOC.BUDAT ASC;
"""


# SELECT 
#     SUM(MATDOC.MENGE) AS "Cantidad Despachada"
# FROM 
#     SAPHANADB.MATDOC
# INNER JOIN 
#     SAPHANADB.MAKT ON MATDOC.MATNR = MAKT.MATNR
# WHERE 
#     MATDOC.BWART = '641'  -- Tipo de movimiento 641
#     AND MATDOC.WERKS = '4089'  -- Centro desde el cual se despachó
#     AND MATDOC.MATNR = '000000000000105005'
#     AND MATDOC.BUDAT >= '20240712'


# Transferencia de Alimento a granja  
# 105025
# 4089
# Transferencia de huevos a incubadora
# Transferencia de pollitos bb a granja engorde
# Transferencia de cria a producción
