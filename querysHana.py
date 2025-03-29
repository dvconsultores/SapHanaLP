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
AND WERKS NOT IN ('3000')
"""

# Warehouse Ready
query_warehouse = """
SELECT LGORT, LGOBE, T001L.WERKS
FROM SAPHANADB.T001L 
INNER JOIN SAPHANADB.T001W ON T001L.WERKS = T001W.WERKS
WHERE T001W.MANDT = '120' 
-- AND T001L.WERKS >= '4000'
AND T001W.NAME1 NOT LIKE '%NO USAR%' 
AND T001L.LGOBE NOT LIKE '%NO USAR%'
-- AND T001L.WERKS = '2000'
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
--WHERE 	temp_warehouse.id_sap = '2000'    
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
INNER JOIN SAPHANADB.T001W ON EKPO1.WERKS = T001W.WERKS
INNER JOIN SAPHANADB.EKKO ON EKPO1.EBELN = EKKO.EBELN -- Join with EKKO to get LIFNR
WHERE T001W.NAME1 NOT LIKE '%NO USAR%' 
  --AND EKPO1.EBELN = '4500015040'
  AND EKPO1.AEDAT >= '20230301'
  AND EKPO1.MATNR = '000000000000110001' -- Material number for machos
GROUP BY EKPO1.EBELN, EKPO1.UNIQUEID, EKKO.LIFNR, EKPO1.WERKS, EKPO1.MENGE, EKPO2.MENGE
"""


# Purchase Orders in Process Temporary table
query_purchase_orders_temp = """
SELECT 
    a.orden_compra,
    trim(a.id_sap) id_sap,
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
    AND MATDOC.MATNR IN ('000000000000105012'
    , '000000000000105003'
    , '000000000000105004'
    , '000000000000105013'
    , '000000000000105027'
    , '000000000000105028'
    , '000000000000105021'
    , '000000000000105007'
    , '000000000000105001'
    , '000000000000105002'
    , '000000000000105005'
    , '000000000000105006'
    , '000000000000105025'
    , '000000000000105016'
    ) -- CRIA, PRODUCCION Y ENGORDE
    AND MATDOC.BUDAT >= '20240301'
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
        WHEN a."MATNR" IN ('000000000000105012', '000000000000105003', '000000000000105016') THEN 'CRIA'
        WHEN a."MATNR" IN ('000000000000105004', '000000000000105013', '000000000000105027', '000000000000105028', '000000000000105021', '000000000000105007') THEN 'PRODUCCION'
        WHEN a."MATNR" IN ('000000000000105001', '000000000000105002', '000000000000105005','000000000000105006', '000000000000105025') THEN 'ENGORDE'
        ELSE 'ENGORDE'
    END AS "CATEGORY"
FROM 
    public.temp_transf_alimento_granja a
INNER JOIN 
    granjas b ON a."WERKS" = b."id_sap" 
WHERE a."WERKS" in (SELECT "id_sap" FROM granjas);
"""    


# Purchase Orders in Process
query_trasnfer_incubator_fattening = """
SELECT EKPO1.EBELN AS "orden_compra"
    , EKPO1.UNIQUEID AS "id_sap"
    , '1' AS "lote"
    , '3000' AS "incubadora"
    , EKPO1.WERKS AS "granjaIdId"
    , EKPO1.MENGE AS "cantidad" -- Replace NULL with 0 for cant_machos
    , EKPO1.AEDAT
    , EKPO1.EBELN 
    , '000000000000' AS "transporteIdId"
FROM SAPHANADB.EKPO EKPO1
 INNER JOIN SAPHANADB.EKKO ON EKPO1.EBELN = EKKO.EBELN -- Join with EKKO to get LIFNR
WHERE EKPO1.AEDAT >= '20240301'
--AND EKPO1.EBELN = '4500015040'
--AND EKPO1.MATNR = '000000000000120000' -- Material number
"""


# Purchase Orders in Process Temporary table
query_trasnfer_incubator_fattening_temp = """
SELECT 
    trim(a.id_sap) id_sap,
	a.orden_compra,
	a.cantidad,
	b.id,
    g.id,
	c.id
FROM 
    temp_incubadoras_engorde a
