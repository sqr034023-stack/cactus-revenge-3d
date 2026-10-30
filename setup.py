from setuptools import setup
PRC_DATA = '''
load-display pandagles2
aux-display pandagles
notify-level info
gl-debug true
'''

setup(
    name='cactus-revenge',
    version='1.0.0',
    options={
        'build_apps': {
            'application_id': 'org.cactusrevenge.game',
            'android_version_code': 1,
            'platforms': ['android'],
            'android_abis': ['arm64-v8a', 'armeabi-v7a'],
            'gui_apps': {'cactus-revenge': 'main.py'},
            'plugins': ['pandagles2', 'pandagles', 'p3openal_audio'],
            'include_patterns': ['**/*.png', '**/*.jpg', '**/*.egg', '**/*.bam'],
            'extra_prc_data': PRC_DATA,
            'android_min_sdk_version': 21,
            'android_target_sdk_version': 35,
            'log_filename': 'cactus-revenge.log',
        },
    },
    classifiers=['Topic :: Games/Entertainment'],
)
