from pathlib import Path
import json, math, textwrap, base64, hashlib, shutil
from xml.sax.saxutils import escape
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image, Preformatted, KeepTogether
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon
import fitz
from PIL import Image as PILImage, ImageOps, ImageDraw

OUT=Path('reporte-final');OUT.mkdir(exist_ok=True)
E=next(Path('insumos').rglob('resumen-lighthouse.json')).parent
L=json.loads((E/'resumen-lighthouse.json').read_text())
FULL=json.loads((E/'lighthouse.report.json').read_text())
S=json.loads((E/'estado-offline.json').read_text())
M=json.loads((E/'manifest-verificado.json').read_text())
print('LIGHTHOUSE_SUMMARY',json.dumps(L,ensure_ascii=True))
GREEN=colors.HexColor('#073d32');LIGHT=colors.HexColor('#edf4f0');INK=colors.HexColor('#24372e');GRAY=colors.HexColor('#5e6f66');LINE=colors.HexColor('#cfded5')
W,H=595.276,841.89; CW=W-108
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='BodyReport',fontName='Helvetica',fontSize=10.2,leading=14.5,textColor=INK,spaceAfter=9,alignment=TA_JUSTIFY))
styles.add(ParagraphStyle(name='ReportH1',fontName='Helvetica-Bold',fontSize=19,leading=23,textColor=GREEN,spaceAfter=17))
styles.add(ParagraphStyle(name='ReportH2',fontName='Helvetica-Bold',fontSize=12,leading=16,textColor=GREEN,spaceBefore=10,spaceAfter=7))
styles.add(ParagraphStyle(name='CaptionReport',fontName='Helvetica',fontSize=8.2,leading=11,textColor=GRAY,spaceBefore=6,spaceAfter=12))
styles.add(ParagraphStyle(name='CellReport',fontName='Helvetica',fontSize=8.5,leading=11.3,textColor=INK))
styles.add(ParagraphStyle(name='CellHead',fontName='Helvetica-Bold',fontSize=8.5,leading=11.3,textColor=colors.white))
styles.add(ParagraphStyle(name='CodeReport',fontName='Courier',fontSize=7.8,leading=10.6,textColor=INK,backColor=LIGHT,borderPadding=8,spaceBefore=6,spaceAfter=12))
styles.add(ParagraphStyle(name='CoverTitle',fontName='Helvetica-Bold',fontSize=23,leading=30,alignment=TA_CENTER,textColor=GREEN,spaceAfter=20))
styles.add(ParagraphStyle(name='CoverCenter',fontName='Helvetica',fontSize=11,leading=17,alignment=TA_CENTER,textColor=INK,spaceAfter=12))
styles.add(ParagraphStyle(name='RefReport',fontName='Helvetica',fontSize=8.7,leading=12.5,leftIndent=18,firstLineIndent=-18,spaceAfter=11,textColor=INK,wordWrap='CJK'))
story=[]; sections=[]
def P(text): story.append(Paragraph(text,styles['BodyReport']))
def h2(text): story.append(Paragraph(text,styles['ReportH2']))
def sect(title,key):
    story.append(PageBreak()); p=Paragraph(title,styles['ReportH1']);p._bookmark=key;story.append(p);sections.append((title,key))
def code(text): story.append(Preformatted(textwrap.dedent(text).strip(),styles['CodeReport']))
def tbl(headers,rows,widths=None):
    data=[[Paragraph(escape(str(c)),styles['CellHead']) for c in headers]]+[[Paragraph(str(c),styles['CellReport']) for c in row] for row in rows]
    table=Table(data,colWidths=[CW*x for x in widths] if widths else [CW/len(headers)]*len(headers),repeatRows=1,hAlign='LEFT')
    table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),GREEN),('VALIGN',(0,0),(-1,-1),'TOP'),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,LIGHT]),('BOTTOMPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),8),('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),('LINEBELOW',(0,-1),(-1,-1),.5,LINE)]));story.append(table);story.append(Spacer(1,10))
def pic(name,caption,maxh=300,maxw=CW):
    path=E/name
    with PILImage.open(path) as im: iw,ih=im.size
    ratio=min(maxw/iw,maxh/ih)
    story.append(Image(str(path),width=iw*ratio,height=ih*ratio,hAlign='CENTER'));story.append(Paragraph(caption,styles['CaptionReport']))
def diagram(kind):
    d=Drawing(CW,245 if kind=='architecture' else 180)
    def box(x,y,w,h,title,sub=''):
        d.add(Rect(x,y,w,h,rx=6,fillColor=LIGHT,strokeColor=LINE));d.add(String(x+w/2,y+h-20,title,fontName='Helvetica-Bold',fontSize=10,fillColor=GREEN,textAnchor='middle'))
        for i,line in enumerate(sub.split('|')): d.add(String(x+w/2,y+h-37-i*13,line,fontName='Helvetica',fontSize=8,fillColor=INK,textAnchor='middle'))
    def arrow(x1,y1,x2,y2):
        d.add(Line(x1,y1,x2,y2,strokeColor=GREEN,strokeWidth=1.3));a=math.atan2(y2-y1,x2-x1);d.add(Polygon([x2,y2,x2-7*math.cos(a-.4),y2-7*math.sin(a-.4),x2-7*math.cos(a+.4),y2-7*math.sin(a+.4)],fillColor=GREEN,strokeColor=GREEN))
    if kind=='architecture':
        box(140,170,207,66,'Interfaz y router CSR','index.html + app.css + app.js');box(0,64,145,75,'IndexedDB','Incidencias y fotos|Catálogo local');box(171,64,145,75,'Service Worker','App Shell + caché|Control de fetch');box(342,64,145,75,'Web APIs','Cámara y ubicación|Notificación local');arrow(190,170,80,139);arrow(243,170,243,139);arrow(300,170,405,139);box(171,0,145,44,'GitHub Pages HTTPS','Archivos y catálogo JSON');arrow(243,64,243,44)
    elif kind=='lifecycle':
        box(0,100,145,65,'Registro','register en app.js');box(171,100,145,65,'Instalación','Precaché completa');box(342,100,145,65,'Activación','Limpieza y claim');arrow(145,132,171,132);arrow(316,132,342,132);box(171,0,145,65,'Intercepción fetch','Shell o catálogo|Actualización controlada');arrow(415,100,316,33);d.add(String(0,58,'Una actualización espera a que cierren',fontSize=8,fillColor=GRAY));d.add(String(0,44,'las pestañas de la versión anterior.',fontSize=8,fillColor=GRAY))
    elif kind=='write':
        box(0,100,145,65,'Formulario válido','Texto + foto + ubicación');box(171,100,145,65,'Transacción','readwrite + put');box(342,100,145,65,'oncomplete','Confirmar guardado');arrow(145,132,171,132);arrow(316,132,342,132);box(171,0,145,65,'Consulta persistente','getAll + orden por fecha|Disponible sin red');arrow(415,100,316,33)
    else:
        box(0,100,145,65,'Commit en main','Código versionado');box(171,100,145,65,'Validación','Sintaxis + PNG|Cuatro pruebas');box(342,100,145,65,'Publicación','Artefacto estático|GitHub Pages');arrow(145,132,171,132);arrow(316,132,342,132);box(171,0,145,65,'Comprobación HTTPS','Bitácora pública|Service Worker activo');arrow(415,100,316,33)
    story.append(d);story.append(Spacer(1,10))