INNER JOIN 
    granjas g ON a."granjaIdId" = g.id_sap
INNER JOIN incubadoras b on a."incubadora" = b."id_sap"
INNER JOIN transportes c on a."transporteIdId" = c."id_sap"
"""

# Outbound Delivery
query_ordenes_salida_cria_produccion = """
SELECT 
    MATDOC.AUFNR AS "orden",
    MATDOC.WERKS AS "granjaOrigenIdId",
    trim(MATDOC.UMWRK) AS "granjaDestinoIdId",
    MATDOC.LGORT AS "almacen",
    MATDOC.BUDAT AS "fecha",
    SUM(MATDOC.ERFMG) AS "cantidad"
FROM SAPHANADB.MATDOC
WHERE MATDOC.BWART = '303'
AND MATDOC.MATNR IN ('000000000000110002', '000000000000110003')
AND MATDOC.AUFNR = '121000000016'
AND MATDOC.WERKS IN ('2000', '2002')
GROUP BY 
    MATDOC.AUFNR,
    MATDOC.WERKS,
    MATDOC.UMWRK,
    MATDOC.LGORT,
    MATDOC.BUDAT
ORDER BY MATDOC.BUDAT DESC
"""   

# Outbound Delivery
temp_query_ordenes_salida_cria_produccion = """
SELECT 
    a.orden as id_sap,
    a.orden,
    a.cantidad,
    b.id as granjaOrigenIdId,
    c.id as granjaDestinoIdId,
    '3730' as transporte,
	d.id as galpon
FROM 
    temp_ordenes_salida_cria_produccion a
INNER JOIN 
    granjas b ON a."granjaOrigenIdId" = b.id_sap
INNER JOIN 
    granjas c ON a."granjaDestinoIdId" = c.id_sap
INNER JOIN 
    galpones d ON a.almacen = d.id_sap
WHERE d."granjaIdId" = (select f.id 
                         from temp_ordenes_salida_cria_produccion e 
						 INNER JOIN granjas f ON e."granjaDestinoIdId" = f.id_sap  )
"""    


# Outbound Delivery
query_ordenes_salida_reproductora_incubadora = """
SELECT 
    MATDOC.AUFNR AS "orden",
    MATDOC.WERKS AS "granjaOrigenIdId",
    '3000' AS "granjaDestinoIdId",
    MATDOC.LGORT AS "almacen",
    MATDOC.BUDAT AS "fecha",
    SUM(MATDOC.ERFMG) AS "cantidad"
FROM SAPHANADB.MATDOC
WHERE MATDOC.BWART = '101'
AND MATDOC.MATNR IN ('000000000000115000')
AND MATDOC.AUFNR = '700200000022'
--AND MATDOC.WERKS IN ('2000', '2002')
AND MATDOC.BUDAT >= '20240301'
GROUP BY 
    MATDOC.AUFNR,
    MATDOC.WERKS,
    MATDOC.UMWRK,
    MATDOC.LGORT,
    MATDOC.BUDAT
ORDER BY MATDOC.BUDAT DESC
"""   

# Outbound Delivery
temp_query_ordenes_salida_reproductora_incubadora = """
SELECT 
    a.orden as id_sap,
    a.orden,
    a.cantidad,
    b.id as granjaOrigenIdId,
    c.id as granjaDestinoIdId,
    '3730' as transporte,
	d.id as galpon
FROM 
    temp_ordenes_salida_cria_produccion a
INNER JOIN 
    granjas b ON a."granjaOrigenIdId" = b.id_sap
INNER JOIN 
    granjas c ON a."granjaDestinoIdId" = c.id_sap
INNER JOIN 
    galpones d ON a.almacen = d.id_sap
