import pathlib, zipfile, json
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'examples'
out=ROOT/'web/outputs/fixtures';out.mkdir(parents=True,exist_ok=True)
text=(source/'biology-textbook.txt').read_text()
paras=''.join('<w:p><w:r><w:t>'+p+'</w:t></w:r></w:p>' for p in text.splitlines() if p)
with zipfile.ZipFile(out/'practice-textbook.docx','w',zipfile.ZIP_DEFLATED) as z:
 z.writestr('[Content_Types].xml','<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>')
 z.writestr('word/document.xml','<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>'+paras+'</w:body></w:document>')
lines=['Biology 101 practice syllabus','Grading: quizzes 20 percent, labs 40 percent, final exam 40 percent.','Office hours: Tuesday, 2 to 3 pm.','Final exam: June 11, 2027.','No late work policy is included.']
stream='BT /F1 12 Tf 50 750 Td '+' '.join('('+line+') Tj 0 -20 Td' for line in lines)+' ET'
objects=[b'<< /Type /Catalog /Pages 2 0 R >>',b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>',b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>',b'<< /Length '+str(len(stream)).encode()+b' >>\nstream\n'+stream.encode()+b'\nendstream']
data=bytearray(b'%PDF-1.4\n');offsets=[0]
for i,obj in enumerate(objects,1):
 offsets.append(len(data));data.extend(str(i).encode()+b' 0 obj\n'+obj+b'\nendobj\n')
xref=len(data);data.extend(b'xref\n0 6\n0000000000 65535 f \n')
for pos in offsets[1:]:data.extend(f'{pos:010d} 00000 n \n'.encode())
data.extend(b'trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n'+str(xref).encode()+b'\n%%EOF\n')
(out/'practice-syllabus.pdf').write_bytes(data)
(out/'bad-backup.json').write_text('{"format":"coursekin-browser","version":99}')
(out/'unreadable.pdf').write_bytes(b'not a PDF')
print(json.dumps({'fixtures':[p.name for p in out.iterdir()]}))