class ReportDoc(SimpleDocTemplate):
    def afterFlowable(self,flowable):
        key=getattr(flowable,'_bookmark',None)
        if key:
            self.canv.bookmarkPage(key);self.canv.addOutlineEntry(flowable.getPlainText(),key,0,False);self.notify('TOCEntry',(0,flowable.getPlainText(),self.page,key))
def pageframe(c,doc):
    if doc.page==1:return
    c.setStrokeColor(LINE);c.line(54,H-39,W-54,H-39)
    c.setFont('Helvetica',8);c.setFillColor(GRAY);c.drawString(54,H-29,'UTGZ  |  Desarrollo y Gestión de Software');c.drawRightString(W-54,H-29,'Memoria técnica PWA')
    c.line(54,43,W-54,43);c.drawString(54,30,'EJE del Golfo  ·  Bitácora de operaciones');c.drawRightString(W-54,30,str(doc.page))

# Portada institucional sobria, siguiendo los datos y la jerarquía del formato UTGZ.
story.append(Spacer(1,24))
for text in ['<b>UNIVERSIDAD TECNOLÓGICA DE<br/>GUTIÉRREZ ZAMORA</b>','INGENIERÍA EN DESARROLLO Y GESTIÓN DE SOFTWARE']:
    story.append(Paragraph(text,styles['CoverCenter']));story.append(Spacer(1,12))
story.append(Spacer(1,25));story.append(Paragraph('Reporte técnico de desarrollo<br/>de la PWA EJE del Golfo',styles['CoverTitle']))
story.append(Paragraph('Bitácora de incidencias con funcionamiento sin conexión',styles['CoverCenter']))
story.append(Spacer(1,22));story.append(Paragraph('<b>ASIGNATURA</b><br/>Aplicaciones Web Progresivas',styles['CoverCenter']))
story.append(Paragraph('<b>ELABORADO POR</b><br/>Tania González Geronimo<br/>Alondra Aimee García Gómez',styles['CoverCenter']))
story.append(Paragraph('<b>DOCENTE</b><br/>Guillermo Martinez Maza',styles['CoverCenter']))
story.append(Paragraph('<b>GRUPO</b><br/>1010 AEI',styles['CoverCenter']))
story.append(Spacer(1,15));story.append(Paragraph('SEPTIEMBRE A DICIEMBRE DE 2026<br/>Gutiérrez Zamora, Veracruz<br/>27 de noviembre de 2026',styles['CoverCenter']))
story.append(PageBreak());story.append(Paragraph('Índice de contenido',styles['ReportH1']))
toc=TableOfContents();toc.levelStyles=[ParagraphStyle(name='TOCReport',fontName='Helvetica',fontSize=9.2,leading=14,textColor=INK,spaceBefore=5,leftIndent=0,firstLineIndent=0)];story.append(toc)
# El índice permanece en una sola página y conserva enlaces a los apartados.

sect('1 Introducción y justificación','s01')
P('EJE del Golfo es el contexto de un proyecto académico de transporte. Para esta actividad desarrollamos una copia independiente del sistema y añadimos una bitácora PWA destinada al personal de taller y operaciones. El problema atendido es la interrupción del registro y la consulta de incidencias cuando una unidad o una persona se encuentra sin acceso a internet. La solución conserva la interfaz y los reportes en el navegador, permitiendo continuar el trabajo localmente.')
P('Una aplicación web convencional que depende de cada respuesta del servidor puede dejar de mostrar sus vistas al perder la conexión. En esta entrega, el App Shell y sus recursos se precargan con un Service Worker, mientras que IndexedDB conserva los datos de negocio. Esta separación permite que la interfaz y los registros sobrevivan a una recarga sin red. La instalación ofrece un acceso desde el dispositivo sin exigir distribuir un paquete nativo distinto para cada plataforma.')
h2('Objetivo general')
P('Desarrollar y documentar una PWA instalable para registrar, consultar y dar seguimiento a incidencias de unidades, con evidencias fotográficas y ubicación opcionales, manteniendo la operación local cuando no existe conexión.')
h2('Objetivos específicos')
tbl(['Objetivo','Criterio verificable'],[['Instalabilidad','Manifiesto válido, iconos PNG de 192 y 512 px y ejecución sobre HTTPS.'],['Continuidad','Abrir la interfaz y consultar reportes tras desconectar y recargar.'],['Persistencia','Confirmar la transacción antes de informar que el reporte fue guardado.'],['Capacidades nativas','Capturar una foto y solicitar coordenadas desde acciones explícitas.'],['Calidad y entrega','Versionar el código, ejecutar pruebas y auditar el sitio publicado.']],[.29,.71])
P('El resultado es una bitácora funcional de almacenamiento local. Su alcance no incluye sincronización con la empresa, autenticación de operadores ni emisión de boletos. El sistema Laravel se conserva en el repositorio como base del proyecto, pero GitHub Pages publica únicamente la PWA estática.')

