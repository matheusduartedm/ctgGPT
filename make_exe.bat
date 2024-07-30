@ECHO OFF


call chatbot\Scripts\activate.bat

set PYTHONPATH=%PYTHONPATH%;


@ECHO Building distribution...
@ECHO.
@SET PYTHONOPTIMIZE=1 && pyinstaller main.spec --noconfirm
@IF %ERRORLEVEL% NEQ 0 (
  @ECHO *** Error *** generating binaries.
  GOTO :error
) ELSE (
  @ECHO.
  @ECHO Done.
  GOTO :success
)

:error
call chatbot\Scripts\deactivate.bat

:success

