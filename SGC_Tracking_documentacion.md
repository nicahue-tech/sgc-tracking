DOCUMENTACIÓN DEL SISTEMA SGC TRACKING

ESTADO ACTUAL

SGC Tracking está completo y funcionando en producción desde julio de dos mil veintiséis. Vive en la carpeta usuarios luis proyectos sgc_tracking en la Mac de Luis, con control de versiones en git y respaldo remoto en GitHub, en git arroba github punto com dos puntos nicahue guion tech barra sgc guion tracking punto git.

DIAGRAMA DE FLUJO DEL SISTEMA, EN TEXTO

Paso uno. PC de la oficina, Windows, con Excel. El archivo tracking punto xlsm contiene una macro llamada ActualizarSGCTracking. Al ejecutarla con alt más F8, la macro refresca la conexión ODBC contra el CRM de la empresa, trayendo los datos más recientes, y después copia la hoja Data y la exporta como archivo csv llamado sgc_tracking punto csv, guardándolo dentro de una carpeta llamada informes en el escritorio, que está sincronizada con OneDrive.

Paso dos. OneDrive sincroniza automáticamente ese archivo csv desde el PC de la oficina hacia la misma carpeta informes dentro de la cuenta de OneDrive de Luis, replicada en su Mac en la ruta usuarios luis Library CloudStorage OneDrive guion FundacionHogardeCristo Escritorio informes.

Paso tres. En la Mac de Luis, un agente de launchd, configurado como un archivo plist en Library LaunchAgents, vigila permanentemente esa ruta exacta del archivo sgc_tracking punto csv. En cuanto detecta que el archivo cambió, dispara automáticamente la ejecución del programa Python, sin que Luis tenga que hacer nada manual en su Mac.

Paso cuatro. El programa Python, orquestado por programa_listas punto py, ejecuta en orden, datos_entrada punto py, que lee el csv y la configuración, calculo punto py, que aplica los filtros de negocio y calcula todos los indicadores, y reportes punto py, que genera el archivo dashboard_sgc_tracking punto xlsx dentro de la carpeta reportes_generados.

Paso cinco. Luis puede en cualquier momento ejecutar manualmente el comando actualizarSGC en su Terminal, que corre todo el proceso anterior y abre el Excel resultante automáticamente. También puede ejecutar el comando enviarSGC, que toma ese mismo dashboard y lo envía por correo electrónico a la lista de supervisores configurada en destinatarios punto txt, usando Gmail con una contraseña de aplicación guardada en credenciales_correo punto txt. Este envío es siempre una decisión manual de Luis, nunca ocurre automáticamente.

ARCHIVOS DEL PROYECTO

Módulos de código Python, bitacora punto py, que registra todo evento del sistema en sistema punto log. datos_entrada punto py, que lee config punto txt y carga el csv. calculo punto py, que contiene toda la lógica de negocio, filtros, e indicadores. reportes punto py, que genera el Excel final con sus hojas, colores, y enlaces de navegación. notificaciones punto py, que arma y envía el correo. programa_listas punto py, el orquestador central.

Archivos de configuración en texto plano, separados del código, config punto txt, con la ruta de la carpeta informes y el nombre del archivo csv. nomina punto txt, con cada ejecutivo, su supervisor, y su tipo, outbound o inbound. metas punto txt, con las metas independientes de acuerdo y reajuste para el global, cada supervisor, y los ejecutivos outbound. dias_habiles punto txt, con el total de días hábiles de cada mes, que Luis ingresa manualmente considerando los feriados. feriados punto txt, agregado recientemente, con las fechas exactas de los feriados chilenos del año, para que el sistema los excluya del conteo de días hábiles ya transcurridos. destinatarios punto txt y credenciales_correo punto txt, ambos excluidos de git por contener información sensible o variable.

Archivo de la macro, macro, que contiene el código Visual Basic de ActualizarSGCTracking, guardado también en el repositorio para referencia.

REGLAS DE NEGOCIO PRINCIPALES

Un acuerdo cuenta cuando el producto es Membresía, la columna Tipo transacción dice Nuevo acuerdo, y el estado del acuerdo es Nuevo, Vigente, o Vigente guion Nuevo Medio de Pago, sumando la columna Monto Final base. Un reajuste cuenta cuando el tipo de transacción es Aumento de aporte, el estado es Activo, el producto es Membresía, y el estado del acuerdo es alguno de los mismos tres válidos, sumando la columna Variación monto.

Para cada entidad, ejecutivo, supervisor, o global, se calculan, monto acumulado, cantidad de operaciones, cuota promedio, promedio diario real, proyectado a cierre de mes, meta asignada cuando corresponde, porcentaje de avance sobre la meta, monto diario requerido para alcanzarla, y porcentaje proyectado sobre la meta, que funciona como semáforo de riesgo, en rojo bajo setenta por ciento, naranjo entre setenta y noventa y nueve coma nueve, y verde desde cien por ciento.

Los días hábiles transcurridos se cuentan de lunes a viernes, excluyendo además las fechas exactas listadas en feriados punto txt. Un movimiento registrado en fin de semana o feriado sí se suma al acumulado, pero ese día no cuenta como día hábil adicional. Las metas de los tres niveles son valores independientes de presupuesto, nunca la suma de los niveles inferiores. Los ejecutivos inbound no tienen meta individual pero sí suman a los totales de su equipo y al global. El sistema recalcula todo desde cero en cada ejecución, sin acumular resultados de corridas anteriores.

ESTRUCTURA DEL DASHBOARD DE SALIDA

El archivo Excel final trae una hoja Global, con los totales de acuerdo y reajuste, más una tabla de avance diario para cada tipo. Una hoja por cada supervisor, con el total de su equipo y el detalle individualizado de cada uno de sus ejecutivos, ordenado como ranking. Una hoja Ejecutivos, con el ranking completo de toda la operación. Todas las hojas tienen enlaces de navegación cruzada en la primera fila, y colores aplicados a columnas clave para facilitar la lectura.

PENDIENTES CONOCIDOS

Existe una diferencia menor pendiente de revisar en el cálculo de reajustes, que Luis decidió dejar para más adelante por no ser significativa. El filtro de donaciones ya está definido en el diseño original pero no se procesa activamente todavía. A futuro, Luis planea construir una versión web de este sistema en Python con Flask, alojada en Render, con acceso por perfiles, como parte de un dominio personal llamado blindmachine punto ai, proyecto que se está trabajando en un chat separado.

PREFERENCIAS DE TRABAJO DE LUIS

Luis es ciego y usa VoiceOver en macOS. Prefiere avanzar siempre paso a paso, una sola instrucción a la vez, esperando confirmación antes de continuar. Para código, siempre se debe entregar el archivo completo para reemplazar entero, nunca fragmentos parciales, entregado dentro de un bloque con triple comilla invertida para que aparezca el botón de copiar. Para pasos de Terminal, se necesita el detalle completo de cada comando por separado. Para pasos de TextEdit, basta con indicar que pegue el código y lo guarde con un nombre, sin detallar cada tecla. Cuando el pegado de un archivo largo falla, la alternativa más confiable es generar el archivo como descarga directa para que Luis lo mueva con el Finder a la carpeta del proyecto, en vez de copiar y pegar en el editor.
