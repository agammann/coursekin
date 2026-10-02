'use strict';
const $ = s => document.querySelector(s);
const state = { token: '', course: null, busy: false, setup: {}, add: {} };
const icon = '<svg viewBox="0 0 30 36" aria-hidden="true"><path d="M6 2h13l7 8v22a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2Z"/><path d="M18 2v9h8"/></svg>';
const bookIcon = '<svg viewBox="0 0 40 36" aria-hidden="true"><path d="M20 7C16 3 8 3 3 5v27c6-2 12-1 17 3 5-4 11-5 17-3V5c-5-2-13-2-17 2Z"/><path d="M20 7v28"/></svg>';
function el(tag, cls, text) { const n=document.createElement(tag); if(cls)n.className=cls; if(text!==undefined)n.textContent=text; return n; }
function notify(message) { $('#toast').textContent=message; $('#toast').classList.remove('hidden'); clearTimeout(notify.timer); notify.timer=setTimeout(()=>$('#toast').classList.add('hidden'),11000); }
async function api(path, options={}) {
  const response=await fetch('/api/'+path,{...options,headers:{'Content-Type':'application/json','X-Coursekin-Token':state.token,...options.headers}});
  const data=await response.json(); if(!response.ok)throw new Error(data.error||'Could not complete this request.'); return data;
}
function documentFields(container, destination, prefix) {
  container.replaceChildren();
  for(const role of ['textbook','syllabus']) {
    const title=role[0].toUpperCase()+role.slice(1), wrap=el('div','document-field '+role);
    const label=el('label','field-label',title); label.htmlFor=prefix+'-'+role;
    const area=el('div','drop-area'); const graphic=el('span'); graphic.innerHTML=role==='textbook'?bookIcon:icon; area.append(graphic);
    const text=el('div'); text.append(el('span','drop-title','Drop your file here'),el('span','browse','or browse files'));
    const note=el('span','file-note','PDF, DOCX, TXT or MD · up to 30 MB');
    const file=el('input'); file.type='file'; file.id=label.htmlFor; file.accept='.pdf,.docx,.txt,.md'; file.setAttribute('aria-label',title+' file');
    area.append(text,note,file);
    const paste=el('textarea','paste-field hidden'); paste.placeholder='Paste your '+role+' here…'; paste.maxLength=8000000; paste.setAttribute('aria-label',title+' text');
    const toggle=el('button','paste-toggle','Paste text instead'); toggle.type='button';
    const data=destination[role]={file:null,text:'',mode:'file'};
    const selected = f => { if(!f)return; if(f.size>30*1024*1024){notify('Each file must be smaller than 30 MB.');file.value='';return;}if(!/\.(pdf|docx|txt|md)$/i.test(f.name)){notify('Please use PDF, DOCX, TXT or Markdown.');file.value='';return;} data.file=f;graphic.replaceChildren(el('span','book-mark','✓'));text.className='file-selected';text.textContent=f.name;note.textContent=(f.size>=1024*1024?(f.size/1024/1024).toFixed(1)+' MB':Math.max(1,Math.ceil(f.size/1024))+' KB')+' · Ready to import';};
    file.addEventListener('change',()=>selected(file.files[0]));
    area.addEventListener('dragover',e=>{e.preventDefault();area.classList.add('dragging');});
    area.addEventListener('dragleave',()=>area.classList.remove('dragging'));
    area.addEventListener('drop',e=>{e.preventDefault();area.classList.remove('dragging');selected(e.dataTransfer.files[0]);});
    paste.addEventListener('input',()=>data.text=paste.value);
    toggle.addEventListener('click',()=>{data.mode=data.mode==='file'?'text':'file';area.classList.toggle('hidden',data.mode==='text');paste.classList.toggle('hidden',data.mode==='file');toggle.textContent=data.mode==='text'?'Choose a file instead':'Paste text instead';if(data.mode==='text')paste.focus();});
    wrap.append(label,area,paste,toggle);container.append(wrap);
  }
}
async function documentsFrom(fields, requireBoth) {
  const docs=[];
  for(const role of ['textbook','syllabus']) {
    const d=fields[role];
    if(d.mode==='text'&&d.text.trim()) docs.push({role,name:role+'.txt',text:d.text.trim()});
    else if(d.mode==='file'&&d.file){const data=await new Promise((resolve,reject)=>{const reader=new FileReader();reader.onload=()=>resolve(reader.result.split(',')[1]);reader.onerror=()=>reject(new Error('Could not read '+d.file.name));reader.readAsDataURL(d.file);});docs.push({role,name:d.file.name,data});}
    else if(requireBoth)throw new Error('Add your '+role+' as a file or pasted text.');
  }
  if(!docs.length)throw new Error('Choose a file or paste some text first.');
  return docs;
}
async function refreshClasses(){const classes=await api('courses');$('#classes').replaceChildren();if(!classes.length)$('#classes').append(el('p','empty-classes','Your classes will appear here.'));for(const c of classes){const b=el('button','class-link'+(state.course?.id===c.id?' active':''),c.name);b.type='button';b.addEventListener('click',()=>openCourse(c.id).catch(e=>notify(e.message)));$('#classes').append(b);}}
function newClass(){if(state.busy)return notify('Wait for the current request to finish.');state.course=null;localStorage.removeItem('coursekin-class');$('#setup').classList.remove('hidden');$('#chat').classList.add('hidden');$('#class-form').reset();state.setup={};documentFields($('#setup-documents'),state.setup,'setup');refreshClasses().catch(e=>notify(e.message));$('#class-name').focus();}
async function openCourse(id){if(state.busy)return notify('Wait for the current request to finish.');const course=await api('courses/'+id);state.course=course;localStorage.setItem('coursekin-class',id);$('#setup').classList.add('hidden');$('#chat').classList.remove('hidden');$('#chat-title').textContent=course.name;$('#messages').replaceChildren();for(const m of course.messages)renderMessage(m);$('#chat-welcome').classList.toggle('hidden',course.messages.length>0);$('#question').value='';await refreshClasses();$('#messages').scrollTop=$('#messages').scrollHeight;$('#question').focus();}
function showSource(source){$('#source-title').textContent=source.name;$('#source-location').textContent=source.location;$('#source-text').textContent=source.text;$('#source-dialog').showModal();}
function renderMessage(m){const box=el('article','message '+m.role);box.append(el('div','message-role',m.role==='user'?'You':'Coursekin'));const content=el('div','message-content');const sources=new Map((m.sources||[]).map(s=>[s.number,s]));for(const part of m.text.split(/(\[\d+\])/g)){const n=/^\[(\d+)\]$/.exec(part);if(n&&sources.has(Number(n[1]))){const b=el('button','citation',n[1]);b.type='button';b.setAttribute('aria-label','Open source '+n[1]);b.addEventListener('click',()=>showSource(sources.get(Number(n[1]))));content.append(b);}else content.append(document.createTextNode(part));}box.append(content);if(sources.size){const row=el('div','sources');for(const s of sources.values()){const b=el('button','source-chip',s.number+' · '+s.name+' · '+s.location);b.type='button';b.addEventListener('click',()=>showSource(s));row.append(b);}box.append(row);}$('#messages').append(box);$('#messages').scrollTop=$('#messages').scrollHeight;return box;}
$('#class-form').addEventListener('submit',async e=>{e.preventDefault();if(state.busy)return;state.busy=true;$('#create-class').disabled=true;$('#import-status').textContent='Reading your materials. Large textbooks can take a moment…';try{const docs=await documentsFrom(state.setup,true);const c=await api('courses',{method:'POST',body:JSON.stringify({name:$('#class-name').value,documents:docs})});state.busy=false;await openCourse(c.id);}catch(err){notify(err.message);}finally{state.busy=false;$('#create-class').disabled=false;$('#import-status').textContent='Your class, ready when you are.';}});
$('#question-form').addEventListener('submit',async e=>{e.preventDefault();if(state.busy||!state.course)return;const question=$('#question').value.trim();if(!question)return;state.busy=true;$('#send').disabled=true;$('#question').disabled=true;$('#answer-status').textContent='Finding the right passages and thinking through your question…';$('#chat-welcome').classList.add('hidden');const user=renderMessage({role:'user',text:question});try{const result=await api('courses/'+state.course.id+'/chat',{method:'POST',body:JSON.stringify({question})});renderMessage(result);state.course.messages.push({role:'user',text:question},result);$('#question').value='';}catch(err){user.remove();notify(err.message);$('#chat-welcome').classList.toggle('hidden',state.course.messages.length>0);}finally{state.busy=false;$('#send').disabled=false;$('#question').disabled=false;$('#answer-status').textContent='Grounded in your materials. Check source references for important details.';$('#question').focus();}});
$('#question').addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey&&!e.isComposing){e.preventDefault();$('#question-form').requestSubmit();}});
document.querySelectorAll('.suggestions button').forEach(b=>b.addEventListener('click',()=>{$('#question').value=b.textContent;$('#question-form').requestSubmit();}));
$('#new-class').addEventListener('click',newClass);
$('#settings-button').addEventListener('click',()=>$('#settings-dialog').showModal());
function renderMaterials(){$('#material-list').replaceChildren();for(const d of state.course.documents){const row=el('div','material-row');row.append(el('strong','',d.name),el('span','',d.role+' · '+d.chunks+' searchable '+(d.chunks===1?'passage':'passages')));$('#material-list').append(row);}}
$('#materials-button').addEventListener('click',()=>{renderMaterials();state.add={};documentFields($('#add-documents'),state.add,'add');$('#materials-dialog').showModal();});
$('#add-form').addEventListener('submit',async e=>{e.preventDefault();if(state.busy)return notify('Wait for the current answer to finish.');state.busy=true;$('#add-submit').disabled=true;$('#add-status').textContent='Reading your new material…';try{const docs=await documentsFrom(state.add,false);state.course=await api('courses/'+state.course.id+'/documents',{method:'POST',body:JSON.stringify({documents:docs})});renderMaterials();state.add={};documentFields($('#add-documents'),state.add,'add');$('#add-status').textContent='Your new material is ready.';}catch(err){$('#add-status').textContent=err.message;}finally{state.busy=false;$('#add-submit').disabled=false;}});
$('#export').addEventListener('click',async()=>{try{const data=await api('courses/'+state.course.id+'/export');const url=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}));const a=el('a');a.href=url;a.download='coursekin-'+state.course.id+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}catch(e){notify(e.message);}});
$('#delete').addEventListener('click',()=>{if(state.busy)return notify('Wait for the current request to finish.');$('#delete-dialog').showModal();});
$('#cancel-delete').addEventListener('click',()=>$('#delete-dialog').close());
$('#confirm-delete').addEventListener('click',async()=>{if(state.busy)return;try{await api('courses/'+state.course.id,{method:'DELETE'});$('#delete-dialog').close();$('#materials-dialog').close();newClass();}catch(e){notify(e.message);}});
async function init(){documentFields($('#setup-documents'),state.setup,'setup');const response=await fetch('/api/session');if(!response.ok)throw new Error('Could not connect to the local Coursekin app.');const session=await response.json();state.token=session.token;$('#connection-status').textContent=session.configured?'Configured':'Key needed';$('#model-name').textContent=session.model;await refreshClasses();const id=localStorage.getItem('coursekin-class');if(id){try{await openCourse(id);}catch{localStorage.removeItem('coursekin-class');}}if(!session.configured)notify('Add your own OpenAI key with the setup command before asking questions. You can still import materials.');}
init().catch(e=>notify(e.message));
