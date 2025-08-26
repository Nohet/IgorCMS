import pathlib


class Config:
    def __init__(self, example_config_path: str = None, config_path: str = None):
        self.example_config_file = example_config_path or "config.example.json"
        self.config_file = config_path or "config.json"

    def copy_config(self):
        example_config_content = (pathlib.Path(__file__).parent.parent / self.example_config_file).read_text()

        (pathlib.Path(__file__).parent.parent / self.config_file).write_text(example_config_content)

    def exists(self):
        return (pathlib.Path(__file__).parent.parent / self.config_file).exists()

