# Ficha técnica: microdatos de varicela individual — Sivigila

Esta carpeta contiene microdatos del evento **Varicela Individual** (código **831**) del Sistema Nacional de Vigilancia en Salud Pública de Colombia (Sivigila), administrado por el Instituto Nacional de Salud (INS). Sivigila reúne las notificaciones de eventos de interés en salud pública; estos archivos corresponden a registros individuales de varicela publicados por el INS para consulta y análisis. El código 831 identifica la notificación individual, distinta de la notificación colectiva de varicela (código 830).

## Fuente y descarga

Fuente: [Buscador de microdatos de Sivigila del INS](https://portalsivigila.ins.gov.co/Paginas/Buscador.aspx).

Para obtener los archivos desde la fuente original:

1. Abrir el buscador de microdatos.
2. Seleccionar **Varicela Individual** como evento y elegir el año deseado.
3. Pulsar **Buscar** y solicitar la descarga del resultado. El portal pide correo electrónico, entidad, nombre y propósito de uso; envía el enlace de descarga al correo indicado.
4. Repetir la consulta para cada año requerido.

El INS describe estas bases como **depuradas, nominales y sin datos de identificación personal**. La disponibilidad y el contenido del portal pueden cambiar con el tiempo; para una versión actualizada, consultar siempre la fuente original.

## Archivos y cobertura

Hay **19 archivos**, uno por año de **2007 a 2025**, sin años faltantes en ese intervalo. El patrón de nombre es `Datos_<año>_831.xlsx`; por ejemplo, `Datos_2007_831.xlsx` y `Datos_2025_831.xlsx`.

Los originales están en `excel/`, en formato **Excel (`.xlsx`)**. Cada uno tiene una hoja llamada `Datos`, con encabezados de variables y filas de registros individuales. Los nombres de las columnas son códigos o abreviaturas del sistema, como `FEC_NOT` (fecha de notificación), `SEMANA` (semana epidemiológica), `ANO` (año epidemiológico), `EDAD`, `SEXO` y `COD_DPTO_O` (departamento de ocurrencia). También hay variables sobre residencia, atención, clasificación y desenlace del caso. Los códigos geográficos y otras categorías deben interpretarse con sus definiciones, no como valores numéricos continuos.

Para generar una copia CSV por año en `csv/`, desde la raíz del repositorio:

```bash
.venv/bin/python scripts/processing/convert_sivigila_excel_to_csv.py
```

El script usa `openpyxl` (incluido en `scripts/requirements.txt`), conserva el orden y los valores de las columnas sin depuración y escribe en UTF-8. Si un CSV ya existe, lo omite; `--overwrite` permite regenerarlo. Los CSV derivados no se incluyen en Git.

El significado de las columnas y de varios valores codificados se documenta en el [diccionario de datos](dic_datos.md). El notebook [`sivigila_raw_explore.ipynb`](../../../notebooks/sivigila_raw_explore.ipynb) permite explorar los archivos. Consulte el diccionario antes de combinar años o construir indicadores; algunas variables pueden estar vacías, depender de otras respuestas o requerir criterios específicos de depuración.

## Consideraciones de uso

- Los registros son **notificaciones de vigilancia**, no una medición de todos los casos de varicela ocurridos en la población. Los conteos directos tampoco son tasas de incidencia: para calcular tasas se necesitan denominadores poblacionales y una definición explícita de caso.
- Para agrupar por año o semana epidemiológica, revise `ANO` y `SEMANA`. `FEC_NOT` es la fecha de notificación y puede responder a una pregunta distinta de la fecha de inicio de síntomas (`INI_SIN`).
- Antes de contar casos, revise las variables de clasificación y ajuste (`TIP_CAS`, `AJUSTE` y las variables de estado final) y documente los filtros aplicados. Para comparar resultados con publicaciones oficiales, consulte el protocolo y la metodología del INS vigentes para el periodo analizado.
- Conserve los archivos originales como fuente y realice cualquier limpieza o transformación en una copia derivada.

Referencias: [portal Sivigila del INS](https://portalsivigila.ins.gov.co/) · [protocolo de vigilancia de varicela del INS](https://www.ins.gov.co/Direcciones/Vigilancia/sivigila/Protocolos/PRO%20Varicela.pdf).

## Esquema y diccionario de datos

Los 19 CSV locales de 2007–2025 tienen los mismos 69 encabezados, en el orden
de la tabla. Cada fila es una notificación individual. CSV no guarda tipos
físicos y Excel permite celdas de tipos diferentes: los tipos indicados son
lógicos. Los procesadores leen inicialmente todas las columnas como texto
y convierten solo los campos necesarios, conservando códigos y faltantes.

Las fechas pueden incluir hora y usar día/mes/año; `INI_SIN` de 2013 usa
mes/día/año en el procesamiento por fechas. No se debe imponer el formato
ISO descrito por el diccionario al texto real sin validarlo. Una celda vacía
significa dato ausente, no cero. El catálogo de códigos detallado está en
[`dic_datos.md`](dic_datos.md); los campos sin catálogo local se describen
con el alcance verificable de su encabezado.

| Columna | Tipo | Descripción |
| --- | --- | --- |
| `CONSECUTIVE` | texto | Identificador consecutivo del registro en la fuente; no se usa como clave de deduplicación. |
| `COD_EVE` | texto | Codigo del evento. Código del Evento según CIE X ó Código del Instituto Nacional de Salud. |
| `FEC_NOT` | texto de fecha/hora | Fecha de notificación; texto de fecha/hora original. |
| `SEMANA` | entero lógico; leer como texto antes de validar | Semana. Semana epidemiológica según calendario vigente Rango. 1-53 |
| `ANO` | entero lógico; leer como texto antes de validar | Año. Año correspondiente a la Semana Epidemiológica |
| `COD_PRE` | texto | Código del prestador de servicios de salud. Código asignado en el SGSSS a los prestadores de servicios de salud que se hayan registrado en el “Registro Especial de Prestadores de Servicios de Salud” Ejemplo: 52 001 00001 |
| `COD_SUB` | texto | Código de prestador de servicios de salud – subindice. Código asignado en el SGSSS a los prestadores de servicios de salud que indica sede ó territorio. * |
| `EDAD` | entero lógico; leer como texto antes de validar | Edad. 0 = No aplica, Edad en números en enteros del paciente |
| `UNI_MED` | código categórico; leer como texto | Unidad de medida de la edad. 0 = No aplica, 1 = Años, 2 = Meses, 3 = Días, 4 = Horas, 5 = Minutos |
| `SEXO` | código categórico; leer como texto | Sexo. M = Masculino, F = Femenino, I = Indeterminado |
| `COD_PAIS_O` | texto | Codigo del pais de ocurrencia. Código de país internacional |
| `COD_DPTO_O` | texto | Codigo del departamento de ocurrencia. Código del Departamento Según registro Divipola fuente DANE. Ejemplo: Nariño = 52 |
| `COD_MUN_O` | texto | Codigo del municipio de ocurrencia. Código DIVIPOLA municipio |
| `AREA` | código categórico; leer como texto | Area geografica. 1 = Cabecera Municipal 2 =, Centro Poblado 3 = Rural, Disperso |
| `OCUPACION` | texto | Código de ocupación original; el diccionario local no especifica su catálogo. |
| `TIP_SS` | código categórico; leer como texto | Tipo de regimen en salud. C = Contributivo, S = Subsidiado, P = Excepción, E = Especial, N = No Asegurado |
| `COD_ASE` | texto | Código de la entidad responsable de la atención del paciente. Código asignado por el MPS a la Administradora. Si se selecciona la opción 5= no afiliado en la variable tipo de régimen en salud, se desactiva la variable código de administradora. Para las demás opciones es obligatorio su diligenciamiento. |
| `PER_ETN` | código categórico; leer como texto | Pertenencia etnica. Es el código asignado por el DANE a la pertenencia étnica, se omiten las etnias consideradas en la clasificación DANE que no tienen evidencia epidemiológica de comportamiento especial para los eventos de interés en salud pública. Se usa la codificación estándar para las de interés: 1 = Indígena, 2 = ROM, Gitano, 3 = Raizal, 4 = Palenquero, 5 = Negro-Mulato-Afro Colombiano, 6 = Otro |
| `GRU_POB` | texto | Grupo poblacional |
| `nom_grupo` | texto | Nombre del grupo poblacional |
| `estrato` | código categórico; leer como texto | Estrato socioeconomico. 1 = Estrato_1, 2 = Estrato_2, 3 = Estrato_3, 4 = Estrato_4, 5 = Estrato_5, 6 = Estrato_6 |
| `GP_DISCAPA` | código categórico; leer como texto | Grupo poblacional - discapacitados. 1 = Sí 2 = No |
| `GP_DESPLAZ` | código categórico; leer como texto | Grupo poblacional - desplazados. 1 = Sí 2 = No |
| `GP_MIGRANT` | código categórico; leer como texto | Grupo poblacional - migrantes. 1 = Sí 2 = No |
| `GP_CARCELA` | código categórico; leer como texto | Grupo poblacional - carcelarios. 1 = Sí 2 = No |
| `GP_GESTAN` | código categórico; leer como texto | Grupo poblacional - gestantes. 1 = Sí 2 = No |
| `sem_ges` | entero lógico; leer como texto antes de validar | Semana gestante. >=1 AND <=45. (Si GP_GESTAN=1) |
| `GP_INDIGEN` | código categórico; leer como texto | Indicador del grupo poblacional indigentes según el diccionario local: 1 sí, 2 no; no es pertenencia étnica indígena. |
| `GP_POBICFB` | código categórico; leer como texto | Grupo poblacional - poblacion infantil a cargo del ICBF. 1 = Sí 2 = No |
| `GP_MAD_COM` | código categórico; leer como texto | Grupo poblacional - madres comunitarias. 1 = Sí 2 = No |
| `GP_DESMOVI` | código categórico; leer como texto | Grupo poblacional - desmovilizados. 1 = Sí 2 = No |
| `GP_PSIQUIA` | código categórico; leer como texto | Grupo poblacional - poblacion en centros psiquiatricos. 1 = Sí 2 = No |
| `GP_VIC_VIO` | código categórico; leer como texto | Grupo poblacional - victima de violencia. 1 = Sí 2 = No |
| `GP_OTROS` | código categórico; leer como texto | Grupo poblacional - otros. 1 = Sí 2 = No |
| `fuente` | código categórico; leer como texto | Fuente. 1 = Notificación rutinaria, 2 = Busqueda Activa Institucional, 3 = Vigilancia intensificada, 4 = Busqueda Activa Comunitaria, 5 = Investigaciones. (Si AJUSTE=0 ó 7) |
| `COD_PAIS_R` | texto | Codigo del pais de residencia |
| `COD_DPTO_R` | texto | Codigo del departamento de residencia. Código del Departamento Según registro Divipola fuente DANE. Ejemplo: Nariño = 52 |
| `COD_MUN_R` | texto | Codigo del municipio de residencia. Código DIVIPOLA municipio |
| `COD_DPTO_N` | texto | Codigo del departamento de notificacion. Código del Departamento Según registro Divipola fuente DANE. Ejemplo: Nariño = 52 |
| `COD_MUN_N` | texto | Codigo del municipio de notificacion. Código DIVIPOLA municipio |
| `FEC_CON` | texto de fecha/hora | Fecha de constitución o inicio de actividades asistenciales. AAAA-MM-DD (Año-Mes-Día separado por guiones) (Norma ISO 8601,NTC 1034) |
| `INI_SIN` | texto de fecha/hora | Fecha de inicio de síntomas; texto de fecha/hora original. |
| `TIP_CAS` | código categórico; leer como texto | Clasificacion inicial del caso. 1 = Sospechoso, 2 = Probable, 3 = Confirmado por Laboratorio, 4 = Confirmado por Clínica, 5 = Confirmado por Nexo Epidemiológico. |
| `PAC_HOS` | código categórico; leer como texto | Hospitalizado. 1 = Sí 2 = No |
| `FEC_HOS` | texto de fecha/hora | Fecha de hospitalizacion. AAAA-MM-DD (Año-Mes-Día separado por guiones) (Norma ISO 8601,NTC 1034) |
| `CON_FIN` | código categórico; leer como texto | Condicion final. 0 = No sabe - no responde, 1 = Vivo, 2 = Muerto |
| `FEC_DEF` | texto de fecha/hora | Fecha de defuncion. AAAA-MM-DD (Año-Mes-Día separado por guiones) (Norma ISO 8601,NTC 1034). (Si CON_FIN=2) |
| `AJUSTE` | código categórico; leer como texto | seguimiento y clasificacion final del caso. 0 = No aplica - No Ajusta - 1ª Vez, 3 = Confirmado por Laboratorio, 4 = Confirmado por Clínica, 5 = Confirmador por Nexo Epidemiológico, 6 = Descartado, 7 = Otro ajuste, D = Descarte por error de digitacion |
| `FECHA_NTO` | texto de fecha/hora | Fecha de nacimiento. AAAA-MM-DD (Año-Mes-Día separado por guiones) (Norma ISO 8601,NTC 1034) |
| `CBMTE` | texto | Causa basica de defuncion o muerte. Código de la CIE X (Si CON_FIN=2) |
| `FEC_ARC_XL` | texto de fecha/hora | Fecha de creacion del archivo de Excel. AAAA-MM-DD (Año-Mes-Día separado por guiones) (Norma ISO 8601,NTC 1034) |
| `FEC_AJU` | texto de fecha/hora | Fecha de ajuste. Corresponde a la fecha del sistema (systemdate) o a la fecha efectiva de digitación del registro o realizar un ajuste a un registro previo |
| `FM_FUERZA` | texto | Fuerza militar. 1 = GAB 2 = CGF 3 = EJC 4 = ARC 5 = FAC 6 = HMC 7 = POL 8 = SIN |
| `FM_UNIDAD` | texto | Unidad - codigo de la unidad militar. Código de la Unidad Militar según tabla de Unidades Militares |
| `FM_GRADO` | texto | Grado - codigo del grado militar. Código de la Grado Militar según tabla de Grados Militares |
| `confirmados` | texto | Confirmados |
| `va_sispro` | texto | Sistema Integral de Informacion para la Proteccion Social |
| `Estado_final_de_caso` | texto | Estado final del caso |
| `nom_est_f_caso` | texto | Nombre de Estado final del caso |
| `Nombre_upgd` | texto | Nombre de la unidad primaria generadora de datos que registró el caso. |
| `Pais_ocurrencia` | texto | Pais de ocurrencia |
| `Nombre_evento` | texto | Nombre del evento |
| `Departamento_ocurrencia` | texto | Departamento ocurrencia |
| `Municipio_ocurrencia` | texto | Municipio ocurrencia |
| `Pais_residencia` | texto | Pais residencia |
| `Departamento_residencia` | texto | Departamento residencia |
| `Municipio_residencia` | texto | Municipio residencia |
| `Departamento_Notificacion` | texto | Departamento notificacion |
| `Municipio_notificacion` | texto | Municipio notificacion |
