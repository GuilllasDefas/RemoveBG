(.venv) PS E:ZPy_Projetos\RemoveBG> nuitka --standalone `
>> --output-filename=RemoveBG.exe `
>> --windows-disable-console `
>> --remove-output `
>> --windows-icon-from-ico=app/gui/icon.ico `
>> --enable-plugin=pyqt6 `
>> --enable-plugin=data-files `
>> --enable-plugin=anti-bloat `
>> main.py

Comando Nuitka Otimizado para Tamanho e Desempenho
(.venv) PS E:\Py_Projetos\RemoveBG> 

pyinstaller `
  --onedir `
  --name RemoveBG `
  --windowed `
  --icon="app/gui/icon.ico" `
  --add-data="app/gui/icon.ico;app/gui" `
  --collect-submodules=Pillow `
  --collect-submodules=PyQt6 `
  --collect-submodules=PyQt6_sip `
  --collect-submodules=rembg `
  --exclude-module=bandit `
  --exclude-module=PyYAML `
  --exclude-module=stevedore `
  --exclude-module=pbr `
  --exclude-module=setuptools `
  --exclude-module=black `
  --exclude-module=blue `
  --exclude-module=click `
  --exclude-module=pathspec `
  --exclude-module=tomli `
  --exclude-module=mypy_extensions `
  --exclude-module=flake8 `
  --exclude-module=mccabe `
  --exclude-module=pycodestyle `
  --exclude-module=pyflakes `
  --exclude-module=darkdetect `
  --exclude-module=isort `
  --exclude-module=Nuitka `
  --exclude-module=pipdeptree `
  --exclude-module=PyQt5 `
  --exclude-module=PyQt5_sip `
  --exclude-module=PyQt5_stubs `
  --exclude-module=pipreqs `
  --exclude-module=ipython `
  --exclude-module=nbconvert `
  --exclude-module=nbformat `
  --exclude-module=jupyter_core `
  --exclude-module=jupyter_client `
  --exclude-module=pywin32-ctypes `
  --exclude-module=pyinstaller-hooks-contrib `
  --exclude-module=tinycss2 `
  main.py

alternativa:

pyinstaller `
  --onedir `
  --name RemoveBG `
  --windowed `
  --icon="app/gui/icon.ico" `
  --add-data="app/gui/icon.ico;app/gui" `
  main.py

alternativa:

nuitka `
  --standalone `
  --output-filename=RemoveBG.exe `
  --windows-console-mode=disable `
  --windows-icon-from-ico="app/gui/icon.ico" `
  --include-data-files="app/gui/icon.ico=app/gui/icon.ico" `
  --enable-plugin=pyqt6,upx `
  --upx-binary="E:\UPX\upx.exe" `
  --include-qt-plugins=platforms `
  --lto=yes `
  --assume-yes-for-downloads `
  --noinclude-default-mode=error `
  --noinclude-numba-mode=nofollow `
  --module-parameter=rembg-no-models=yes `
  --include-package-data=rembg `
  --include-package=rembg `
  --include-module=pymatting `
  --python-flag=no_site `
  --python-flag=no_warnings `
  main.py


# Comando para compressão UPX (depois da compilação)
# E:\UPX\upx.exe -9 dist\RemoveBG\RemoveBG.exe

# Comando Nuitka revisado para resolver problemas de execução
nuitka `
  --standalone `
  --output-dir="dist" `
  --windows-console-mode=disable `
  --windows-icon-from-ico="app/gui/icon.ico" `
  --include-data-files="app/gui/icon.ico=app/gui/icon.ico" `
  --enable-plugin=pyqt6 `
  --include-qt-plugins=platforms,styles,imageformats,iconengines `
  --lto=yes `
  --assume-yes-for-downloads `
  --noinclude-default-mode=error `
  --include-package-data=rembg `
  --include-package=rembg `
  --include-package=onnxruntime `
  --include-package=numpy `
  --include-package=PIL `
  --include-module=pymatting `
  --include-module=pooch `
  --include-module=tqdm `
  --include-module=cv2 `
  --include-module=imageio `
  --python-flag=no_site `
  --python-flag=no_warnings `
  main.py

# Comando alternativo sem UPX e com todos os modelos do rembg 
# (Tente este se o primeiro não funcionar)
nuitka `
  --standalone `
  --output-dir="dist" `
  --windows-console-mode=disable `
  --windows-icon-from-ico="app/gui/icon.ico" `
  --include-data-files="app/gui/icon.ico=app/gui/icon.ico" `
  --enable-plugin=pyqt6 `
  --include-qt-plugins=platforms,styles,imageformats,iconengines `
  --lto=no `
  --assume-yes-for-downloads `
  --noinclude-numba-mode=nofollow `
  --module-parameter=numba-disable-jit=yes `
  --include-package-data=rembg `
  --include-package=rembg `
  --include-package=onnxruntime `
  main.py

o onmxruntime é necessário para o funcionamento do rembg, mas ele depende do numba que pode trazer uma tamnho desnecessário para o executável final.

# Caso ainda tenha problemas, tente com o console habilitado 
# para ver mensagens de erro ao executar
nuitka `
  --standalone `
  --output-dir="dist" `
  --windows-console-mode=enable `
  --windows-icon-from-ico="app/gui/icon.ico" `
  --include-data-files="app/gui/icon.ico=app/gui/icon.ico" `
  --enable-plugin=pyqt6 `
  --include-package-data=rembg `
  --include-package=rembg `
  main.py