sect('2 Análisis del caso y requerimientos','s02')
P('El usuario principal es una persona del área de taller u operaciones que necesita documentar una situación asociada a una unidad. El flujo comienza con la captura de un título, descripción, unidad y prioridad; opcionalmente incorpora fotografía y ubicación. Después del guardado, el reporte puede consultarse, marcarse como atendido, reabrirse, eliminarse o exportarse.')
tbl(['ID','Requerimiento funcional','Resultado esperado'],[['RF01','Registrar una incidencia','Título de 3 a 100 caracteres y descripción de 5 a 2000, sin texto vacío.'],['RF02','Adjuntar evidencia','Foto como Blob JPEG; alternativa de selección de imagen de hasta 10 MB.'],['RF03','Obtener ubicación','Latitud, longitud y precisión; el permiso denegado no bloquea el guardado.'],['RF04','Consultar y filtrar','Listado por fecha, búsqueda de texto y filtro por estado.'],['RF05','Actualizar seguimiento','Estado Pendiente o Atendida persistente después de recargar.'],['RF06','Exportar bitácora','JSON con registros y fotos codificadas como data URL.'],['RF07','Consultar catálogo','Rutas académicas disponibles desde la última consulta local.']],[.12,.30,.58])
h2('Requerimientos no funcionales')
P('La interfaz debe adaptarse a escritorio y móvil, usar recursos propios para no depender de fuentes externas y manejar errores de permisos o almacenamiento. Las operaciones se ejecutan de forma asíncrona. La aplicación requiere HTTPS o localhost para las capacidades restringidas del navegador. No se solicita micrófono y no se envían coordenadas ni fotografías a un servidor.')
h2('Restricciones del análisis')
P('No se realizó un levantamiento operativo con datos reales de la empresa para esta copia. Las unidades y rutas se identifican como referencias académicas. El catálogo no representa tarifas, horarios ni disponibilidad comercial. La validación de cámara y geolocalización en CI utiliza medios simulados, por lo que no sustituye pruebas físicas en todos los dispositivos.')

sect('3 Arquitectura de la solución','s03')
diagram('architecture')
story.append(Paragraph('Figura 1. Componentes de la PWA y relaciones de acceso a datos. Elaboración propia a partir del código.',styles['CaptionReport']))
P('La PWA utiliza renderizado del lado del cliente (CSR). El archivo index.html contiene la estructura común y app.js genera las vistas según el fragmento de URL. El módulo db.js encapsula el acceso a IndexedDB. sw.js opera en un contexto separado y atiende solicitudes dentro de su ámbito. Las Web APIs se invocan desde la interfaz cuando el usuario pulsa un botón.')
tbl(['Capa','Responsabilidad','Archivos'],[['Presentación','Navegación, formularios, mensajes y diseño adaptable.','index.html, app.css'],['Aplicación','Validación, estado de la vista, captura y exportación.','app.js'],['Persistencia local','Abrir base, leer, escribir y eliminar mediante promesas.','db.js'],['Disponibilidad','Precaché, intercepción fetch y limpieza de versiones.','sw.js'],['Distribución','Servir archivos estáticos por HTTPS.','GitHub Pages y pwa-pages.yml']],[.23,.52,.25])
P('La base MySQL y las sesiones del sistema Laravel quedan fuera del ámbito del Service Worker de la bitácora. Esta decisión reduce el riesgo de guardar páginas privadas en la caché pública. También significa que registrar una incidencia en esta PWA no crea automáticamente una incidencia en el backend Laravel.')

sect('4 App Shell y renderizado responsivo','s04')
pic('01-inicio-escritorio.png','Figura 2. App Shell publicado: navegación, encabezado, resumen y contenido dinámico. Captura real del sitio HTTPS.',300)
P('El shell está formado por barra lateral, navegación principal, encabezado con estado de conexión, contenedor #view y pie de página. Esta estructura se conserva mientras cambian las vistas. La función render() lee los registros de IndexedDB y elige la función de vista mediante location.hash. El evento hashchange actualiza la vista y dirige el foco al contenido principal.')
code("""const page = window.location.hash.slice(1) || 'inicio';
({inicio: renderSummary, reportar: renderForm,
  incidencias: renderRecords, rutas: renderRoutes,
  ajustes: renderSettings}[page] || renderSummary)();""")
P('app.css aplica CSS Grid y Flexbox. En pantallas de hasta 700 px, la barra lateral deja de ser fija y la navegación se vuelve horizontal; el formulario pasa a una columna. Se incorporan etiquetas de campos, enlace para saltar al contenido, foco visible y mensajes con role="status". La prueba de ancho móvil comprueba que la página no exceda el viewport de 390 px.')

sect('5 Manifiesto e instalabilidad','s05')
P('El manifiesto describe la identidad y la forma de apertura de la aplicación. Se enlaza desde index.html mediante rel="manifest". Los valores relativos mantienen la instalación dentro de la ruta del proyecto tanto en localhost como en GitHub Pages (MDN Web Docs, s. f.-f).')
code(json.dumps({key:M[key] for key in ['id','name','short_name','start_url','scope','display','background_color','theme_color']},ensure_ascii=False,indent=2))
tbl(['Parámetro','Configuración y propósito'],[['id, start_url y scope','./ identifica y delimita la aplicación al directorio publicado.'],['display','standalone solicita apertura sin la interfaz habitual de pestañas.'],['lang y dir','es-MX y ltr expresan idioma y dirección del contenido.'],['background_color y theme_color','#f5f7f6 y #073d32 definen fondo inicial y color de integración.'],['Iconos','PNG 192x192 y 512x512 con purpose any; PNG 512x512 con purpose maskable.'],['shortcuts','Acceso directo a Nueva incidencia mediante ./#reportar.']],[.36,.64])
P('beforeinstallprompt se conserva para invocarlo al pulsar Instalar app; si no está disponible, se muestran instrucciones del menú del navegador. appinstalled oculta el botón. Los metadatos e iconos permiten que sistemas compatibles generen la pantalla de inicio nativa. La revisión del manifiesto no demuestra que la instalación o la splash hayan sido probadas físicamente en cada plataforma.')
P('En Safari de iPhone se utiliza la opción Compartir y Agregar a inicio. El archivo incluye apple-touch-icon y metadatos de aplicación web. La compatibilidad depende del navegador y del sistema operativo; no se presenta una splash simulada como evidencia de instalación real.')

