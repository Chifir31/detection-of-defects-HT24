import os
import shutil

import torch
from PIL import Image, ImageDraw
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.shortcuts import render
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from torch import classes
from transformers import (AutoImageProcessor, AutoModelForObjectDetection)
import supervision as sv
from .models import Report, Photo
import PIL
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io


DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
classes = {'dead-pixels': 'Битые пиксели', 'scratches': 'Царапины', 'lock': 'Замок',
           'chip': 'Скол', 'missing-screw': 'Отсутствующий шуруп', 'keyboard-defect': 'Дефект клавиатуры'}

model = AutoModelForObjectDetection.from_pretrained('./main/deter_model').to(DEVICE)
processor = AutoImageProcessor.from_pretrained('./main/deter_model')

def start_detection(request):
    return render(request, 'main/start_detection.html')

def float_to_binary(value):
    if value >= 0.5:
        return 1
    else:
        return 0

def result_detection(request):
    media_dir = 'media/photos/'
    if os.path.exists(media_dir):
        for filename in os.listdir(media_dir):
            file_path = os.path.join(media_dir, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
    files = request.FILES.getlist('files')
    serial_number = request.POST.get('serialNumber')
    print(serial_number)
    Photo.objects.all().delete()
    Report.objects.all().delete()
    number, count_defects, count_photo = 0, 0, 0
    defects = {'Битые пиксели': 0, 'Царапины': 0, 'Замок': 0, 'Скол': 0, 'Отсутствующий шуруп': 0, 'Дефект клавиатуры': 0}
    for file in files:
        count_photo += 1
        image = Image.open(file)
        inputs = processor(image, return_tensors="pt").to(DEVICE)

        with torch.no_grad():
            outputs = model(**inputs)

        results = processor.post_process_object_detection(outputs, target_sizes=torch.tensor([image.size[::-1]]), threshold=0.3)
        print(results)
        for result in results:
            scores, label_ids, boxes = result["scores"], result["labels"], result["boxes"]
            if len(scores) != 0:
                for score, label_id, box in zip(scores , label_ids, boxes):
                    score, label = score.item(), label_id.item()
                    box = [int(round(i, 0)) for i in box.tolist()]
                    predict = classes[model.config.id2label[label]]
                    defects[predict] = defects[predict] + 1

                    # Создаем объект рисования на изображении
                    draw = ImageDraw.Draw(image)

                    # Рисуем прямоугольник на изображении
                    draw.rectangle(box, outline=(255, 0, 0), width=5)

                    # Сохраняем изображение в памяти
                    buffer = io.BytesIO()
                    image.save(buffer, format='JPEG')
                    buffer.seek(0)

                    # Создаем новый экземпляр модели Photo и сохраняем изображение
                    photo = Photo(image=ContentFile(buffer.read(), name=file.name), predict=predict, x1=box[0], y1=box[1], x2=box[2], y2=box[3])
                    photo.save()
                    # photo = Photo(image=file, id=number, predict=predict, x1=box[0], y1=box[1], x2=box[2], y2=box[3])
                    # photo.save()
                    number += 1
                    count_defects += 1
            else:
                photo = Photo(image=file, id=number, predict='Нет дефектов', x1=0, y1=0, x2=0, y2=0)
                photo.save()
                number += 1
    resume = 'Контроль качества пройден'
    if count_defects != 0:
        resume = 'Контроль качества не пройден'
    Report(serial_number=serial_number, count_defects=count_defects, count_photos=count_photo, resume = resume,
           dead_pixels = defects['Битые пиксели'], scratches=defects['Царапины'], lock = defects['Замок'], chip = defects['Скол'],
           missing_screw = defects['Отсутствующий шуруп'], keyboard_defect = defects['Дефект клавиатуры']).save()
    photos = Photo.objects.all()
    return render(request, 'main/result_detection.html', {'photos': photos, 'serial_number': serial_number, 'count_defects': count_defects, 'count_photo': count_photo, 'defects': defects})

def do_report(request):
    report = Report.objects.get()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    # pdf_file = "output.pdf"
    c = canvas.Canvas(response, pagesize=letter)
    pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
    c.setFont('Arial', 12)
    c.drawString(100, 750, "Отчет")
    c.drawString(100, 730, f"Серийный номер: {report.serial_number}")
    # # Заголовки
    c.drawString(100, 700, f"Обработано фотографий: {report.count_photos}")
    c.drawString(100, 680, f"Общее число дефектов: {report.count_defects}")
    c.line(100, 670, 500, 670)
    c.drawString(150, 650, f"Количество царапин: {report.scratches}")
    c.drawString(150, 630, f"Количество битых пикселей: {report.dead_pixels}")
    c.drawString(150, 610, f"Количество дефектов клавиатуры: {report.keyboard_defect}")
    c.drawString(150, 590, f"Количество проблем с замками: {report.lock}")
    c.drawString(150, 570, f"Количество отсутствующих шурупов: {report.missing_screw}")
    c.drawString(150, 550, f"Количество сколов: {report.chip}")

    c.line(100, 520, 500, 520)
    c.setFont('Arial', 14)
    c.drawString(100, 500, f"Итог: {report.resume}")

    c.showPage()

    # Указываем размеры страницы
    width, height = letter
    #
    # for img_file in request:
    #     # Открываем изображение с помощью Pillow
    #     img = Image.open(img_file)
    #     img_width, img_height = img.size
    #
    #     # Приводим размер изображения к необходимому
    #     aspect = img_height / img_width
    #     new_width = width - 40  # Оставляем отступы по 20 с каждой стороны
    #     new_height = new_width * aspect
    #
    #     if new_height > height - 40:  # Если изображение не помещается, лучше уменьшить
    #         new_height = height - 40
    #         new_width = new_height / aspect
    #
    #     # Центрируем изображение по странице
    #     x = (width - new_width) / 2
    #     y = height - new_height - 20  # Отступ сверху
    #
    #     # Рисуем изображение
    #     c.drawImage(img_file, x, y, width=new_width, height=new_height)
    #     c.showPage()
    #
    c.save()
    return response
