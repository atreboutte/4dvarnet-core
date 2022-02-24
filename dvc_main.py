import inspect
import hydra
import hydra_config
import shlex
from omegaconf import OmegaConf
from pathlib import Path
import subprocess

"""
- [ ] register resolver
- [ ] dump config
- [ ] print dvc command

"""

XP_FILE_NAME = "xp_config"

class DvcStageBuilder:
    def __init__(self, name):
        self.name = name
        self.options = []
        self.base_cmd = []
        self.app_cmd = []
        self.init_attrs()

    def init_attrs(self):
        self.options = []
        self.base_cmd = ["dvc", "stage", "add", "--force"]
        self.app_cmd = [
            "python",
            "-c",
            "import dvc_main as dm; dm.dvc_execute()",
        ]

    def add_opt(self, value, opt):
        if value is not None:
            self.options.append((opt, value))
        else: 
            self.options.append((opt,))
        return value

    def cmd(self):
        parts = self.base_cmd + [tt for t in set(self.options) for tt in t] + self.app_cmd
        print(parts)
        cmd = shlex.join(parts)
        self.options = []
        return cmd

def register_resolvers(stage_builder):
        OmegaConf.register_new_resolver(
            "aprl", stage_builder.add_opt, replace=True
        )
        OmegaConf.register_new_resolver(
            f"aprl_cmd", stage_builder.cmd, replace=True
        )

@hydra.main(config_path='hydra_config', config_name='dvc_main')
def dvc_dump(cfg):
    sb = DvcStageBuilder('yo')
    register_resolvers(sb)
    OmegaConf.resolve(cfg)
    Path(f'{ XP_FILE_NAME }.yaml').write_text(OmegaConf.to_yaml(cfg))
    print(cfg.dvc.cmd)
    ret_code = subprocess.call(shlex.split(cfg.dvc.cmd))
    print(ret_code)


def dvc_execute():
    import hydra
    with hydra.initialize():
        cfg = hydra.compose(config_name=XP_FILE_NAME)

    hydra.utils.call(cfg.dvc.entrypoint, cfg=cfg)

if __name__ == '__main__':
    dvc_dump()
