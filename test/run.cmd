:: print(sys.executable)
:: C:\Users\xiaos\Anaconda3\envs\py3torch-cpu\python.exe test_run_all_tests.py


:: https://stackoverflow.com/questions/138497/iterate-all-files-in-a-directory-using-a-for-loop
::https://stackoverflow.com/questions/734598/how-do-i-make-a-batch-file-terminate-upon-encountering-an-error
@ECHO OFF
setlocal enabledelayedexpansion
for %%f in (.\*.py) do (
  echo "-------------------------------------------------------------------------------------" "checking: %%f"
  C:\Users\xiaos\Anaconda3\envs\py3torch-cpu\python.exe %%f || goto :error
)


goto :EOF


:error
echo Failed with error #%errorlevel%.
exit /b %errorlevel%