from pathlib import Path
from fastapi.templating import Jinja2Templates

current_working_directory: Path = Path.cwd()
templates = Jinja2Templates(directory=f"{current_working_directory}/app/router/template")
