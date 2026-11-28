"""Validate the exact supplied MFCase Complete 1.0.3 archive without installing it."""
import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import tempfile
import venv
from pathlib import Path
from zipfile import ZipFile

DIGEST = 'c603da2dc5e9e9d133842158aef701f7382a3ae92e6a500196048f2dea291175'
NAME = 'MFCase_Complete_V1.0.3_Full_Online_Install.zip'
COUNT = 31
SUITE = '''import unittest
suite = unittest.defaultTestLoader.discover('tests', pattern='test_*.py')
result = unittest.TextTestRunner(verbosity=2).run(suite)
print('MFCASE_VALIDATION_COUNTS', result.testsRun, len(result.failures), len(result.errors), len(result.skipped), len(result.expectedFailures), len(result.unexpectedSuccesses))
raise SystemExit(0 if result.wasSuccessful() and result.testsRun == 31 and not result.skipped and not result.expectedFailures and not result.unexpectedSuccesses else 1)
'''

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', nargs='?', type=Path, default=Path(NAME))
    parser.add_argument('--report', type=Path, default=Path('MFCase_Complete_Validation_Report.json'))
    parser.add_argument('--use-current-python', action='store_true', help='Use existing test dependencies instead of a new temporary virtual environment')
    args = parser.parse_args()
    report_path = args.report.resolve()
    report = {'archive': NAME, 'expected_sha256': DIGEST, 'platform': platform.system(), 'launcher_python': platform.python_version(), 'status': 'FAIL', 'tests': None, 'installer_executed': False, 'live_update_tested': False}
    try:
        data = args.archive.read_bytes()
        report['archive_sha256'] = hashlib.sha256(data).hexdigest()
        if report['archive_sha256'] != DIGEST:
            raise RuntimeError('Archive hash mismatch; use the exact supplied 1.0.3 installer.')
        with tempfile.TemporaryDirectory(prefix='mfcase_complete_validation_') as td:
            root = Path(td)
            archive = root / NAME
            archive.write_bytes(data)
            with ZipFile(archive) as z:
                if z.testzip() is not None:
                    raise RuntimeError('Archive CRC failed.')
                # The exact archive hash is verified before extracting any member.
                z.extractall(root / 'source')
            app = root / 'source' / 'MFCase_Complete_V1.0.3'
            if (app/'PRODUCT_ID.txt').read_text().strip() != 'MFCaseComplete':
                raise RuntimeError('Product identity mismatch.')
            config = json.loads((app/'update_config.json').read_text())
            if config != {'repository':'chrisbrook0127/MFCase-Complete-Updates','asset_name':'MFCaseComplete_Update.zip'}:
                raise RuntimeError('Updater isolation check failed.')
            if 'self.app_version = "1.0.3"' not in (app/'case_number_ocr.py').read_text(encoding='utf-8'):
                raise RuntimeError('Application version mismatch.')
            env = dict(os.environ)
            home = root/'isolated_data'; home.mkdir()
            env.update(LOCALAPPDATA=str(home), APPDATA=str(home), HOME=str(home), USERPROFILE=str(home), PYTHONDONTWRITEBYTECODE='1', HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', MFCASE_SKIP_STARTUP_MAINTENANCE='1')
            # Keep pip setup outside the app directory and never run SETUP.bat.
            if args.use_current_python:
                python = Path(sys.executable)
            else:
                if sys.version_info[:2] != (3, 11):
                    raise RuntimeError('Use Python 3.11 for the Windows validation environment.')
                venv.create(root/'venv', with_pip=True)
                python = root/'venv'/('Scripts/python.exe' if os.name=='nt' else 'bin/python')
                subprocess.run([str(python),'-m','pip','install','numpy','opencv-python-headless','Pillow','pymupdf<2.0'], check=True, cwd=root)
            report['test_python'] = subprocess.check_output([str(python),'-c','import platform; print(platform.python_version())'], text=True).strip()
            subprocess.run([str(python),'verify_package.py'],check=True,cwd=app,env=env)
            report['package_integrity'] = 'PASS'
            process = subprocess.run([str(python),'-c',SUITE],cwd=app,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,errors='replace')
            print(process.stdout)
            lines = [line for line in process.stdout.splitlines() if line.startswith('MFCASE_VALIDATION_COUNTS ')]
            if len(lines) != 1:
                raise RuntimeError('Missing or ambiguous application test counts.')
            counts = [int(x) for x in lines[0].split()[1:]]
            report['tests'] = dict(zip(['run','failures','errors','skipped','expected_failures','unexpected_successes'],counts))
            if process.returncode or counts != [COUNT,0,0,0,0,0]:
                raise RuntimeError('Application regression validation failed.')
            report['status'] = 'PASS'
    except Exception as error:
        report['failure_type'] = type(error).__name__
        print('VALIDATION FAILED:', error, file=sys.stderr)
    finally:
        report_path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        print('Report:', report_path)
    return 0 if report['status']=='PASS' else 1

if __name__ == '__main__':
    raise SystemExit(main())
