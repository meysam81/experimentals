import os
from importlib import import_module
from pathlib import Path

# from glob import glob
from app.config import config
from meysam_utils import get_logger

logger = get_logger(__name__)

# root_path = Path(__file__).parent
# modules = [module.rstrip(".py").replace("/", ".") for module in glob(f"{root_path}/app/servers/*.py")]
# services_root = import_module("app.servers")
# modules = []
# logger.info(dir(services_root))
# for attr in dir(services_root):
#     if attr.startswith("__"):
#         continue
#     module = getattr(services_root, attr)
#     if not hasattr(module, "services"):
#         continue
#     modules.append(module)
# logger.info(modules)

root = Path(__file__).parent
services_dir = root / "app/servers"
services = []
for module in os.listdir(services_dir):
    if module.startswith("__"):
        continue
    mod = import_module(f"app.servers.{module.rstrip('.py')}")
    if not hasattr(mod, "services"):
        continue
    services.extend(mod.services)


logger.info(services)

if __name__ == "__main__":
    try:
        from app.metrics import PromServerInterceptor
        from app.server import serve

        if config.PROMETHEUS_ENABLED:
            from app.metrics import serve as metrics

            metrics()
        serve(services, {PromServerInterceptor()})
    except KeyboardInterrupt:
        print("Shutting down server ...")
        exit(0)
