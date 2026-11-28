from pathlib import Path
import json,subprocess,base64,hashlib,shutil,re
import imageio_ffmpeg
from PIL import Image,ImageDraw,ImageFont

root=Path('video-trabajo');out=Path('video-final')
assert out.resolve().parent==Path.cwd().resolve()
if out.exists():shutil.rmtree(out)
out.mkdir();record=json.loads((root/'registro-demostracion.json').read_text())
ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
def ass_time(t):
 h=int(t//3600);m=int(t%3600//60);s=t%60
 return f'{h}:{m:02}:{s:05.2f}'
header='''[Script Info]
ScriptType: v4.00+
PlayResX: 1280
PlayResY: 960
WrapStyle: 0
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Caption,DejaVu Sans,22,&H00FFFFFF,&H00FFFFFF,&H00172A22,&H00172A22,0,0,0,0,100,100,0,0,1,0,0,2,36,36,20,1
Style: Label,DejaVu Sans,15,&H00FFFFFF,&H00FFFFFF,&H00172A22,&H00172A22,0,0,0,0,100,100,0,0,1,0,0,7,20,20,9,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
# The explanatory bands are outside the recorded 1280x800 app viewport.
events=[f'Dialogue: 0,0:00:00.00,{ass_time(record["duration"]+2)},Label,,0,0,0,,NAVEGADOR REAL · DEMOSTRACIÓN AUTOMATIZADA · HTTPS · DATOS DE PRUEBA']
for i,scene in enumerate(record['scenes']):
 end=record['scenes'][i+1]['time'] if i+1<len(record['scenes']) else record['duration']+2
 text='{\\b1}'+scene['title']+'{\\b0}\\N'+scene['text']
 events.append(f'Dialogue: 1,{ass_time(scene["time"])},{ass_time(end)},Caption,,0,0,0,,{text}')
subs=root/'subtitulos.ass';subs.write_text(header+'\n'.join(events),encoding='utf-8')
mp4=out/'Video_Funcionalidad_PWA_Eje_del_Golfo.mp4'
cmd=[ffmpeg,'-y','-i',str(root/'captura.webm'),'-vf',f'pad=1280:960:0:30:color=0x172a22,ass={subs.as_posix()}','-c:v','libx264','-preset','medium','-crf','28','-pix_fmt','yuv420p','-movflags','+faststart','-an',str(mp4)]
subprocess.run(cmd,check=True)
# Decode the finished video to ensure the deliverable has no corrupt frames.
subprocess.run([ffmpeg,'-v','error','-i',str(mp4),'-f','null','-'],check=True)
times=[record['duration']*fraction for fraction in [.05,.18,.30,.43,.57,.70,.83,.94]]
thumbs=[]
for i,t in enumerate(times):
 p=out/f'revision-frame-{i+1:02}.png'
 subprocess.run([ffmpeg,'-y','-ss',str(t),'-i',str(mp4),'-frames:v','1',str(p)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 im=Image.open(p).convert('RGB');im.thumbnail((640,450));thumbs.append(im)
for start in [0,4]:
 sheet=Image.new('RGB',(1280,900),'white')
 for j,im in enumerate(thumbs[start:start+4]):sheet.paste(im,((j%2)*640,(j//2)*450))
 sheet.save(out/f'revision-video-{start//4+1:02}.png')
manifest={'file':mp4.name,'bytes':mp4.stat().st_size,'sha256':hashlib.sha256(mp4.read_bytes()).hexdigest(),'durationSeconds':record['duration'],'resolution':'1280x960','audio':False,'realBrowser':True,'automated':True,'nativeInstallRecorded':False,'physicalCameraGPSRecorded':False,'runtimeErrors':record['pageErrors'],'checks':['Create incident and attach real image file','Disable context network and reload','Recover incident and photo offline','Create second incident offline','Update state and reload offline','Search and filter offline','Read cached catalog offline','Restore connectivity and export two incidents']}
(out/'verificacion-video.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
shutil.copy(root/'registro-demostracion.json',out/'registro-demostracion.json')
trans=out/'transporte';trans.mkdir()
for path in [mp4,*out.glob('revision-video-*.png')]:
 data=base64.b64encode(path.read_bytes()).decode()
 for n,pos in enumerate(range(0,len(data),240000)):(trans/f'{path.name}.part{n:03}.b64').write_text(data[pos:pos+240000],encoding='ascii')
print('VIDEO_OK',json.dumps(manifest))
