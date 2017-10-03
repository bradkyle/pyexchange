import json
import os


class Config():


    def load_config(self, directory):
        self.config = {}

        for config_file in os.listdir(directory):
            with open(config_file) as json_data_file:
                data = json.load(json_data_file)
                data.update(self.config)

    def get_config(self):
        return NotImplementedError

    def update_config(self):
        return NotImplementedError

    def persist_config(self):
        return NotImplementedError