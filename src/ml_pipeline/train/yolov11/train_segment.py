from ultralytics import YOLO

# Загрузка модели для сегментации
model = YOLO('yolo11n-seg.pt')  # Поддерживает сегментацию

# Обучение модели на ваших данных
results = model.train(
    data='data.yaml',  # Путь к файлу конфигурации
    epochs=1,         # Количество эпох
    imgsz=640,         # Размер изображений
    batch=16,          # Размер батча
    task='segment',    # Задача сегментации
    device='cpu',      # Использовать процессор
)

# Сохранение обученной модели
model.export(format='torchscript')
