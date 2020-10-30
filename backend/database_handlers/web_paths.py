from dataclasses import dataclass
from pathlib import Path


@dataclass
class WebPathStructure:
    backend_dir_absolute: str = Path('backend').absolute()
    frontend_dir_absolute: str = Path('frontend').absolute()
    frontend_ignore: str = 'static'
