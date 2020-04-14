import yaml
from pathlib import Path

__all__ = ('load_config', ) # ограничиваем экспорт из файла только одной функции

def load_config(config_file=None):
    default_file = Path(__file__).parent / 'config.yaml'
    with open(default_file, 'r') as f:
        config = yaml.safe_load(f)

    # Если указан другой конфиг, то считываем его и обновляем значения по умолчанию.
    if config_file:
        cf = yaml.safe_load(config_file)
        config.update(cf)
    return config