sect('6 Ciclo de vida del Service Worker','s06')
diagram('lifecycle')
story.append(Paragraph('Figura 3. Registro, instalación, activación y atención de solicitudes. Elaboración propia.',styles['CaptionReport']))
P('El registro se realiza con navigator.serviceWorker.register("./sw.js", {scope:"./", updateViaCache:"none"}). Durante install, event.waitUntil prolonga el evento hasta guardar todo el shell y el catálogo inicial. Si esta etapa falla, el nuevo trabajador no termina de instalarse. Una primera visita conectada es necesaria para preparar los recursos.')
code("""self.addEventListener('install', event => {
  event.waitUntil((async () => {
    const cache = await caches.open(STATIC);
    await cache.addAll(SHELL.map(absolute));
    const data = await caches.open(DYNAMIC);
    await data.add(absolute('./catalogo.json'));
  })());
});""")
P('En activate se eliminan únicamente las cachés cuyo nombre comienza con eje-bitacora-actividad- y no corresponde a las versiones vigentes. clients.claim() permite controlar clientes existentes después de la activación. La limpieza está acotada para no borrar cachés de aplicaciones ajenas en el mismo origen.')
P('No se ejecuta skipWaiting de forma forzada. Una versión nueva espera a que se cierren las ventanas de la anterior, evitando reemplazar el shell durante la edición de un formulario. Para publicar cambios en recursos precargados debe incrementarse VERSION. Esta política se apoya en el ciclo documentado de Service Workers y se concreta en sw.js (MDN Web Docs, s. f.-e).')

sect('7 Estrategias de caché y flujo offline','s07')
tbl(['Recurso','Estrategia','Justificación'],[['HTML del shell','Cache First para navegación dentro del ámbito.','Permite volver a abrir las vistas CSR sin depender de una respuesta de red.'],['CSS, JS, manifiesto e iconos','Cache First sobre lista explícita.','Los recursos cambian con una versión del shell y deben estar disponibles juntos.'],['catalogo.json','Stale While Revalidate.','Responde con la copia existente y consulta actualizaciones en segundo plano.'],['Incidencias y fotografías','IndexedDB; no se guardan como respuestas HTTP.','Son datos estructurados y archivos del usuario, independientes de la caché de recursos.'],['Páginas privadas de Laravel','Fuera del ámbito.','Evita precargar sesiones o paneles del sistema de origen.']],[.26,.31,.43])
code("""const update = caches.open(DYNAMIC).then(async cache => {
  const response = await fetch(event.request);
  // El código valida tipo JSON y estructura antes de guardar.
  if (response.ok) { /* validar y actualizar cache */ }
  return response;
});
event.waitUntil(update.catch(() => undefined));
event.respondWith(caches.open(DYNAMIC).then(async cache =>
  (await cache.match(event.request)) || await update));""")
P('El fragmento es un extracto abreviado del flujo de catálogo; el archivo completo valida Content-Type y los arreglos rutas y unidades antes de reemplazar la copia. Al fallar una actualización se conserva el catálogo anterior. En app.js, la consulta tiene un tiempo límite de ocho segundos y recurre al catálogo guardado en IndexedDB si no obtiene una respuesta utilizable.')
P('El modo offline no convierte el navegador en un servidor ni asegura que existan recursos nunca descargados. La continuidad depende de una preparación inicial exitosa y de que el almacenamiento del sitio no haya sido eliminado. navigator.onLine muestra un estado orientativo; la lectura efectiva de IndexedDB y la recarga con red deshabilitada son la comprobación funcional principal.')

sect('8 Modelo de persistencia en IndexedDB','s08')
P('La base local se llama eje-golfo-pwa-actividad y utiliza la versión 1. El evento onupgradeneeded crea dos almacenes: incidencias, con keyPath id, y catalogos, con clave externa. Las operaciones usan transacciones asíncronas y no requieren conexión a MySQL ni a un servicio remoto. IndexedDB admite objetos estructurados y Blob, lo que permite conservar la fotografía junto con el registro (MDN Web Docs, s. f.-b).')
tbl(['Almacén','Clave','Contenido'],[['incidencias','id generado con crypto.randomUUID()','Reportes locales y evidencia opcional.'],['catalogos','referencia','Rutas, unidades y fecha de consulta del catálogo académico.']],[.22,.36,.42])
tbl(['Campo de incidencia','Tipo','Uso'],[['id','string UUID','Identificación sin depender de un contador del servidor.'],['titulo / descripcion','string','Descripción validada de la situación.'],['unidad / prioridad','string','Unidad seleccionada y nivel Normal, Alta o Baja.'],['estado','string','Pendiente o Atendida.'],['creada / actualizada','fecha ISO en string','Orden cronológico y actualización del seguimiento. actualizada se añade al cambiar estado.'],['ubicacion','objeto o null','lat, lng y precision en metros.'],['foto','Blob JPEG o null','Imagen comprimida antes del guardado.']],[.30,.25,.45])
P('No se definieron índices secundarios: el volumen de la actividad permite leer los registros con getAll, ordenar por creada y filtrar en memoria. Para una cartera extensa sería necesario paginar e incorporar índices de estado y fecha. La base está aislada por origen del sitio y perfil del navegador; no es una base compartida entre dispositivos.')

sect('9 Escritura lectura y recuperación de datos','s09')
diagram('write')
story.append(Paragraph('Figura 4. El guardado se confirma al finalizar la transacción, antes de actualizar la vista. Elaboración propia.',styles['CaptionReport']))
code("""const tx = db.transaction(store, 'readwrite');
if (key === undefined) tx.objectStore(store).put(value);
else tx.objectStore(store).put(value, key);
tx.oncomplete = () => resolve(value);
tx.onerror = () => reject(tx.error);
tx.onabort = () => reject(tx.error ||
  new Error('No se pudo guardar.'));""")
P('La promesa de escritura se resuelve en tx.oncomplete. El envío del formulario espera await write antes de navegar a Mis incidencias y mostrar la confirmación. getAll recupera el contenido y la interfaz lo ordena de forma descendente por fecha. Cambiar el estado reutiliza put sobre el mismo UUID; eliminar utiliza delete dentro de otra transacción readwrite.')
h2('Recuperación ante falta de red y errores')
P('Al reiniciar, la aplicación abre la base y reconstruye la vista desde los objetos persistentes. Si falla el almacenamiento, se informa el error sin presentar el registro como guardado. onblocked avisa que deben cerrarse otras ventanas; onversionchange libera la conexión. No se implementó una cola de sincronización remota: los reportes se conservan como datos locales.')
P('La exportación produce JSON y convierte cada Blob a data URL mediante FileReader. Los registros pueden conservarse fuera del navegador, aunque no existe una función de importación. Las URL temporales de imágenes se revocan al cambiar de vista para liberar memoria. Borrar los datos del sitio o usar un perfil distinto impide recuperar automáticamente la bitácora anterior.')

sect('10 Integración de la cámara','s10')
P('La cámara se solicita al pulsar Abrir cámara. Se comprueba la existencia de navigator.mediaDevices.getUserMedia y se pide exclusivamente video, con facingMode ideal environment para preferir la cámara trasera. Este valor expresa una preferencia, no una garantía sobre el dispositivo elegido. El permiso requiere un contexto seguro y autorización del navegador (MDN Web Docs, s. f.-c).')
code("""const nextStream = await navigator.mediaDevices.getUserMedia({
  video: {facingMode: {ideal: 'environment'}},
  audio: false
});
video.srcObject = nextStream;
video.hidden = false;
video.muted = true;
await video.play();""")
P('Al capturar se dibuja el fotograma en canvas y se genera un Blob JPEG con calidad 0.8. Para la cámara, el ancho se limita a 1280 px; para archivos seleccionados se limita la mayor dimensión a 1280 px. La selección alternativa acepta imágenes de hasta 10 MB. Después se muestra la vista previa y el Blob se incluye en la transacción del reporte.')
tbl(['Situación','Respuesta implementada'],[['Permiso denegado','Mensaje comprensible y alternativa para elegir imagen.'],['API no disponible o cámara inaccesible','Se conserva la opción de adjuntar archivo.'],['Video aún sin dimensiones','Se pide esperar antes de capturar.'],['Cambio de vista o cierre','Se detienen las pistas del MediaStream.'],['Error al iniciar la vista previa','Se liberan pistas y se ocultan controles de captura.']],[.40,.60])
P('Las pruebas automatizadas de esta ruta usan un MediaStream sintético de canvas. Se ejecutan la vista previa, captura, compresión y persistencia reales, pero no se valida un sensor físico. No se afirma una prueba de cámara real en teléfono a partir de esa simulación.')

sect('11 Geolocalización notificaciones y permisos','s11')
P('Obtener ubicación invoca getCurrentPosition una sola vez. Se almacenan latitud, longitud y precisión; no se realiza seguimiento continuo. La interfaz indica si existe ubicación adjunta y permite guardar sin ella cuando el usuario niega el permiso o no se obtiene posición (MDN Web Docs, s. f.-a).')
code("""navigator.geolocation.getCurrentPosition(
  position => {
    location = {
      lat: position.coords.latitude,
      lng: position.coords.longitude,
      precision: position.coords.accuracy
    };
  },
  error => { /* informar y permitir guardar sin ubicación */ },
  {enableHighAccuracy: true, timeout: 15000, maximumAge: 60000}
);""")
tbl(['Opción o permiso','Tratamiento'],[['enableHighAccuracy','Solicita mayor precisión; puede incrementar el tiempo o consumo del dispositivo.'],['timeout 15000','Limita la espera de la solicitud de posición a 15 segundos.'],['maximumAge 60000','Permite aceptar una posición disponible de hasta un minuto de antigüedad.'],['Permiso denegado','Se comunica el resultado y se mantiene habilitado el guardado.'],['Solicitud finalizada en otra vista','renderId evita actualizar controles de una pantalla que ya fue abandonada.']],[.36,.64])
h2('Notificación de guardado opcional')
P('En Aplicación se ofrece Notification.requestPermission. Si existe permiso granted y un Service Worker activo, showNotification confirma un guardado local. No se implementaron Push API, suscripciones ni servidor de mensajería. Una notificación local no demuestra recepción de mensajes desde la empresa (MDN Web Docs, s. f.-d).')
P('Cámara y ubicación se activan por botones separados y no se solicitan al abrir el sitio. Los registros no se transmiten automáticamente. La precisión depende del dispositivo y del entorno: disponer de la API no garantiza que se pueda obtener una posición nueva sin cobertura.')

sect('12 Configuración versionamiento y despliegue','s12')
diagram('deploy')
story.append(Paragraph('Figura 5. Pipeline de validación y publicación de la copia académica. Elaboración propia.',styles['CaptionReport']))
P('Se importó el repositorio de origen a patata-ni/eje-del-golfo-pwa-actividad, conservando el historial anterior. La adaptación se realizó en esta copia. El workflow original de Railway se retiró de main en la copia y se añadió pwa-pages.yml. La variable de ejemplo DB_DATABASE se cambió a ejegolfo_pwa_actividad para separar una posible ejecución local de Laravel.')
tbl(['Elemento','Configuración'],[['Publicación','https://patata-ni.github.io/eje-del-golfo-pwa-actividad/'],['Repositorio','https://github.com/patata-ni/eje-del-golfo-pwa-actividad'],['Contenido desplegado','Directorio public/pwa, sin PHP, MySQL ni credenciales.'],['Disparador','Push a main o workflow_dispatch.'],['Validaciones','node --check, validación PNG/manifest y suite Playwright.'],['Entrega','Artefacto de Pages y despliegue con permisos pages:write e id-token:write.']],[.27,.73])
P('GitHub Pages sirve la aplicación mediante HTTPS. En la revisión se verificó isSecureContext=true y un Service Worker activado en el ámbito del proyecto. La evidencia del reporte se produjo en una rama separada, sin modificar los recursos de la versión publicada. Los enlaces y los identificadores permiten distinguir una configuración declarada de una ejecución realmente comprobada.')

sect('13 Pruebas funcionales y trazabilidad','s13')
P('La suite tests/pwa/bitacora.spec.mjs se ejecuta en Chromium mediante Playwright. La nueva ejecución de evidencia volvió a comprobar los cuatro casos. Las pruebas esperan que el trabajador esté listo y que exista un controlador antes de deshabilitar la red. La recarga se realiza después de observar el guardado confirmado para no interrumpir una transacción pendiente.')
tbl(['Caso','Comprobación','Resultado'],[['P01 Persistencia offline','Crear sin red, recargar, marcar atendida, recargar y eliminar.','Aprobado'],['P02 Evidencia y posición','MediaStream sintético y coordenadas ficticias; captura, guardado y recuperación de foto.','Aprobado'],['P03 Permiso y exportación','Denegar ubicación, guardar, mostrar texto con HTML sin ejecutarlo y descargar JSON.','Aprobado'],['P04 App Shell móvil','390x844 px sin desbordamiento, manifiesto y consulta de rutas offline.','Aprobado']],[.24,.59,.17])
h2('Identificación de las ejecuciones')
P('Versión publicada revisada: <b>0e9d4f82a10614ccc4bf05f0f5e172393eba1fff</b>. La publicación inicial y su validación concluyeron correctamente en la ejecución 45752150265. La ejecución específica de evidencia es <b>46062408170</b>, en la rama evidencias-reporte-pwa. Su artefacto conserva capturas, JSON de estado, manifiesto, resultados de Lighthouse y reporte de pruebas.')
P('La simulación móvil valida tamaño de viewport y comportamiento del navegador, no un teléfono físico. La cobertura no incluye todos los navegadores, instalación real, splash en sistemas distintos ni una auditoría completa de seguridad. El resultado aprobado significa que se verificaron las aserciones descritas, no que la aplicación esté libre de cualquier defecto.')
h2('Correcciones documentadas')
P('Durante la preparación se añadió inicio explícito del video y liberación de pistas ante errores. El servidor de CI no pudo utilizar cámara física, por lo que se suministró un flujo sintético. También se corrigió la prueba que recargaba antes de confirmar el guardado y se evitó instalar fuentes opcionales que retrasaban el runner. Estos cambios se registraron en commits reales.')

