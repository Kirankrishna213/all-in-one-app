from flask import render_template, request, flash, redirect, url_for, send_file
from app import app
from PyPDF2 import PdfMerger
from docx import Document
from PIL import Image, ImageEnhance, ImageFilter
import pytz
from datetime import datetime
import io

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/pdf-tools', methods=['GET', 'POST'])
def pdf_tools():
    if request.method == 'POST':
        files = request.files.getlist('pdf_files')
        if len(files) < 2:
            flash('Please upload at least 2 PDFs', 'danger')
            return redirect(url_for('pdf_tools'))
        
        merger = PdfMerger()
        for file in files:
            merger.append(file)
        
        output = io.BytesIO()
        merger.write(output)
        output.seek(0)
        
        return send_file(
            output,
            as_attachment=True,
            download_name='merged.pdf',
            mimetype='application/pdf'
        )
    
    return render_template('pdf_tools.html')

@app.route('/word-tools', methods=['GET', 'POST'])
def word_tools():
    if request.method == 'POST':
        file = request.files['word_file']
        if not file.filename.endswith('.docx'):
            flash('Please upload a .docx file', 'danger')
            return redirect(url_for('word_tools'))
        
        doc = Document(file)
        
        # Enhanced Word processing
        for para in doc.paragraphs:
            if request.form.get('find_text') and request.form.get('replace_text'):
                para.text = para.text.replace(
                    request.form['find_text'],
                    request.form['replace_text']
                )
        
        output = io.BytesIO()
        doc.save(output)
        output.seek(0)
        
        return send_file(
            output,
            as_attachment=True,
            download_name='edited.docx',
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
    
    return render_template('word_tools.html')

@app.route('/timezone', methods=['GET', 'POST'])
def timezone():
    timezones = sorted(pytz.all_timezones)
    common_timezones = [
        'UTC',
        'US/Eastern',
        'US/Central',
        'US/Mountain',
        'US/Pacific',
        'Europe/London',
        'Europe/Paris',
        'Asia/Kolkata',
        'Asia/Tokyo',
        'Australia/Sydney'
    ]
    
    if request.method == 'POST':
        from_tz = request.form['from_tz']
        to_tz = request.form['to_tz']
        time_str = request.form['time']
        ampm = request.form.get('ampm', 'AM')
        
        try:
            # Parse time with AM/PM
            time_obj = datetime.strptime(f"{time_str} {ampm}", "%I:%M %p")
            naive_time = datetime(2000, 1, 1, time_obj.hour, time_obj.minute)
            
            from_zone = pytz.timezone(from_tz)
            to_zone = pytz.timezone(to_tz)
            localized = from_zone.localize(naive_time)
            converted = localized.astimezone(to_zone)
            
            return render_template('timezone.html', 
                                result=converted.strftime('%I:%M %p %Z'),
                                timezones=timezones,
                                common_timezones=common_timezones)
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('timezone.html', 
                         timezones=timezones,
                         common_timezones=common_timezones)

@app.route('/image-tools', methods=['GET', 'POST'])
def image_tools():
    if request.method == 'POST':
        file = request.files['image_file']
        img = Image.open(file)
        
        # Apply all enhancements
        if request.form.get('brightness'):
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(float(request.form['brightness']))
        
        if request.form.get('contrast'):
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(float(request.form['contrast']))
        
        if request.form.get('sharpness'):
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(float(request.form['sharpness']))
        
        if request.form.get('rotate'):
            img = img.rotate(int(request.form['rotate']), expand=True)
        
        if request.form.get('blur_radius'):
            img = img.filter(ImageFilter.GaussianBlur(
                radius=float(request.form['blur_radius'])
            ))
        
        output = io.BytesIO()
        img.save(output, format='PNG')
        output.seek(0)
        
        return send_file(
            output,
            as_attachment=True,
            download_name='edited.png',
            mimetype='image/png'
        )
    
    return render_template('image_tools.html')