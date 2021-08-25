# -*- mode: python ; coding: utf-8 -*-
# $pyinstaller kine_project_reducer-onefile.spec

block_cipher = None

src = [
    './src/kine_project_reducer.py', 
    './src/kine_ffmpeg.py', 
    './src/kine_zip.py', 
    './src/kine_logger.py', 
    './src/kine_media_resizer.py', 
    './src/kine_info.py',
    './src/kine_protobuf.py',
    './src/km_protobuf/kinemaster_project_wire_pb2.py']

a = Analysis(src,
             pathex=['./src', './scr/km_protobuf'],
             binaries=[('./pre-ffmpeg/ffprobe', 'pre-ffmpeg'), ('./pre-ffmpeg/ffmpeg', 'pre-ffmpeg')],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='KineReducer',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )
