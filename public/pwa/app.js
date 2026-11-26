import {database, read, readAll, write, remove} from './db.js';
const $ = selector => document.querySelector(selector);
const escape = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const date = value => new Date(value).toLocaleString('es-MX', {dateStyle:'medium',timeStyle:'short'});
let catalog = {rutas:[],unidades:['Otra unidad']};
let records = [], stream, photo, location, installPrompt, reg, toastTimer, renderId = 0;
let urls = [];
function toast(message) { clearTimeout(toastTimer); $('#toast').textContent = message; $('#toast').hidden = false; toastTimer = setTimeout(() => $('#toast').hidden = true, 6500); }
function failure(error) { console.error(error); toast('No se pudo completar la acción. Revisa el almacenamiento y vuelve a intentarlo.'); }
function stopCamera() { stream?.getTracks().forEach(track => track.stop()); stream = undefined; }
function heading(title, text, action = '') { return `<div class="heading"><div><p class="eyebrow">EJE DEL GOLFO / OPERACIONES</p><h1>${title}</h1><p class="subtitle">${text}</p></div>${action}</div>`; }
function thumbnail(blob) { const url = URL.createObjectURL(blob); urls.push(url); return url; }
function cards(items) {
  if (!items.length) return '<div class="card empty"><div class="empty-icon" aria-hidden="true">▤</div><h2>Tu bitácora comienza aquí</h2><p>Las incidencias que registres aparecerán en este espacio.</p><a class="button" href="#reportar">Crear una incidencia</a></div>';
  return `<div class="list">${items.map(item => `<article class="card incident"><div><span class="badge ${item.prioridad === 'Alta' ? 'offline' : ''}">${escape(item.prioridad)} · ${escape(item.estado)}</span><h3>${escape(item.titulo)}</h3><div class="incident-meta">${escape(item.unidad)} · ${date(item.creada)}</div><p>${escape(item.descripcion)}</p><div class="incident-meta">${item.ubicacion ? `Ubicación: ${Number(item.ubicacion.lat).toFixed(5)}, ${Number(item.ubicacion.lng).toFixed(5)} · precisión ±${Math.round(item.ubicacion.precision)} m` : 'Sin ubicación adjunta'}</div><div class="actions"><button class="secondary" data-toggle="${escape(item.id)}">${item.estado === 'Pendiente' ? 'Marcar atendida' : 'Reabrir'}</button><button class="danger" data-delete="${escape(item.id)}">Eliminar</button></div></div>${item.foto ? `<a href="${thumbnail(item.foto)}" target="_blank" rel="noopener" aria-label="Ver evidencia fotográfica"><img src="${urls[urls.length-1]}" alt="Evidencia de la incidencia"></a>` : ''}</article>`).join('')}</div>`;
}
function bindCards() {
  document.querySelectorAll('[data-toggle]').forEach(button => button.onclick = async () => {
    button.disabled = true;
    try { const item = await read('incidencias', button.dataset.toggle); item.estado = item.estado === 'Pendiente' ? 'Atendida' : 'Pendiente'; item.actualizada = new Date().toISOString(); await write('incidencias', item); await render(); toast('Estado actualizado en este dispositivo.'); } catch(error) { failure(error); button.disabled = false; }
  });
  document.querySelectorAll('[data-delete]').forEach(button => button.onclick = async () => {
    if (!confirm('¿Eliminar esta incidencia y su evidencia de este dispositivo?')) return;
    try { await remove('incidencias', button.dataset.delete); await render(); toast('Incidencia eliminada.'); } catch(error) { failure(error); }
  });
}
function renderSummary() {
  const pending = records.filter(item => item.estado === 'Pendiente').length;
  $('#view').innerHTML = heading('Cada recorrido cuenta.', 'Todo listo para dar seguimiento a tus incidencias.', '<a class="button" href="#reportar">＋ Nueva incidencia</a>') +
    `<section class="hero"><div><p class="eyebrow" style="color:#b9d69c">EN RUTA, CON O SIN CONEXIÓN</p><h2>Una bitácora que sigue<br>tu ritmo de trabajo.</h2><p>Documenta una falla, añade una fotografía y guarda su ubicación. Tu información estará disponible cuando la necesites.</p><a class="button" href="#reportar">Registrar una incidencia ↗</a></div><svg class="hero-art" viewBox="0 0 160 180" fill="none" stroke="#c7dfb6" stroke-width="3" aria-hidden="true"><rect x="28" y="18" width="104" height="142" rx="20"/><path d="M55 35h50M40 55h80v52H40zM40 128h18m44 0h18M53 160v9m54-9v9M40 115h80"/><circle cx="51" cy="144" r="5"/><circle cx="109" cy="144" r="5"/></svg></section>` +
    `<section class="metrics" aria-label="Resumen de incidencias"><div class="metric"><span>Incidencias registradas</span><strong>${records.length}</strong><small>En este dispositivo</small></div><div class="metric"><span>Por atender</span><strong>${pending}</strong><small>Seguimiento pendiente</small></div><div class="metric"><span>Atendidas</span><strong>${records.length-pending}</strong><small>Seguimiento completado</small></div></section><div class="section-head"><h2>Actividad reciente</h2><a class="text-link" href="#incidencias">Ver toda la bitácora →</a></div>` + cards(records.slice(0,3));
  bindCards();
}
function renderForm() {
  photo = undefined; location = undefined;
  $('#view').innerHTML = heading('Nueva incidencia', 'Documenta lo que sucede. Puedes guardar el reporte sin conexión.') + `<form id="report-form"><div class="grid"><section class="card"><h2>Información del reporte</h2><div class="form-grid"><div class="field"><label for="unit">Unidad</label><select id="unit" required>${catalog.unidades.map(unit=>`<option>${escape(unit)}</option>`).join('')}</select></div><div class="field"><label for="priority">Prioridad</label><select id="priority"><option>Normal</option><option>Alta</option><option>Baja</option></select></div></div><div class="field"><label for="title">Título de la incidencia</label><input id="title" required minlength="3" maxlength="100" placeholder="Ej. Revisión de luces delanteras"></div><div class="field"><label for="description">Descripción</label><textarea id="description" required minlength="5" maxlength="2000" placeholder="Describe la falla o la situación que observaste…"></textarea></div><div class="notice">El reporte se guarda en este navegador. Puedes exportarlo desde Mis incidencias para compartirlo con tu equipo.</div><div class="actions"><button id="save-report" type="submit">Guardar incidencia</button><a class="button secondary" href="#incidencias">Cancelar</a></div></section><aside><section class="card field"><h2>Evidencia fotográfica</h2><p class="hint">Activa la cámara o selecciona una imagen. La fotografía se guarda junto con el reporte.</p><video id="camera" autoplay playsinline muted hidden></video><img id="photo-preview" class="preview" alt="Vista previa de la evidencia" hidden><div class="actions field"><button class="secondary" id="open-camera" type="button">Abrir cámara</button><button id="capture" type="button" hidden>Capturar</button><button id="close-camera" class="secondary" type="button" hidden>Cerrar cámara</button><button id="remove-photo" class="secondary" type="button" hidden>Quitar foto</button></div><label for="photo-file">O elegir una imagen (máx. 10 MB)</label><input id="photo-file" type="file" accept="image/*" capture="environment"></section><section class="card"><h2>Ubicación del incidente</h2><p class="hint">Se solicita únicamente al pulsar el botón. También puedes guardar sin ubicación.</p><button class="secondary" id="locate" type="button">Obtener ubicación</button><p id="location-status" role="status">Sin ubicación adjunta.</p></section></aside></div></form>`;
  $('#open-camera').onclick = async () => {
    if (!navigator.mediaDevices?.getUserMedia) { toast('Este navegador no permite acceder a la cámara. Usa Elegir una imagen.'); return; }
    $('#open-camera').disabled = true;
    try {
      const activeRender = renderId;
      const nextStream = await navigator.mediaDevices.getUserMedia({video:{facingMode:{ideal:'environment'}},audio:false});
      if (activeRender !== renderId) { nextStream.getTracks().forEach(track => track.stop()); return; }
      stopCamera(); stream = nextStream; const video = $('#camera'); video.srcObject = stream; video.hidden = false; video.muted = true; $('#capture').hidden = false; $('#close-camera').hidden = false;
      await video.play();
    } catch(error) { console.warn('Camera unavailable:', error.name, error.message); toast(error.name === 'NotAllowedError' ? 'Permiso de cámara denegado. Puedes elegir una imagen.' : 'No se pudo abrir la cámara. Puedes elegir una imagen.'); }
    finally { if ($('#open-camera')) $('#open-camera').disabled = false; }
  };
  $('#close-camera').onclick = () => { stopCamera(); $('#camera').hidden = true; $('#capture').hidden = true; $('#close-camera').hidden = true; };
  $('#capture').onclick = async () => {
    const video = $('#camera');
    if (!video.videoWidth) return toast('Espera a que la cámara esté lista.');
    const canvas = document.createElement('canvas'); const ratio = Math.min(1,1280/video.videoWidth);
    canvas.width = Math.round(video.videoWidth*ratio); canvas.height = Math.round(video.videoHeight*ratio); canvas.getContext('2d').drawImage(video,0,0,canvas.width,canvas.height);
    const activeRender = renderId; const blob = await new Promise(resolve=>canvas.toBlob(resolve,'image/jpeg',.8));
    if (activeRender !== renderId || !blob) return;
    showPhoto(blob); $('#close-camera').click();
  };
  $('#photo-file').onchange = async event => {
    const file = event.target.files[0]; if (!file) return;
    if (!file.type.startsWith('image/') || file.size > 10*1024*1024) { toast('Selecciona una imagen de hasta 10 MB.'); event.target.value = ''; return; }
    const activeRender = renderId;
    try {
      const bitmap = await createImageBitmap(file); const canvas = document.createElement('canvas'); const ratio = Math.min(1,1280/Math.max(bitmap.width,bitmap.height));
      canvas.width = Math.round(bitmap.width*ratio); canvas.height = Math.round(bitmap.height*ratio); canvas.getContext('2d').drawImage(bitmap,0,0,canvas.width,canvas.height); bitmap.close();
      const blob = await new Promise(resolve=>canvas.toBlob(resolve,'image/jpeg',.8));
      if (activeRender === renderId && blob) showPhoto(blob);
    } catch { toast('No se pudo leer la imagen. Prueba con JPG o PNG.'); }
  };
  $('#remove-photo').onclick = () => { photo = undefined; $('#photo-preview').hidden = true; $('#remove-photo').hidden = true; $('#photo-file').value = ''; };
  $('#locate').onclick = () => {
    if (!navigator.geolocation) return toast('Este navegador no dispone de geolocalización.');
    const activeRender = renderId; $('#locate').disabled = true; $('#location-status').textContent = 'Obteniendo ubicación…';
    navigator.geolocation.getCurrentPosition(position => {
      if (activeRender !== renderId) return;
      location = {lat:position.coords.latitude,lng:position.coords.longitude,precision:position.coords.accuracy};
      $('#location-status').textContent = `${location.lat.toFixed(5)}, ${location.lng.toFixed(5)} · precisión ±${Math.round(location.precision)} m`; $('#locate').disabled = false;
    }, error => { if (activeRender !== renderId) return; $('#location-status').textContent = error.code === 1 ? 'Permiso denegado. Puedes guardar sin ubicación.' : 'Ubicación no disponible. Puedes guardar sin ubicación o reintentar.'; $('#locate').disabled = false; }, {enableHighAccuracy:true,timeout:15000,maximumAge:60000});
  };
  $('#report-form').onsubmit = async event => {
    event.preventDefault(); const title = $('#title').value.trim(), description = $('#description').value.trim();
    if (title.length < 3 || description.length < 5) return toast('Escribe un título de al menos 3 caracteres y una descripción de al menos 5.');
    $('#save-report').disabled = true;
    try {
      await write('incidencias', {id:crypto.randomUUID(),titulo:title,descripcion:description,unidad:$('#unit').value,prioridad:$('#priority').value,estado:'Pendiente',creada:new Date().toISOString(),ubicacion:location || null,foto:photo || null});
      stopCamera(); window.location.hash = 'incidencias'; toast('Incidencia guardada en este dispositivo.');
      if ('Notification' in window && Notification.permission === 'granted' && reg?.active) reg.showNotification('EJE del Golfo', {body:'Tu incidencia se guardó en la bitácora local.',icon:'./icons/icon-192.png'}).catch(()=>{});
    } catch(error) { failure(error); if ($('#save-report')) $('#save-report').disabled = false; }
  };
}
function showPhoto(blob) { photo = blob; $('#photo-preview').src = thumbnail(blob); $('#photo-preview').hidden = false; $('#remove-photo').hidden = false; }
function renderRecords() {
  $('#view').innerHTML = heading('Mis incidencias', 'Consulta y actualiza los reportes guardados en este dispositivo.', '<button class="secondary" id="export">↓ Exportar bitácora</button>') + '<div class="toolbar"><input id="search" type="search" aria-label="Buscar incidencias" placeholder="Buscar por título, descripción o unidad…"><select id="status" aria-label="Filtrar estado"><option value="">Todos los estados</option><option>Pendiente</option><option>Atendida</option></select></div><div id="records"></div>';
  const filter = () => { const term = $('#search').value.toLocaleLowerCase('es'); const state = $('#status').value; urls.forEach(URL.revokeObjectURL); urls=[]; $('#records').innerHTML = cards(records.filter(item=>(!state || item.estado===state) && `${item.titulo} ${item.descripcion} ${item.unidad}`.toLocaleLowerCase('es').includes(term))); bindCards(); };
  filter(); $('#search').oninput = filter; $('#status').onchange = filter;
  $('#export').onclick = async () => {
    if (!records.length) return toast('Aún no hay incidencias para exportar.');
    const button = $('#export'); button.disabled = true;
    try {
      const exported = await Promise.all(records.map(async item => ({...item,foto:item.foto ? await new Promise((resolve,reject)=>{const reader=new FileReader();reader.onload=()=>resolve(reader.result);reader.onerror=reject;reader.readAsDataURL(item.foto);}) : null})));
      const blob=new Blob([JSON.stringify({aplicacion:'EJE del Golfo · Bitácora académica',exportada:new Date().toISOString(),incidencias:exported},null,2)],{type:'application/json'});
      const url=URL.createObjectURL(blob); const link=document.createElement('a');link.href=url;link.download='eje-golfo-bitacora.json';document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),10000);toast('Bitácora exportada con fotografías y ubicaciones.');
    } catch(error) { failure(error); } finally { button.disabled = false; }
  };
}
function renderRoutes() {
  $('#view').innerHTML = heading('Rutas de referencia', 'Un punto de partida para identificar el recorrido de una unidad.', '<button class="secondary" id="refresh">Actualizar catálogo</button>') + '<div class="notice">Catálogo académico basado en el corredor del proyecto. No representa horarios, tarifas ni disponibilidad comercial. La última consulta se conserva sin conexión.</div>' + `<div class="list">${catalog.rutas.map(route=>`<article class="card route-card"><div class="route-icon" aria-hidden="true">↗</div><div><h3>${escape(route.origen)} → ${escape(route.destino)}</h3><p>${escape(route.detalle)}</p></div><span class="badge">${escape(route.id)}</span></article>`).join('') || '<p>No hay un catálogo disponible. Conéctate una vez para descargarlo.</p>'}</div><p class="hint">Última consulta: ${catalog.consultado ? date(catalog.consultado) : 'pendiente'}. Las actualizaciones recibidas en segundo plano estarán disponibles en la próxima consulta.</p>`;
  $('#refresh').onclick = async () => { if(!navigator.onLine) return toast('Sin conexión. Se muestra el último catálogo guardado.'); await loadCatalog(); await render(); toast('Catálogo consultado.'); };
}
function renderSettings() {
  $('#view').innerHTML = heading('Tu aplicación', 'Instalación, permisos y disponibilidad sin conexión.') + `<div class="settings"><section class="card"><h2>Instala EJE Bitácora</h2><p>Ábrela desde tu pantalla de inicio como una aplicación.</p><button id="install-settings">Instalar aplicación</button><p class="hint">En iPhone o iPad: Safari → Compartir → Agregar a inicio. En Android y escritorio: usa Instalar aplicación en el menú del navegador si el botón no está disponible.</p></section><section class="card"><h2>Disponibilidad y permisos</h2><p id="worker-status">${reg?.active ? 'La aplicación está preparada para uso sin conexión.' : 'Preparando almacenamiento sin conexión. Mantén la aplicación abierta unos segundos.'}</p><p>La cámara y la ubicación se solicitan desde Nueva incidencia, solo al pulsar sus botones.</p><button id="notifications" class="secondary">Activar notificación de guardado</button><p class="hint">Notificación local opcional; no es un servicio de notificaciones push.</p></section><section class="card"><h2>Sobre tus datos</h2><p>Las incidencias, fotos y ubicaciones permanecen en este navegador. No se envían a la empresa ni se sincronizan con el sistema Laravel. Borrar los datos del sitio elimina la bitácora. Exporta los registros que quieras conservar.</p><p class="hint">Copia independiente para la actividad PWA. Versión 1.0 · Tania Gonzalez y Alondra Aimee Garcia Gomez.</p></section></div>`;
  $('#install-settings').onclick = install;
  $('#notifications').onclick = async () => {
    if (!('Notification' in window)) return toast('Notificaciones no disponibles en este navegador.');
    try { const permission = await Notification.requestPermission(); toast(permission === 'granted' ? 'Notificación local de guardado activada.' : 'Las notificaciones están desactivadas. Puedes guardar incidencias.'); } catch { toast('No fue posible activar las notificaciones.'); }
  };
}
async function render() {
  const current = ++renderId;
  stopCamera(); urls.forEach(URL.revokeObjectURL); urls=[];
  try {
    records = (await readAll('incidencias')).sort((a,b)=>b.creada.localeCompare(a.creada));
    if (current !== renderId) return;
    const page = window.location.hash.slice(1) || 'inicio';
    document.querySelectorAll('[data-nav]').forEach(link => { link.classList.toggle('active',link.dataset.nav===page); if(link.dataset.nav===page)link.setAttribute('aria-current','page');else link.removeAttribute('aria-current'); });
    ({inicio:renderSummary,reportar:renderForm,incidencias:renderRecords,rutas:renderRoutes,ajustes:renderSettings}[page] || renderSummary)();
  } catch(error) { $('#view').innerHTML='<h1>No se pudo abrir la bitácora</h1><p>El navegador no permite acceder al almacenamiento local. Revisa los permisos del sitio y vuelve a abrir la aplicación.</p>'; failure(error); }
}
async function loadCatalog() {
  try {
    const response = await fetch('./catalogo.json', {signal:AbortSignal.timeout(8000)});
    if (!response.ok) throw new Error('Catálogo no disponible');
    const data = await response.json();
    if (!Array.isArray(data.rutas) || !Array.isArray(data.unidades)) throw new Error('Catálogo no válido');
    catalog = {...data,consultado:new Date().toISOString()}; await write('catalogos',catalog,'referencia');
  } catch { catalog = await read('catalogos','referencia') || catalog; }
}
function connection() { $('#connection').textContent=navigator.onLine?'Con conexión':'Sin conexión · modo local'; $('#connection').classList.toggle('offline',!navigator.onLine); }
async function install() {
  if (!installPrompt) return toast('Usa el menú del navegador para instalar. En iPhone: Compartir → Agregar a inicio.');
  try { await installPrompt.prompt(); const choice=await installPrompt.userChoice; toast(choice.outcome==='accepted'?'Instalación solicitada al navegador.':'Puedes instalar la aplicación más tarde.'); installPrompt=undefined; $('#install').hidden=true; } catch { toast('Usa el menú del navegador para instalar.'); }
}
window.addEventListener('beforeinstallprompt', event=>{event.preventDefault();installPrompt=event;$('#install').hidden=false;});
window.addEventListener('appinstalled',()=>{installPrompt=undefined;$('#install').hidden=true;toast('Aplicación instalada.');});
$('#install').onclick=install;
window.addEventListener('online',()=>{connection();loadCatalog().catch(failure);});
window.addEventListener('offline',connection);
window.addEventListener('hashchange',()=>{render();$('#main').focus();});
window.addEventListener('pagehide',stopCamera);
document.addEventListener('visibilitychange',()=>{if(document.hidden)stopCamera();});
connection();
try {
  await database();
  catalog=await read('catalogos','referencia') || catalog;
  await render();
  await loadCatalog();
  if ((window.location.hash.slice(1)||'inicio') !== 'reportar') await render();
} catch(error) { failure(error); }
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('./sw.js',{scope:'./',updateViaCache:'none'}).then(registration=>{
    reg=registration;
    registration.addEventListener('updatefound',()=>{const worker=registration.installing;worker?.addEventListener('statechange',()=>{if(worker.state==='installed')toast(navigator.serviceWorker.controller?'Actualización lista. Cierra todas las ventanas de la app para aplicarla.':'Aplicación preparada para uso sin conexión.');});});
    navigator.serviceWorker.ready.then(()=>{if($('#worker-status'))$('#worker-status').textContent='La aplicación está preparada para uso sin conexión.';});
  }).catch(()=>toast('No se pudo preparar el modo sin conexión. Abre la aplicación mediante HTTPS o localhost.'));
}