sect('14 Evidencia de operación offline','s14')
pic('03-offline-escritorio.png','Figura 6. Consulta después de deshabilitar la red y recargar el sitio publicado. El reporte mostrado es ficticio y el indicador confirma modo local.',280)
P('El procedimiento de evidencia abrió el sitio HTTPS, esperó la activación del Service Worker, completó un reporte académico y confirmó su aparición. Después ejecutó context.setOffline(true), recargó y comprobó nuevamente el mismo título. La captura corresponde al estado posterior a esa recarga, por lo que no depende únicamente de una vista que permaneciera abierta en memoria.')
tbl(['Dato observado','Valor registrado'],[['Conectividad del contexto',str(S['online']).lower()],['Contexto seguro',str(S['secureContext']).lower()],['Estado del trabajador',S['worker']['state']],['Almacenes locales',', '.join(S['stores'])],['Registros recuperados',str(len(S['incidencias']))],['Momento de evidencia UTC',S['capturedAt']]],[.42,.58])
P('Cache Storage conserva el shell y el catálogo, mientras IndexedDB conserva el reporte. Son mecanismos distintos: borrar uno de ellos puede afectar una parte diferente de la experiencia. La evidencia se limita a la persistencia de este origen en el perfil de prueba; no demuestra transferencia de datos entre equipos.')

sect('15 Evidencia móvil y estado de almacenamiento','s15')
pic('04-offline-movil.png','Figura 7. Emulación móvil de 390 px de ancho con red deshabilitada y reporte recuperado. Es una prueba de navegador, no una fotografía de un teléfono.',425,maxw=235)
P('En el viewport móvil el menú se reorganiza en la parte superior y el contenido conserva su lectura en una columna. La captura mantiene el indicador de falta de conexión y el reporte ficticio. La comprobación programática registró overflow='+str(S['overflow']).lower()+', por lo que el ancho total no excedía el viewport en este estado.')
P('Las cachés encontradas fueron <b>'+escape(', '.join(S['caches']))+'</b>. El trabajador activo se sirvió desde el directorio de la PWA y controló su ámbito. El catálogo y las incidencias se recuperaron del almacenamiento preparado antes de la desconexión. El archivo estado-offline.json conserva estos valores para su comprobación independiente.')

sect('16 Auditoría Lighthouse del sitio publicado','s16')
pic('05-lighthouse.png','Figura 8. Reporte Lighthouse real de la URL publicada. La captura muestra los resultados de la ejecución de laboratorio.',290)
cats={'performance':'Rendimiento','accessibility':'Accesibilidad','best-practices':'Buenas prácticas','seo':'SEO'}
tbl(['Categoría','Puntuación /100','Lectura'],[[cats.get(k,k),str(v),'Requiere atender hallazgos' if v<90 else 'Resultado alto en esta ejecución'] for k,v in L['categories'].items()],[.37,.23,.40])
P('Herramienta: Lighthouse '+str(L['version'])+'. Perfil: '+str(L['formFactor'])+'. Fecha de captura UTC: '+L['fetchTime']+'. La auditoría se ejecutó sobre la URL pública con el perfil móvil y la simulación de rendimiento del informe. Es una medición de laboratorio; no representa una distribución de usuarios reales ni garantiza que la misma puntuación se repita en cualquier conexión (Google, s. f.).')
P('Lighthouse retiró la categoría PWA a partir de la versión 12. Por ello este documento no inventa una puntuación PWA. Se combinan las categorías disponibles con validación del manifiesto, comprobación del Service Worker, evidencia de IndexedDB y pruebas offline (GoogleChrome, 2024).')

sect('17 Análisis de métricas y hallazgos','s17')
definitions={'first-contentful-paint':'Primer contenido visible. Evalúa el inicio de la presentación.','largest-contentful-paint':'Mayor elemento visible. Relaciona carga con percepción del contenido principal.','speed-index':'Velocidad de progresión visual durante la carga.','total-blocking-time':'Tiempo de bloqueo por tareas largas; no equivale a una medición de INP de usuarios reales.','cumulative-layout-shift':'Desplazamientos inesperados del contenido durante la medición.'}
tbl(['Métrica','Resultado','Interpretación'],[[{'first-contentful-paint':'FCP','largest-contentful-paint':'LCP','speed-index':'Speed Index','total-blocking-time':'TBT','cumulative-layout-shift':'CLS'}[k],str(v['display']),definitions[k]] for k,v in L['metrics'].items()],[.18,.19,.63])
lcp=L['metrics']['largest-contentful-paint']['value']/1000;cls=L['metrics']['cumulative-layout-shift']['value']
P(f'El LCP obtenido fue de {lcp:.2f} s y el CLS de {cls:.3f}. Como referencia de experiencia web, Google propone LCP de hasta 2.5 s y CLS de hasta 0.1. En esta ejecución, el LCP '+('se ubicó dentro' if lcp<=2.5 else 'quedó fuera')+' de esa referencia y el CLS '+('se mantuvo dentro' if cls<=.1 else 'quedó fuera')+'. Estos valores no permiten afirmar cumplimiento de Core Web Vitals en campo: faltan datos de usuarios, percentiles e INP (Walton, 2024).')
findings=L.get('findings',[])
actions={'cumulative-layout-shift':'Reservar espacio para el contenido inicial y comparar la traza antes y después de cada render del contenedor #view.', 'layout-shifts':'Examinar los dos desplazamientos registrados y estabilizar las dimensiones de sus contenedores.', 'color-contrast':'Aumentar la diferencia de luminancia del texto y su fondo en los elementos señalados; validar cada combinación.', 'cache-insight':'Revisar cabeceras HTTP del hosting. La caché del Service Worker y la vida útil HTTP son mecanismos diferentes.', 'cls-culprits-insight':'Relacionar los cambios de geometría con la reconstrucción de la vista; confirmar la causa con la traza antes de modificar el diseño.'}
if findings:
    tbl(['Hallazgo del informe','Acción propuesta'],[[escape(f['title'])+((' ('+escape(str(f.get('display')))+')') if f.get('display') else ''),actions.get(f['id'],'Revisar los recursos señalados y repetir una medición comparable tras el ajuste.')] for f in findings[:5]],[.55,.45])
