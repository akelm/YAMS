# -*- mode: python -*-

block_cipher = None


a = Analysis(['yams/yams.py'],
             pathex=['/home/ania/Desktop/YAMS/yams', '/home/ania/.wine/drive_c/windows/system32', '/home/ania/.local', '/home/ania/.local/lib/python3.5', '/usr/lib/python3/dist-packages/spyder/utils/site', '/usr/lib/python35.zip', '/usr/lib/python3.5', '/usr/lib/python3.5/plat-x86_64-linux-gnu', '/usr/lib/python3.5/lib-dynload', '/home/ania/.local/lib/python3.5/site-packages', '/usr/local/lib/python3.5/dist-packages', '/usr/lib/python3/dist-packages', '/usr/lib/python35.zip', '/usr/lib/python3.5/plat-x86_64-linux-gnu', '/usr/lib/python3.5/lib-dynload', '/usr/lib/python3/dist-packages/IPython/extensions', '/home/ania/.ipython', '/home/ania/Desktop/YAMS','/usr/bin/upx','/usr/bin/'],
             binaries=[],
             datas=[],
             hiddenimports=['webbrowser'],
             hookspath=[],
             runtime_hooks=[],
             excludes=['PyQt4','gtk','atlas','crypto','pycairo','fortran-magic'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='yams',
          debug=True,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='yams')
