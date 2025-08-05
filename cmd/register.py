import os
import yaml
class register_cmd:
    def __init__(self):
        self.name = "register_name" #将会在data/cmd下创建一个名为name的json的文件来注册系统命令
        self.cmd = "register_cmd"   #这是你想要注册的命令
        self.usage = "register_help>" #在此处显示此类命令的帮助
        self.type = "general"  #在此处填写你要注册的命令的分类
    def get_cmd(self):
        result = [self.name,self.cmd,self.usage,self.type]
        return result
    def register(self):
        return (f"命令{self.name}注册成功<{self.type}><{self.cmd}>")
    def check_cmd(self):
        if self.name == "" or self.cmd == "" or self.type == "":
            return False
        else:
            return True
    def check_path(self):
        if os.path.exists(project_root,"data","cmd",f"{self.name}.yaml"):
            return False
        else:
            return True
    def check_name(self):
        with open(os.path.join(project_root,"data","cmd",f"{self.name}.yaml"),"r") as f:
            data = yaml.safe_load(f)
            if data[self.name] == None:
                return False
            else:
                return True
    def check_type(self):
        with open(os.path.join(project_root,"data","cmd",f"{self.name}.yaml"),"r") as f:
            data = yaml.safe_load(f)
            if data[self.type] == None:
                return False
            else:
                return True
    def check_cmd(self):
        with open(os.path.join(project_root,"data","cmd",f"{self.name}.yaml"),"r") as f:
            data = yaml.safe_load(f)
            if data[self.cmd] == None:
                return False
            else:
                return True
    def get_data(self):
        with open(os.path.join(project_root,"data","cmd",f"{self.name}.yaml"),"r") as f:
            data = yaml.safe_load(f)
            return data
    def write_data(self,data):
        with open(os.path.join(project_root,"data","cmd",f"{self.name}.yaml"),"w") as f:
            f.write(yaml.dump(data))
        