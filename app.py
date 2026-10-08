from pathlib import Path
from io import BytesIO
import re
import fitz
from PIL import Image, ImageOps, UnidentifiedImageError
from flask import Flask, render_template, request, send_file

ROOT = Path(__file__).resolve().parent
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 30 * 1024 * 1024
MEDIUM = fitz.Font(fontfile=str(ROOT / 'assets/Pretendard-Medium.otf'))
BOLD = fitz.Font(fontfile=str(ROOT / 'assets/Pretendard-ExtraBold.otf'))
LIMITS = {'team_name': 16, 'members': 100, 'reflection': 160, 'place': 24, 'insight': 90}

def generate(data, photos):
    doc = fitz.open(ROOT / 'assets/report.pdf')
    page = doc[0]
    sx, sy = page.rect.width / 990, page.rect.height / 1400
    page.insert_font(fontname='PM', fontbuffer=MEDIUM.buffer)
    page.insert_font(fontname='PB', fontbuffer=BOLD.buffer)
    color = (.27, .26, .23)
    def width(text, size, bold=False):
        return (BOLD if bold else MEDIUM).text_length(text, fontsize=size)
    def line(x, y, text, size, bold=False):
        # CFF fonts can misencode a tilde in PDF consumers; use the standard glyph for it.
        chunks = re.split(r'(~)', text)
        for chunk in chunks:
            if not chunk:
                continue
            font = 'helv' if chunk == '~' else ('PB' if bold else 'PM')
            page.insert_text((x*sx, y*sy), chunk, fontname=font, fontsize=size*sx, color=color)
            x += fitz.get_text_length(chunk, fontname='helv', fontsize=size) if chunk == '~' else width(chunk,size,bold)
    def wrap(text, size, max_width):
        rows = []
        for paragraph in text.split('\n'):
            row = ''
            for ch in paragraph:
                if width(row+ch,size) > max_width:
                    rows.append(row.rstrip()); row = ch
                else:
                    row += ch
            rows.append(row.rstrip())
        return rows
    def block(text, box, size, align='left', bold=False):
        x1,y1,x2,y2 = box
        while size >= 14:
            rows = wrap(text,size,x2-x1)
            leading = size*1.25
            if len(rows)*leading <= y2-y1:
                break
            size -= .5
        else:
            raise ValueError('입력 내용이 PDF 칸을 초과합니다. 내용을 줄여주세요.')
        y = (y1+y2-len(rows)*leading)/2 + size
        for row in rows:
            x = (x1+x2-width(row,size,bold))/2 if align=='center' else x1
            line(x,y,row,size,bold); y += leading
    number = data['team_number']
    size = 60 if len(number)==1 else 56
    line((545+618-width(number,size,True))/2,188,number,size,True)
    block(data['team_name'],(140,352,288,394),20,'center')
    block(data['members'],(410,352,930,394),17)
    for i in range(3):
        top = 580+166*i
        block(data[f'place_{i}'],(66,top+10,247,top+156),20,'center')
        bullets = [data[f'insight_{i}_{j}'] for j in range(2)]
        size = 18
        while size >= 14:
            rows = [wrap(t,size,327) for t in bullets]
            leading = size*1.28
            height = sum(len(r) for r in rows)*leading+9
            if height <= 142:
                break
            size -= .5
        else:
            raise ValueError('인사이트 내용을 줄여주세요.')
        y = top+(166-height)/2+size
        for item in rows:
            line(272,y,'·',20)
            for row in item:
                line(291,y,row,size); y+=leading
            y+=9
        if photos[i]:
            image = ImageOps.exif_transpose(Image.open(BytesIO(photos[i])))
            image = image.convert('RGB'); image.thumbnail((2400,2400))
            buf = BytesIO(); image.save(buf,format='JPEG',quality=90)
            page.insert_image(fitz.Rect(650*sx,(top+9)*sy,931*sx,(top+157)*sy),stream=buf.getvalue(),keep_proportion=True)
    block(data['reflection'],(66,1218,930,1290),23)
    result = doc.tobytes(garbage=4,deflate=True)
    doc.close()
    return result

@app.get('/')
def index():
    return render_template('index.html', limits=LIMITS)

@app.post('/pdf')
def pdf():
    data = {k:v.strip() for k,v in request.form.items()}
    try:
        number = data.get('team_number','')
        if not number.isdecimal() or not 1 <= int(number) <= 99:
            raise ValueError('조 번호는 1~99로 입력해주세요.')
        data['team_number'] = str(int(number))
        fields = [(k,LIMITS[k]) for k in ('team_name','members','reflection')]
        fields += [(f'place_{i}',LIMITS['place']) for i in range(3)]
        fields += [(f'insight_{i}_{j}',LIMITS['insight']) for i in range(3) for j in range(2)]
        for key,limit in fields:
            if not data.get(key) or len(data[key])>limit:
                raise ValueError(f'모든 항목을 입력하고 글자 수 제한을 확인해주세요. ({key})')
        photos = [request.files[f'photo_{i}'].read() if request.files.get(f'photo_{i}') else None for i in range(3)]
        result = generate(data,photos)
    except (ValueError,UnidentifiedImageError,Image.DecompressionBombError) as error:
        return str(error),400
    name = re.sub(r'[\\/:*?"<>|\x00-\x1f]','_',data['team_name'])
    return send_file(BytesIO(result),mimetype='application/pdf',as_attachment=True,download_name=f'현장체험_보고서_{data["team_number"]}조_{name}.pdf')

@app.errorhandler(413)
def too_large(error):
    return '사진 전체 용량은 30MB 이내로 첨부해주세요.',413

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000)
