# Developer: Andrés Dominguez
# GlobalDV C.A
# Date: 2021-09-15
# @AllRightsReserved

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


query_transfer_food_farms = """
SELECT 
    MATDOC.BUDAT,
    MATDOC.MATNR,
    MAKT.MAKTX,
    MATDOC.MENGE,
    MATDOC.WERKS,
    MATDOC.LGORT,
    MATDOC.BWART,
    MATDOC.BUKRS,
    MATDOC.MBLNR,
    MATDOC.EBELN
FROM 
    SAPHANADB.MATDOC
INNER JOIN 
    SAPHANADB.MAKT ON MATDOC.MATNR = MAKT.MATNR
WHERE 
    MATDOC.BWART = '641'  -- Tipo de movimiento 641
    AND MATDOC.MATNR BETWEEN  '000000000000105000' AND '000000000000105999'
    AND MATDOC.BUDAT >= TO_CHAR(CURRENT_DATE, 'YYYY') || '0101'
ORDER BY 
    MATDOC.BUDAT ASC;
"""

query_transfer_food_temp = """
SELECT 
    CONCAT(a."MBLNR", '-', a."EBELN", '-', a."MATNR") AS "id_sap"
    , a."EBELN"
    , a."MENGE"
    , b."id" "granjas_id_sap"
    , a."MATNR"
    , a."MAKTX"
    , CASE
        WHEN a."MATNR" IN ('000000000000105012', '000000000000105003') THEN 'CRIA'
        WHEN a."MATNR" IN ('000000000000105004', '000000000000105013', '000000000000105027', '000000000000105028', '000000000000105021', '000000000000105007') THEN 'PRODUCCION'
        WHEN a."MATNR" = '000000000000105025' THEN 'ENGORDE'
        ELSE 'ENGORDE'
    END AS "CATEGORY"
FROM 
    public.temp_transf_alimento_granja a
INNER JOIN 
    granjas b ON a."WERKS" = b."id_sap" 
WHERE a."WERKS" in (SELECT "id_sap" FROM granjas);
"""    



##########################################################################################################################
##########################################################################################################################
##########################################################################################################################
# Querys For testing tables only
query = """
SELECT 
    MATDOC.BUDAT AS "Fecha",
    MATDOC.MATNR AS "CodigoMaterial",
    MAKT.MAKTX AS "DescMaterial",
    MATDOC.MENGE AS "Cantidad Despachada",
    MATDOC.WERKS AS "Centro",
    MATDOC.LGORT AS "Almacén",
    MATDOC.BWART AS "Tipo de Movimiento",
    MATDOC.BUKRS AS "Centro de Entrega",  -- Agregado BURKS
    MATDOC.MBLNR AS "Número de Documento",
    MATDOC.EBELN AS "Orden de Transferencia"
FROM 
    SAPHANADB.MATDOC
INNER JOIN 
    SAPHANADB.MAKT ON MATDOC.MATNR = MAKT.MATNR
WHERE 
    MATDOC.BWART = '641'  -- Tipo de movimiento 641
    --AND MATDOC.WERKS = '4089'  -- Centro desde el cual se despachó
    --AND MATDOC.MATNR BETWEEN  '000000000000105000' AND '000000000000105999'
    AND MATDOC.BUDAT >= TO_CHAR(CURRENT_DATE, 'YYYY') || '0101' --'20240715'
ORDER BY 
    MATDOC.BUDAT ASC;
"""

# Transferencia de Alimento a granja  
# MATDOC
# TIPO DE MOVIMIENTO 641
# EL ORIGEN SIEMPRE ES ABA
# FILTROS GRANJA + MOVIMIENTO 641 + MATERIAL 105000 A 105999
# EN EL ADMINISTRATIVO DEBE ESTAR LA CREACION DEL LOTE
# SALEN DEL 1000 ABA
# la orden es Orden de Transferencia


# Transferencia de huevos a incubadora
# MATDOC
# TIPO DE MOVIMIENTO 641
# SALEN DE LAS GRANJAS DE PRODUCCION
# FILTROS GRANJA + MOVIMIENTO 641 + MATERIAL 000000000000115000
# en app recepcion y distribucion de aves, agregar granja, numero de documento


# Transferencia de pollitos bb a granja engorde
# MATDOC
# TIPO DE MOVIMIENTO 641
# SALEN DEL 3000 incubadora
# FILTROS GRANJA + MOVIMIENTO 641 + MATERIAL 000000000000120000 Y 000000000000120005 , AGREGAR EN EL ADMIN ESA LISTA
# en app recepcion y distribucion de aves, agregar granja, numero de documento


# Transferencia de cria a producción

# inventarios
query_inventories = """
SELECT
    MATDOC.MATNR AS MATERIAL,
    MAKT.MAKTX AS DESCRIPCION_DEL_MATERIAL,
    MATDOC.WERKS AS CENTRO,
    T001W.NAME1 AS DESCRIPCION_DEL_CENTRO,
    MATDOC.LGORT AS ALMACEN,
    T001L.LGOBE AS DESCRIPCION_DEL_ALMACEN,
    MATDOC.BWART AS CLASE_DE_MOVIMIENTOS,
    T156HT.BTEXT AS DESCR_CLASE_DE_MOVIMIENTOS,
    MATDOC.SOBKZ AS STOCK_ESPECIAL,
    MATDOC.MBLNR AS DOCUMENTO_MATERIAL,
    MATDOC.ZEILE AS POSICION_DOCUMENTO_MATERIAL,
    MATDOC.BKTXT AS TEXTO_DOCUMENTO_MATERIAL,
    MATDOC.BUDAT AS FECHA_CONTABILIZACION,
    MATDOC.BLDAT AS FECHA_DOCUMENTO,
    MATDOC.CPUDT AS FECHA_REGISTRO,
    MATDOC.ERFMG AS CANTIDAD_EN_UM_ENTRADA,
    MATDOC.ERFME AS UNIDAD_MEDIDA_ENTRADA,
    MATDOC."/CWM/MENGE" AS CANTIDAD_EN_UM_PARALELA,
    MATDOC."/CWM/MEINS" AS UNIDAD_MEDIDA_PARALELA,
    MATDOC.MJAHR AS EJERCICIO,
    MATDOC.CHARG AS LOTE,
    MATDOC.USNAM AS USUARIO,
    MATDOC.SHKZG AS INDICADOR
FROM SAPHANADB.MATDOC
LEFT OUTER JOIN SAPHANADB.MAKT 
    ON MAKT.MATNR = MATDOC.MATNR
    AND MAKT.SPRAS = 'S'
LEFT OUTER JOIN SAPHANADB.T001W
    ON T001W.WERKS = MATDOC.WERKS
LEFT OUTER JOIN SAPHANADB.T001L
    ON T001L.WERKS = MATDOC.WERKS
    AND T001L.LGORT = MATDOC.LGORT
LEFT OUTER JOIN SAPHANADB.T156HT
    ON T156HT.BWART = MATDOC.BWART
    AND T156HT.SPRAS = 'S'
WHERE MATDOC.MJAHR = '2024'
  AND MATDOC.BUDAT BETWEEN '20240101' AND '20241231';
"""






