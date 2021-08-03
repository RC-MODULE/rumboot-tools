import os
import shutil
import glob 
import sys 
import zipfile
from rumboot import __version__

major = sys.version_info.major
minor = sys.version_info.minor
micro = sys.version_info.micro

packagedir=f"rumboot-tools-{__version__}-python{major}.{minor}.{micro}"

if os.path.exists(packagedir):
    print("Cleaning up...")
    shutil.rmtree(packagedir)
os.mkdir(packagedir)
os.mkdir(f"{packagedir}\wheels")

print("Building windows packages...")
os.system("pip wheel .")
script = open(f"{packagedir}/install.cmd", "w+")
for f in glob.glob("*.whl"):
    os.rename(f, f"{packagedir}\wheels\\{f}")
    script.write(f"pip install wheels\\{f}\n\r")
script.close()


def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file), 
                       os.path.relpath(os.path.join(root, file), 
                                       os.path.join(path, '..')))
      
zipf = zipfile.ZipFile(f'{packagedir}.zip', 'w', zipfile.ZIP_DEFLATED)
zipdir(packagedir, zipf)
zipf.close()

print(f"Built  {packagedir}")