else:P('El resumen no registró auditorías con score inferior a 1. Esto no sustituye las revisiones manuales de accesibilidad ni una evaluación de seguridad independiente.')
nodes=FULL.get('audits',{}).get('color-contrast',{}).get('details',{}).get('items',[])
selectors=[item.get('node',{}).get('selector','') for item in nodes if item.get('node',{}).get('selector')]
if selectors:P('Los elementos concretos señalados por contraste incluyen: <b>'+escape('; '.join(selectors[:3]))+'</b>. La revisión debe concentrarse en esos selectores y volver a ejecutar el análisis después del cambio.')
P('Como hipótesis de mejora para CLS, conviene revisar la doble reconstrucción inicial de la vista al cargar el catálogo. El código permite esa secuencia, pero esta auditoría no demuestra por sí sola que sea la causa de los dos desplazamientos; debe confirmarse con la traza de rendimiento.')
P('La puntuación de rendimiento agrega métricas; los diagnósticos orientan mejoras, pero no deben confundirse con los componentes directos de la puntuación. La página inicial usa recursos pequeños y no incorpora bibliotecas visuales externas; esa decisión reduce dependencias, aunque no elimina la necesidad de revisar contraste, navegación por teclado, prioridades de carga y políticas del hosting (Chrome for Developers, s. f.).')

sect('18 Seguridad límites y mejoras previstas','s18')
P('La PWA conserva fotografías y coordenadas, por lo que el almacenamiento local debe tratarse como información de trabajo. Se evita solicitar permisos al iniciar, se utiliza HTTPS y se escapa el texto al generar HTML. La prueba con una cadena que contiene una etiqueta img confirma que se muestra como texto en lugar de crear ese elemento. Este caso no equivale a una auditoría exhaustiva de XSS.')
tbl(['Riesgo o límite','Tratamiento actual','Mejora priorizada'],[['Pérdida de datos del sitio','Exportación manual en JSON; aviso sobre almacenamiento local.','Añadir importación validada y respaldo autorizado.'],['Datos en equipo compartido','No se envían al servidor; no existe cifrado ni acceso por usuario.','Evaluar autenticación y política de retención antes de uso real.'],['No hay sincronización','El alcance se informa explícitamente.','Diseñar API autenticada, cola, idempotencia y resolución de conflictos.'],['Volumen creciente','getAll y filtrado en memoria.','Índices, paginación y límites de almacenamiento.'],['Actualizaciones del shell','Versionado manual y espera del trabajador nuevo.','Automatizar versión y notificación de actualización sin perder formularios.'],['Cobertura de dispositivos','Chromium y viewport móvil emulado.','Pruebas físicas en Android e iOS; instalación y permisos reales.']],[.25,.36,.39])
P('No se implementó cifrado de la base local, control de acceso multiusuario ni tratamiento empresarial de datos personales. Por ello se utilizan datos de demostración en las evidencias. La prioridad antes de llevarla a una operación real sería acordar quién registra, quién puede consultar, cuánto tiempo se conservan los datos y cómo se recuperan ante pérdida del dispositivo.')
P('El informe de Lighthouse se conserva como línea base. Las mejoras deben verificarse mediante una medición comparable y pruebas funcionales, sin eliminar el modo offline ni la accesibilidad para aumentar una cifra aislada.')

sect('19 Conclusiones y lecciones aprendidas','s19')
P('El desarrollo demostró que una bitácora puede continuar operando sin red cuando se separan correctamente el shell, las respuestas cacheadas y los datos del usuario. El resultado principal no es solamente abrir una página guardada: se verificaron creación, actualización, eliminación y recuperación de reportes después de recargar en modo offline. El manifiesto y la publicación HTTPS completan la base de instalabilidad, aunque la instalación física requiere comprobación específica por plataforma.')
P('Aprendimos que la confirmación del guardado debe corresponder a la finalización de una transacción. La prueba de evidencia falló cuando intentó recargar inmediatamente después del clic, antes de observar el guardado confirmado. Esperar el reporte persistente hizo que el caso comprobara el comportamiento previsto y evitó confundir una condición de carrera de la prueba con pérdida permanente de datos.')
P('La cámara también mostró la importancia de diferenciar un entorno de CI de un dispositivo real. Un video sintético permite comprobar captura, compresión y almacenamiento sin acceder a una cámara física. Su aprobación es evidencia del flujo de software, pero no de todos los sensores, permisos y restricciones de equipos finales. La documentación debe expresar esa diferencia con claridad.')
P('Otra lección fue tratar la caché como una política de actualización. Cache First favorece continuidad del shell; Stale While Revalidate permite responder rápido con el catálogo existente y buscar novedades. Ambas estrategias requieren límites, validación y renovación de versiones. Un catálogo antiguo puede seguir siendo útil como referencia, pero no debe presentarse como información comercial vigente.')
P('Concluimos que la PWA cumple el caso académico de registro local de incidencias con capacidades del dispositivo y evidencia verificable. Para ampliar su alcance se necesita una etapa de seguridad, respaldo y sincronización, además de pruebas en dispositivos físicos. La evolución debe conservar trazabilidad y reconocer los límites de los resultados de laboratorio.')

