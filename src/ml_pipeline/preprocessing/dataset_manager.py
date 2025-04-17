import os
import shutil
import uuid


class PicsManager:
    def __init__(self, source_root, destination_root):
        self.source_root = source_root
        self.destination_root = destination_root
        os.makedirs(self.destination_root, exist_ok=True)

    def collect_photos(self):
        """Собирает все фотографии из подкаталогов и присваивает случайные имена."""
        count = 0  # Счётчик обработанных фотографий
        for dirpath, _, filenames in os.walk(self.source_root):
            for filename in filenames:
                if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                    # Создаем случайное имя файла
                    new_name = f"{uuid.uuid4()}.jpg"  # или .png, в зависимости от формата
                    source_path = os.path.join(dirpath, filename)
                    destination_path = os.path.join(self.destination_root, new_name)

                    # Копируем файл в новую директорию
                    shutil.copy2(source_path, destination_path)

                    count += 1  # Увеличиваем счётчик

                    # Выводим количество обработанных фотографий каждые 100
                    if count % 100 == 0:
                        print(f"Обработано {count} фотографий...")

        print(f"Сбор фотографий завершен! Всего обработано: {count} фотографий.")

    def organize_photos(self):
        """Организует фотографии: нумерация и разделение на два датасета."""
        # Получаем список всех файлов в исходной директории
        files = [f for f in os.listdir(self.source_root) if os.path.isfile(os.path.join(self.source_root, f))]
        files.sort()  # Сортируем по алфавиту

        # Создаем папки для двух датасетов
        dataset1_path = os.path.join(self.destination_root, 'dataset1')
        dataset2_path = os.path.join(self.destination_root, 'dataset2')
        os.makedirs(dataset1_path, exist_ok=True)
        os.makedirs(dataset2_path, exist_ok=True)

        # Перемещаем файлы и нумеруем их
        for index, filename in enumerate(files):
            # Форматируем номер
            new_name = f"{index:06d}.jpg"
            source_path = os.path.join(self.source_root, filename)

            if index < 50000:
                destination_path = os.path.join(dataset1_path, new_name)
            else:
                destination_path = os.path.join(dataset2_path, new_name)

            # Перемещаем файл
            shutil.move(source_path, destination_path)

            # Выводим количество обработанных фотографий каждые 100
            if (index + 1) % 100 == 0:
                print(f"Обработано {index + 1} фотографий...")

        print("Организация фотографий завершена!")

    def split_dataset(self):
        """Разделяет 50000 фотографий из dataset1 по 5 папкам."""
        dataset1_path = os.path.join(self.destination_root, 'dataset1')
        categories = ['dataset1_noise', 'dataset1_abrasion', 'dataset1_blur', 'dataset1_scratch']

        # Создаем папки для категорий
        for category in categories:
            os.makedirs(os.path.join(self.destination_root, category), exist_ok=True)

        # Получаем список файлов в dataset1
        files = [f for f in os.listdir(dataset1_path) if os.path.isfile(os.path.join(dataset1_path, f))]
        files.sort()

        # Перемещаем файлы в соответствующие папки
        for index, filename in enumerate(files):
            source_path = os.path.join(dataset1_path, filename)

            # Определяем категорию по индексу
            category_index = index % len(categories)
            destination_path = os.path.join(self.destination_root, categories[category_index], filename)

            shutil.move(source_path, destination_path)

            if (index + 1) % 100 == 0:
                print(f"Перемещено {index + 1} фотографий в категорию...")

        print("Разделение фотографий по категориям завершено!")


if __name__ == '__main__':
    source_directory = r'D:\Dataset\Original\all'
    destination_directory = r'D:\Dataset\Original'
    manager = PicsManager(source_directory, destination_directory)
    manager.split_dataset()
