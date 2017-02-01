# BOB_FUZZER

##  Overview

pydbg를 활용하여 구현하였습니다.
퍼저의 내용은 fuzzer 디렉토리에서 확인하실 수 있습니다.
환경설정은 config.JSON 파일로 설정하실 수 있으며, 그곳에서 offset 값을 지정할 수 있습니다.

mutation의 경우, 블록 단위로 입력 파일 stream을 나누고, 이를 기준으로 변형을 가했습니다.
이렇게 블록 단위로 stream을 나누어 놓음으로서 mutation할 부분을 보다 빨리 결정하고, crash가 발생했을 경우, 보다 빠르게 minimize할 수 있도록 하였습니다.


## Requirement

Windows 32bit 기준으로 작성되었으며, pydbg python 라이브러리가 설치되어 있어야 합니다.


## Execute
실행은 cmd 상에서 cd 명령어를 통해 main.py가 존재하는 디렉토리로 이동한 뒤, main.py를 실행시키면 fuzzer가 실행됩니다.


## SOURCE

**main.py** 프로그램 실행을 담당합니다.
**fuzzer.py** fuzzer의 기본 뼈대가 되는 소스입니다.
**misc.py** 사소한 함수들이 포함되어 있습니다.
**proc_manager.py** 디버거 관련 소스입니다.
**mutation.py** mutation 관련 소스입니다. minimize 기능 및 offset 기능이 포함되어 있습니다.


## Directory Info

**seeds** seed 파일이 저장되는 위치입니다. config.JSON 파일을 통해 변경할 수 있습니다.
**crashes** 크래시가 발생한 파일이 저장되는 위치입니다. config.JSON 파일을 통해 변경할 수 있습니다. minimize된 파일 또한 함께 존재합니다.
**work** 임시 퍼징 작업 파일이 저장되는 위치입니다. config.JSON 파일을 통해 변경할 수 있습니다.