WHERE d."granjaIdId" = (select f.id 
                         from temp_ordenes_salida_cria_produccion e 
						 INNER JOIN granjas f ON e."granjaDestinoIdId" = f.id_sap  )"""
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
    AND MATDOC.BUDAT >= '20240301' --'20240715'
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


# Transferencia de gallinas a reproductoras
# MATDOC
# TIPO DE MOVIMIENTO 303
# SALEN DEL 3000 incubadora
# FILTROS GRANJA + MOVIMIENTO 303 + MATERIAL 000000000000110002
# en app recepcion y distribucion de aves, agregar granja, numero de documento

# Transferencia de machos a reproductoras
# MATDOC
# TIPO DE MOVIMIENTO 303
# SALEN DEL 3000 incubadora
# FILTROS GRANJA + MOVIMIENTO 303 + MATERIAL 000000000000110003
# en app recepcion y distribucion de aves, agregar granja, numero de documento


# Transferencia de cria a producción

# inventarios
query_inventories = """
SELECT 
    MATDOC.MANDT AS EMPRESA,
    SUBSTRING(MATDOC.MATNR, LENGTH(MATDOC.MATNR) - 5, 6) AS MATERIAL,
    MAKT.MAKTX AS DESCRIPCION_DEL_MATERIAL,
    MATDOC.WERKS AS CENTRO,
    T001W.NAME1 AS DESCRIPCION_DEL_CENTRO,
    MATDOC.LGORT AS ALMACEN,
    T001L.LGOBE AS DESCRIPCION_DEL_ALMACEN,
    MATDOC.BWART AS CLASE_DE_MOVIMIENTOS,
    MAX(T156HT.BTEXT) AS DESCR_CLASE_DE_MOVIMIENTOS,
    MATDOC.SOBKZ AS STOCK_ESPECIAL,
    MATDOC.MBLNR AS DOCUMENTO_MATERIAL,
    MATDOC.ZEILE AS POSICION_DOCUMENTO_MATERIAL,
    MATDOC.BKTXT AS TEXTO_DOCUMENTO_MATERIAL,
    TO_DATE(MATDOC.BUDAT, 'YYYYMMDD') AS FECHA_CONTABILIZACION,
    TO_DATE(MATDOC.BLDAT, 'YYYYMMDD') AS FECHA_DOCUMENTO,
    TO_DATE(MATDOC.CPUDT, 'YYYYMMDD') AS FECHA_REGISTRO,
    CASE
        WHEN MATDOC.SHKZG = 'S' THEN CAST(MATDOC.ERFMG AS DECIMAL)
        ELSE CAST(MATDOC.ERFMG AS DECIMAL) * -1
    END AS CANTIDAD_EN_UM_ENTRADA,
    MATDOC.ERFME AS UNIDAD_MEDIDA_ENTRADA,
    CASE
        WHEN MATDOC.SHKZG = 'S' THEN CAST(MATDOC."/CWM/MENGE" AS DECIMAL)
        ELSE CAST(MATDOC."/CWM/MENGE" AS DECIMAL) * -1
    END AS CANTIDAD_EN_UM_PARALELA,
    MATDOC."/CWM/MEINS" AS UNIDAD_MEDIDA_PARALELA,
    MATDOC.MJAHR AS EJERCICIO,
    MATDOC.CHARG AS LOTE,
    MATDOC.USNAM AS USUARIO,
    CASE 
        WHEN MATDOC.SHKZG = 'S' THEN 'Positivo' 
        WHEN MATDOC.SHKZG = 'H' THEN 'Negativo' 
        ELSE MATDOC.SHKZG 
    END AS INDICADOR,
    MATDOC.TCODE2 AS CODIGO_TRANSACCION
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
  AND MATDOC.BUDAT BETWEEN '20240101' AND '20241231'
  -- AND MATDOC.MBLNR = '4900120490'
GROUP BY 
    MATDOC.MANDT,
    MATDOC.MATNR,
    MAKT.MAKTX,
    MATDOC.WERKS,SOL
    T001W.NAME1,
    MATDOC.LGORT,
    T001L.LGOBE,
    MATDOC.BWART,
    MATDOC.SOBKZ,
    MATDOC.MBLNR,
    MATDOC.ZEILE,
    MATDOC.BKTXT,
    MATDOC.BUDAT,
    MATDOC.BLDAT,
    MATDOC.CPUDT,
    MATDOC.ERFMG,
    MATDOC.ERFME,
    MATDOC."/CWM/MENGE",
    MATDOC."/CWM/MEINS",
    MATDOC.MJAHR,
    MATDOC.CHARG,
    MATDOC.USNAM,
    MATDOC.SHKZG,
    MATDOC.TCODE2;
"""






