import os
import shutil
import uuid


class PicsManager:
    def __init__(self, source_root, destination_root):
        self.source_root = source_root
        self.destination_root = destination_root
        os.makedirs(self.destination_root, exist_ok=True)

    def collect_photos(self):
        count = 0
        for dirpath, _, filenames in os.walk(self.source_root):
            for filename in filenames:
                if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                    new_name = f"{uuid.uuid4()}.jpg"
                    source_path = os.path.join(dirpath, filename)
                    destination_path = os.path.join(self.destination_root, new_name)

                    shutil.copy2(source_path, destination_path)

                    count += 1
                    if count % 100 == 0:
                        print(f"Обработано {count} фотографий...")

        print(f"Сбор фотографий завершен! Всего обработано: {count} фотографий.")

    def organize_photos(self):
        """Организует фотографии: нумерация и разделение на два датасета."""
        files = [f for f in os.listdir(self.source_root) if os.path.isfile(os.path.join(self.source_root, f))]
        files.sort()
        dataset1_path = os.path.join(self.destination_root, 'dataset1')
        dataset2_path = os.path.join(self.destination_root, 'dataset2')
        os.makedirs(dataset1_path, exist_ok=True)
        os.makedirs(dataset2_path, exist_ok=True)

        for index, filename in enumerate(files):
            new_name = f"{index:06d}.jpg"
            source_path = os.path.join(self.source_root, filename)

            if index < 50000:
                destination_path = os.path.join(dataset1_path, new_name)
            else:
                destination_path = os.path.join(dataset2_path, new_name)
            shutil.move(source_path, destination_path)
            if (index + 1) % 100 == 0:
                print(f"Обработано {index + 1} фотографий...")

        print("Организация фотографий завершена!")

    def split_dataset(self):
        """Разделяет 50000 фотографий из dataset1 по 5 папкам."""
        dataset1_path = os.path.join(self.destination_root, 'dataset1')
        categories = ['dataset1_noise', 'dataset1_abrasion', 'dataset1_blur', 'dataset1_scratch']
        for category in categories:
            os.makedirs(os.path.join(self.destination_root, category), exist_ok=True)
        files = [f for f in os.listdir(dataset1_path) if os.path.isfile(os.path.join(dataset1_path, f))]
        files.sort()

        for index, filename in enumerate(files):
            source_path = os.path.join(dataset1_path, filename)

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
