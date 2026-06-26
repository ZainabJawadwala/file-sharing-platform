async function log(msg){
  const el=document.getElementById('log');
  el.textContent += msg + '\n';
}

async function getUploadLink(url, filename, token){
  const params = new URLSearchParams({filename});
  const headers = {};
  if(token) headers['Authorization'] = token.startsWith('Bearer ')? token : ('Bearer '+token);
  const res = await fetch(url + '?' + params.toString(), {method: 'GET', headers});
  if(!res.ok) throw new Error('Upload link request failed: ' + res.status + ' ' + await res.text());
  return res.json();
}

async function uploadWithPost(form, uploadUrl, fields){
  const fd = new FormData();
  // append all returned fields first
  for(const [k,v] of Object.entries(fields)) fd.append(k, v);
  // append file (must use the same field name expected by S3, usually 'file' or 'key' from form)
  fd.append('file', form.file);
  // POST the multipart form to S3
  const r = await fetch(uploadUrl, {method: 'POST', body: fd});
  return r;
}

async function uploadWithPut(url, file){
  const r = await fetch(url, {method: 'PUT', body: file, headers: {'Content-Type': file.type || 'application/octet-stream'}});
  return r;
}

document.getElementById('uploadBtn').addEventListener('click', async ()=>{
  const token = document.getElementById('token').value.trim();
  const filename = document.getElementById('filename').value.trim();
  const fileInput = document.getElementById('file');
  const method = document.getElementById('method').value;

  document.getElementById('log').textContent = '';

  if(!filename){ await log('Please enter a filename.'); return; }
  if(!fileInput.files.length){ await log('Please choose a file.'); return; }
  const file = fileInput.files[0];

  try{
    await log('Requesting upload link...');
    if(method === 'post'){
      const data = await getUploadLink('/s3/presign', filename, token);
      await log('Got upload link. Uploading to S3 via form...');
      // data.form usually contains {url, fields}
      const uploadUrl = data.form.url || data.url || data.bucketUrl || data.bucket;
      const fields = data.form.fields || data.form || {};
      const res = await uploadWithPost({file}, data.form.url, fields);
      if(res.ok) await log('Upload succeeded (POST).'); else await log('Upload failed (POST): ' + res.status);
    } else {
      const data = await getUploadLink('/s3/presign_put', filename, token);
      await log('Got upload link (PUT). Uploading file directly...');
      const putUrl = data.put_url || data.putUrl || data.url;
      const res = await uploadWithPut(putUrl, file);
      if(res.ok) await log('Upload succeeded (PUT).'); else await log('Upload failed (PUT): ' + res.status);
    }
  }catch(err){
    await log('Error: ' + err.message);
  }
});