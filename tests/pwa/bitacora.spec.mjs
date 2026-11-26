import {test,expect} from '@playwright/test';

async function ready(page){
  await page.goto('/');
  await expect(page.getByRole('heading',{name:'Cada recorrido cuenta.'})).toBeVisible();
  await page.evaluate(async()=>{await navigator.serviceWorker.ready;if(!navigator.serviceWorker.controller)await new Promise(resolve=>navigator.serviceWorker.addEventListener('controllerchange',resolve,{once:true}));});
}
async function report(page,title='Falla en luces delanteras'){
  await page.getByRole('link',{name:/Nueva incidencia/}).first().click();
  await page.getByLabel('Título de la incidencia').fill(title);
  await page.getByLabel('Descripción',{exact:true}).fill('Revisar las luces de la unidad antes de su salida.');
}
test('IndexedDB conserva altas, cambios y consultas después de recargar sin red',async({page,context})=>{
  await ready(page);
  await context.setOffline(true);
  await report(page);
  await page.getByRole('button',{name:'Guardar incidencia',exact:true}).click();
  await expect(page.getByRole('heading',{name:'Falla en luces delanteras'})).toBeVisible();
  await page.reload();
  await expect(page.getByRole('heading',{name:'Falla en luces delanteras'})).toBeVisible();
  await page.getByRole('button',{name:'Marcar atendida'}).click();
  await expect(page.getByRole('button',{name:'Reabrir'})).toBeVisible();
  await page.reload();
  await expect(page.getByRole('button',{name:'Reabrir'})).toBeVisible();
  page.once('dialog',dialog=>dialog.accept());
  await page.getByRole('button',{name:'Eliminar',exact:true}).click();
  await expect(page.getByRole('heading',{name:'Tu bitácora comienza aquí'})).toBeVisible();
});
test('cámara y geolocalización adjuntan evidencia local con permisos simulados',async({page,context})=>{
  page.on('console',message=>{if(message.type()==='warning'||message.type()==='error')console.log('Browser:',message.text());});
  // CI has no physical camera. Supply a real synthetic MediaStream through the
  // same getUserMedia entry point; capture, compression and IndexedDB stay real.
  await page.addInitScript(()=>{
    Object.defineProperty(navigator.mediaDevices,'getUserMedia',{value:async()=>{
      const canvas=document.createElement('canvas');canvas.width=640;canvas.height=480;
      const ctx=canvas.getContext('2d');
      const paint=()=>{ctx.fillStyle='#073d32';ctx.fillRect(0,0,640,480);ctx.fillStyle='#fff';ctx.font='24px sans-serif';ctx.fillText('Evidencia de prueba',40,80);};
      paint();const stream=canvas.captureStream(10);const timer=setInterval(paint,100);
      stream.getVideoTracks()[0].addEventListener('ended',()=>clearInterval(timer));
      return stream;
    }});
  });
  await context.grantPermissions(['camera','geolocation']);
  await context.setGeolocation({latitude:20.533,longitude:-97.46,accuracy:25});
  await ready(page); await report(page,'Prueba de evidencia');
  await page.getByRole('button',{name:'Obtener ubicación',exact:true}).click();
  await expect(page.locator('#location-status')).toContainText('20.53300');
  await page.getByRole('button',{name:'Abrir cámara',exact:true}).click();
  await expect(page.locator('video')).toBeVisible();
  await expect.poll(()=>page.locator('video').evaluate(video=>video.videoWidth),{timeout:15000}).toBeGreaterThan(0);
  await page.getByRole('button',{name:'Capturar',exact:true}).click();
  await expect(page.getByAltText('Vista previa de la evidencia')).toBeVisible();
  await page.getByRole('button',{name:'Guardar incidencia',exact:true}).click();
  await expect(page.getByRole('heading',{name:'Prueba de evidencia',exact:true})).toBeVisible();
  await expect(page.getByAltText('Evidencia de la incidencia')).toBeVisible();
  await page.reload();
  await expect(page.getByAltText('Evidencia de la incidencia')).toBeVisible();
  await expect(page.locator('#records')).toContainText('20.53300');
});
test('permiso denegado permite guardar, exportar y mostrar texto sin ejecutar HTML',async({page,context})=>{
  await context.grantPermissions([]);
  await ready(page);await report(page,'<img src=x onerror=alert(1)>');
  await page.getByRole('button',{name:'Obtener ubicación',exact:true}).click();
  await expect(page.locator('#location-status')).toContainText('Permiso denegado');
  await page.getByRole('button',{name:'Guardar incidencia',exact:true}).click();
  await expect(page.getByRole('heading',{name:'<img src=x onerror=alert(1)>',exact:true})).toBeVisible();
  expect(await page.locator('#records img').count()).toBe(0);
  const download=page.waitForEvent('download');
  await page.getByRole('button',{name:'Exportar bitácora'}).click();
  expect((await download).suggestedFilename()).toBe('eje-golfo-bitacora.json');
});
test('App Shell móvil, catálogo offline y manifiesto instalable',async({page,context})=>{
  await page.setViewportSize({width:390,height:844});await ready(page);
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  const manifest=await (await page.request.get('/manifest.json')).json();
  expect(manifest.display).toBe('standalone');
  expect(manifest.icons.map(icon=>icon.sizes)).toEqual(expect.arrayContaining(['192x192','512x512']));
  await context.setOffline(true);
  await page.getByRole('link',{name:/Rutas de referencia/}).click();
  await expect(page.getByRole('heading',{name:'Poza Rica → Martínez de la Torre',exact:true})).toBeVisible();
});