sect('20 Referencias bibliográficas','s20')
refs=[
('Chrome for Developers. (s. f.). <i>Lighthouse performance scoring.</i>','https://developer.chrome.com/docs/lighthouse/performance/performance-scoring'),
('Google. (s. f.). <i>Introduction to Lighthouse.</i> Chrome for Developers.','https://developer.chrome.com/docs/lighthouse/overview'),
('GoogleChrome. (2024, 22 de abril). <i>Release v12.0.0.</i> GitHub.','https://github.com/GoogleChrome/lighthouse/releases/tag/v12.0.0'),
('MDN Web Docs. (s. f.-a). <i>Geolocation: getCurrentPosition() method.</i>','https://developer.mozilla.org/en-US/docs/Web/API/Geolocation/getCurrentPosition'),
('MDN Web Docs. (s. f.-b). <i>IndexedDB API.</i>','https://developer.mozilla.org/en-US/docs/Web/API/IndexedDB_API'),
('MDN Web Docs. (s. f.-e). <i>Service Worker API.</i>','https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API'),
('MDN Web Docs. (s. f.-f). <i>Web application manifest.</i>','https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Manifest'),
('MDN Web Docs. (s. f.-c). <i>MediaDevices: getUserMedia() method.</i>','https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia'),
('MDN Web Docs. (s. f.-d). <i>Notifications API.</i>','https://developer.mozilla.org/en-US/docs/Web/API/Notifications_API'),
('Walton, P. (2024, 31 de octubre). <i>Web Vitals.</i> web.dev.','https://web.dev/articles/vitals')]
refs.sort(key=lambda item:item[0])
for name,url in refs: story.append(Paragraph(name+'<br/><link href="'+url+'" color="#075d43">'+url+'</link>',styles['RefReport']))
story.append(Paragraph('Fuentes técnicas consultadas el 27 de noviembre de 2026. El código, las capturas y las métricas de esta entrega constituyen evidencia propia del proyecto; las referencias sustentan los conceptos y las recomendaciones técnicas.',styles['CaptionReport']))

sect('Anexo A Reproducción y entrega','anexo')
h2('Enlaces y revisión de evidencia')
P('<b>Aplicación:</b> <link href="https://patata-ni.github.io/eje-del-golfo-pwa-actividad/" color="#075d43">https://patata-ni.github.io/eje-del-golfo-pwa-actividad/</link><br/><b>Repositorio:</b> <link href="https://github.com/patata-ni/eje-del-golfo-pwa-actividad" color="#075d43">https://github.com/patata-ni/eje-del-golfo-pwa-actividad</link><br/><b>Evidencia:</b> ejecución 46062408170, artefacto evidencias-reporte-pwa.')
code('python -m http.server 8765 --directory public/pwa\n# Abrir http://localhost:8765/\npython scripts/validate-pwa.py\nnpm ci\nnpx playwright install chromium\nnpx playwright test --config playwright-pwa.config.mjs')
h2('Procedimiento de comprobación')
P('1. Abrir la PWA conectada y esperar que indique disponibilidad offline.<br/>2. Registrar una incidencia ficticia y esperar la confirmación de guardado.<br/>3. Desactivar la red del contexto y recargar.<br/>4. Consultar y cambiar el estado del reporte; volver a recargar.<br/>5. Conectar y exportar el JSON. Para cámara y ubicación reales, autorizar cada permiso únicamente al usar su botón.<br/>6. Revisar manifiesto, cachés y base local en las herramientas del navegador.')
tbl(['Criterio de la rúbrica','Ubicación en el reporte'],[['Portada e índice','Portada institucional e índice con enlaces y paginación.'],['Introducción y justificación','Secciones 1 y 2.'],['App Shell y manifiesto','Secciones 3, 4 y 5.'],['Service Worker y caché','Secciones 6 y 7.'],['IndexedDB','Secciones 8 y 9.'],['Web APIs y permisos','Secciones 10 y 11.'],['Pruebas y Lighthouse','Secciones 13 a 17.'],['Conclusiones y bibliografía','Secciones 19 y 20.']],[.41,.59])
P('La fecha de elaboración del documento es 27 de noviembre de 2026. La entrega en tiempo y forma se acredita con el comprobante real de Classroom; este PDF no afirma que el envío haya ocurrido ni modifica la fecha límite establecida por el docente.')

pdf=OUT/'Reporte_Tecnico_PWA_Eje_del_Golfo_Tania_Gonzalez.pdf'
doc=ReportDoc(str(pdf),pagesize=(W,H),leftMargin=54,rightMargin=54,topMargin=57,bottomMargin=58,title='Reporte técnico de desarrollo de la PWA EJE del Golfo',author='Tania González Geronimo y Alondra Aimee García Gómez')
doc.multiBuild(story,onFirstPage=pageframe,onLaterPages=pageframe)

# Verificación y vistas de todas las páginas para revisión visual.
document=fitz.open(pdf);info=[];thumbs=[]
qa=OUT/'revision';qa.mkdir(exist_ok=True)
for i,page in enumerate(document):
    text=page.get_text();assert text.strip(),f'Blank page {i+1}'
    assert '\ufffd' not in text, f'Replacement glyph on page {i+1}'
    pix=page.get_pixmap(matrix=fitz.Matrix(1.1,1.1),alpha=False);path=qa/f'pagina-{i+1:02}.png';pix.save(path)
    im=PILImage.open(path).convert('RGB');im.thumbnail((268,380));thumb=PILImage.new('RGB',(290,412),'#dce4df');thumb.paste(im,((290-im.width)//2,8));ImageDraw.Draw(thumb).text((14,392),f'Pagina {i+1}',fill='#073d32');thumbs.append(thumb)
    info.append({'page':i+1,'chars':len(text),'title':text.splitlines()[0]})
for start in range(0,len(thumbs),6):
    sheet=PILImage.new('RGB',(870,824),'white')
    for j,im in enumerate(thumbs[start:start+6]):sheet.paste(im,((j%3)*290,(j//3)*412))
    sheet.save(OUT/f'revision-{start//6+1:02}.png')
(OUT/'verificacion.json').write_text(json.dumps({'pages':len(document),'sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'bytes':pdf.stat().st_size,'sections':sections,'pageInfo':info},ensure_ascii=False,indent=2),encoding='utf-8')
shutil.copy(E/'resumen-lighthouse.json',OUT/'resumen-lighthouse.json');shutil.copy(E/'estado-offline.json',OUT/'estado-offline.json')
# Transporte de revisión por archivos de texto cuando el host no dispone de red.
transport=OUT/'transporte';transport.mkdir(exist_ok=True)
for path in [pdf,*OUT.glob('revision-*.png')]:
    data=base64.b64encode(path.read_bytes()).decode()
    for n,start in enumerate(range(0,len(data),180000)):(transport/f'{path.name}.part{n:02}.b64').write_text(data[start:start+180000],encoding='ascii')
print('PDF_OK',json.dumps({'pages':len(document),'bytes':pdf.stat().st_size,'path':str(pdf)}))
