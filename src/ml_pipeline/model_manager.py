import json
import importlib
import os
import torch
from pathlib import Path
from typing import Union, Dict, Any, Type
from ultralytics import YOLO
from torch import nn


class ModelManager:

    def __init__(self, config_path: str, ml_settings):
        self.config_path = Path(config_path)
        self.ml_settings = ml_settings
        self.models_config = self._load_and_interpolate_config()
        self.models = {}
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    def _load_and_interpolate_config(self) -> Dict[str, Any]:
        if not self.config_path.exists():
            raise FileNotFoundError(f"Конфигурационный файл не найден: {self.config_path}")

        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        for model_name, model_config in config.items():
            if 'model_path' in model_config:
                if model_name == 'cnn':
                    model_config['model_path'] = self.ml_settings.path_to_cnn
                elif model_name == 'gan':
                    model_config['model_path'] = self.ml_settings.path_to_gan

        return config

    def _load_model_class(self, class_path: str) -> Type[nn.Module]:
        module_path, class_name = class_path.rsplit('.', 1)
        try:
            module = importlib.import_module(module_path)
            return getattr(module, class_name)
        except (ImportError, AttributeError) as e:
            raise ImportError(f"Не удалось загрузить класс {class_path}: {str(e)}")

    def load_model(self, model_name: str) -> Union[YOLO, nn.Module]:
        if model_name in self.models:
            return self.models[model_name]

        if model_name not in self.models_config:
            raise ValueError(f"Конфигурация для модели '{model_name}' не найдена")

        config = self.models_config[model_name]
        model_path = config['model_path']

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Файл модели не найден: {model_path}")

        is_yolo = config.get('is_yolo', model_name == 'yolo' or 'yolo' in model_name.lower())

        if is_yolo:
            model = YOLO(model_path)
            if 'model_type' in config:
                model.task = config['model_type']
        else:
            if 'model_class' not in config:
                raise KeyError(f"Для модели '{model_name}' отсутствует обязательный ключ 'model_class'")

            model_class = self._load_model_class(config['model_class'])
            model_args = config.get('model_args', {})
            model = model_class(**model_args).to(self.device)

            state_dict = torch.load(model_path, map_location=self.device)
            if 'G' in state_dict:
                model.load_state_dict(state_dict['G'])
            elif 'generator_state_dict' in state_dict:
                model.load_state_dict(state_dict['generator_state_dict'])
            elif 'state_dict' in state_dict:
                model.load_state_dict(state_dict['state_dict'])
            else:
                try:
                    model.load_state_dict(state_dict)
                except RuntimeError as e:
                    raise RuntimeError(f"Не удалось загрузить веса: {str(e)}")

            model.eval()

        self.models[model_name] = model
        return model

    def save_model(
            self,
            model: Union[YOLO, nn.Module],
            save_path: str,
            model_name: str = None,
            additional_data: Dict[str, Any] = None
    ) -> None:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)

        if isinstance(model, YOLO) or (
                model_name and model_name in self.models_config and 'yolo' in model_name.lower()):
            model.save(save_path)
        else:
            state_dict = {
                'state_dict': model.state_dict(),
                'model_type': model_name if model_name else 'pytorch_model',
                'model_class': model.__class__.__name__,
                **(additional_data if additional_data else {})
            }
            torch.save(state_dict, save_path)

    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        if model_name not in self.models_config:
            raise ValueError(f"Модель '{model_name}' не найдена в конфигурации")

        config = self.models_config[model_name]
        model_path = config['model_path']

        info = {
            'name': model_name,
            'path': model_path,
            'exists': os.path.exists(model_path),
            'size': os.path.getsize(model_path) if os.path.exists(model_path) else 0,
            'type': 'yolo' if model_name == 'yolo' else 'pytorch'
        }

        if model_name == 'cnn':
            info['task'] = config.get('model_type', 'segment')
        else:
            info['model_class'] = config['model_class'].__name__
        return info

# if __name__ == '__main__':
#     models_config = {
#         'cnn': {
#             'model_path': r'D:\Projects\Python\diploma_project\src\ml_pipeline\model_cnn\results\yolo_best_v4.pt',
#             'model_type': 'segment',
#             'is_yolo': True
#         },
#         'gan': {
#             'model_path': r'D:\Projects\Python\diploma_project\src\ml_pipeline\model_gan\results\states_tf_places2.pth',
#             'model_class': Generator,
#             'model_args': {'cnum_in': 5, 'cnum': 48, 'return_flow': False}
#         }
#     }
#
#     model_manager = ModelManager(models_config)
#
#     cnn_model = model_manager.load_model('cnn')
#     gan_model = model_manager.load_model('gan')
#
#     model_manager.save_model(gan_model,
#                              r'D:\Projects\Python\diploma_project\src\ml_pipeline\model_gan\results\weights.pt', 'cnn')
#     model_manager.save_model(cnn_model,
#                              r'D:\Projects\Python\diploma_project\src\ml_pipeline\model_cnn\results\weights.pt', 'gan')
#
#     print(model_manager.get_model_info('cnn'))
#     print(model_manager.get_model_info('gan'))
