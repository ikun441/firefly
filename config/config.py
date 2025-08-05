# 操作config.yaml的方法
import yaml

class config:
    def __init__(self):
        self.path = "config.yaml"
        self.key = "self_key"
        self.value = "self.value"
    def get_config(self):
        with open(self.path,"r") as f:
            data = yaml.safe_load(f)
            get_data = data[self.key]
            return get_data
    def updata_config(self):
             get_data = self.get_config()
             get_data[self.key] = self.value
             with open(self.path,"w") as f:
                yaml.dump(get_data,f)
    def check_config(self):
        if self.key == "" or self.value == "":
            return "config_dose_not_exist"
        else:
            return True
    def delete_config(self):
        get_data = self.get_config()
        del get_data[self.key]
        with open(self.path,"w") as f:
            yaml.dump(get_data,f)